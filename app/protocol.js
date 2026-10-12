/*
 * Offline mirror of swarm/engine.py.
 *
 * The browser app must be able to produce the personalised protocol with no
 * server and no language model. This file re-implements the deterministic
 * policy so the recommendation logic runs on-device. tests/test_parity.py
 * compares this output against the Python engine to catch drift.
 */
(function (global) {
  "use strict";

  const SNR_LOSS_BANDS = [
    [2.0, "normal_0_2db"],
    [7.0, "mild_3_7db"],
    [15.0, "moderate_8_15db"],
    [Infinity, "severe_gt_15db"]
  ];

  const TV_LADDER = ["news_anchor", "interview", "soap_opera_with_questions", "film_with_music"];
  const MUSIC_DOSE_MIN_PER_SESSION = 15;
  const MUSIC_SESSIONS_PER_WEEK = 2;
  const DEFAULT_MICRO_SESSIONS_PER_DAY = 3;
  const DEFAULT_MINUTES_PER_SESSION = 6;

  const COMPLAINTS = ["tv", "noise", "group", "phone", "quick_speech", "female_voice", "fatigue"];

  function classifySnrLoss(v) {
    for (const [t, name] of SNR_LOSS_BANDS) if (v <= t) return name;
    return SNR_LOSS_BANDS[SNR_LOSS_BANDS.length - 1][1];
  }

  function signalChain(p) {
    const actions = [];
    if (p.hearing_aid_streaming === "none") {
      actions.push({ action: "enable_tv_audio_streaming", detail: "Add a TV adapter or Bluetooth streaming path so TV audio goes directly to the hearing aids instead of through the room.", why: "bypasses room acoustics, noise and distance in one step", refs: ["tv_streaming_2024", "tv_adapter_2010"] });
    } else if (p.hearing_aid_streaming === "unknown") {
      actions.push({ action: "verify_streaming_capability", detail: "Check the hearing-aid model for TV adapter or Bluetooth streaming support; this is the single fastest available win.", why: "capability unknown; verify before planning around it", refs: ["tv_streaming_2024"] });
    }
    if (p.tv_can_configure) {
      actions.push({ action: "configure_tv_streaming_today", detail: "Configure the TV streaming path on day 1 and confirm the aids are on the correct program for streamed audio.", why: "visible improvement on day 1 builds adherence", refs: ["tv_streaming_2024"] });
    }
    if (p.top_complaints.includes("noise") || p.top_complaints.includes("group")) {
      actions.push({ action: "introduce_remote_microphone", detail: "For restaurants, family gatherings and car rides, place a remote microphone on the talker rather than relying on the hearing-aid microphones.", why: "+11 to +19.5 dB SNR, benefit independent of distance", refs: ["remote_mic_2021", "snr_requirement_10db"] });
    }
    actions.push({ action: "audit_room_acoustics", detail: "Reduce competing noise at the source (hard floors, running TV or radio, kitchen appliances) before increasing volume.", why: "SNR is driven by ambient noise, distance and reverberation", refs: ["snr_requirement_10db"] });
    if (p.medications_ototoxic) {
      actions.push({ action: "medication_review", detail: "Ask the prescriber or pharmacist to review current medicines for ototoxic effects. Do not stop any prescribed drug without medical advice.", why: "some drugs affect hearing or balance", refs: ["ototoxic_meds"] });
    }
    return { agent: "A1_signal_chain", objective: "maximise signal-to-noise ratio and device configuration first", actions: actions };
  }

  function dosage(p) {
    let sessions = DEFAULT_MICRO_SESSIONS_PER_DAY;
    let minutes = DEFAULT_MINUTES_PER_SESSION;
    const notes = [];
    if (p.cognitive_impairment) {
      sessions = 2; minutes = 5;
      notes.push("shorter, more frequent sessions; stop at the first sign of fatigue");
    }
    if (p.falls_last_year >= 1) notes.push("sit during training; keep the walk inside and supervised");
    return {
      agent: "A2_dosage",
      objective: "reach the therapeutic window without inducing auditory fatigue",
      micro_sessions_per_day: sessions,
      minutes_per_session: minutes,
      days_per_week: 3,
      expected_plateau_weeks: "5-7.5",
      ending_rule: "always end the session on a correct response",
      escalation_rule: "raise difficulty after 3 consecutive correct responses without hesitation",
      notes: notes,
      refs: ["humes_dosage_2014", "act_gamified_2025"]
    };
  }

  function transfer(p) {
    const ladder = TV_LADDER.slice();
    const tvNote = p.uses_captions
      ? "Captions stay OFF during the training block only; keep them available outside training so leisure TV remains enjoyable."
      : "Introduce captions only if a week of the ladder stalls.";
    return {
      agent: "A3_transfer",
      objective: "move gains from exercises into TV, phone and real conversation",
      tv_ladder: ladder,
      favourite_program: p.favourite_program,
      favourite_time: p.favourite_time,
      tv_note: tvNote,
      music: {
        minutes_per_session: MUSIC_DOSE_MIN_PER_SESSION,
        sessions_per_week: MUSIC_SESSIONS_PER_WEEK,
        detail: "music from the participant's era, singing along where possible",
        refs: ["music_mci_2024", "choir_rct_2025", "zendel_music_2019"]
      },
      active_ingredients: ["adaptive speech-in-noise", "time-compressed speech (0.85x -> 1.0x)", "competing talker", "gap detection (temporal resolution)", "auditory working memory"],
      refs: ["act_gamified_2025", "auditory_training_sin_meta", "kraus_brainfit_2013"]
    };
  }

  function partner(p) {
    let mode, detail;
    if (p.living === "alone") { mode = "self_and_remote"; detail = "train the main remote contact by phone and any regular visitor"; }
    else if (p.living === "care_facility") { mode = "staff_briefing"; detail = "brief the care staff on clear speech and on the hearing-aid routine"; }
    else { mode = "household_partner"; detail = "train the household partner who speaks with him most often"; }
    return {
      agent: "A4_partner",
      objective: "raise intelligibility by changing how others speak, not only how he listens",
      mode: mode,
      detail: detail,
      caregiver_hours_per_day: p.caregiver_hours_per_day,
      rules: ["face him before speaking", "reduce background noise first", "speak slightly slower and slightly louder, not shouted", "never shout: it raises pitch and lowers clarity", "confirm understanding by asking him to repeat the key point"],
      refs: ["clear_speech_partner_2016", "nia_communication_tips"]
    };
  }

  function safety(p) {
    const flags = [];
    if (p.falls_last_year >= 1) flags.push({ flag: "falls", action: "refer for balance and hearing review; consider vestibular assessment" });
    if (p.tinnitus) flags.push({ flag: "tinnitus", action: "mention tinnitus at the next audiology appointment; do not self-treat" });
    if (p.medications_ototoxic) flags.push({ flag: "ototoxic_medication", action: "prescriber or pharmacist medication review before any change" });
    return {
      agent: "A5_safety",
      objective: "never let a rehabilitation plan delay medical care",
      escalation_rules: ["sudden hearing change in one ear -> urgent medical assessment", "ear pain, discharge or sudden dizziness -> medical assessment", "no measurable progress after 4 weeks at >=80% adherence -> new audiometry and device review"],
      flags: flags,
      ceiling: "Cochlear hair-cell loss is permanent. The plan targets central processing, attention, strategy and signal quality, not restoration.",
      refs: ["presbycusis_irreversible", "ototoxic_meds"]
    };
  }

  function planWeeks(p, d) {
    const micro = d.micro_sessions_per_day;
    const minutes = d.minutes_per_session;
    const tv = TV_LADDER;
    return [
      { week: 1, focus: "signal + first win", actions: ["configure TV streaming and confirm the correct hearing-aid program", "baseline QuickSIN-like SNR loss estimate and HHIE-S", "start music sessions and partner clear-speech training"], tv_content: tv[0], refs: ["tv_streaming_2024", "hhie_s_screening", "clear_speech_partner_2016"] },
      { week: 2, focus: "establish the routine", actions: [micro + " micro-sessions/day of " + minutes + " min, 3 days/week", "speech-in-noise at the easiest SNR", "end every session on a correct response"], tv_content: tv[0], refs: ["humes_dosage_2014"] },
      { week: 3, focus: "add difficulty", actions: ["speech compression 0.90x", "introduce the competing-talker task", "first mid-point check of the TV ladder"], tv_content: tv[1], refs: ["act_gamified_2025"] },
      { week: 4, focus: "first re-test", actions: ["repeat QuickSIN-like estimate and HHIE-S", "review adherence; if <80%, simplify rather than intensify"], tv_content: tv[1], refs: ["hhie_s_screening", "zheng_rehab_meta_2024"] },
      { week: 5, focus: "temporal resolution", actions: ["gap detection and time-compressed speech at 0.95x", "remote microphone in one real noisy setting"], tv_content: tv[2], refs: ["remote_mic_2021"] },
      { week: 6, focus: "real-world transfer", actions: ["TV content with questions after each block", "phone practice with a familiar speaker"], tv_content: tv[2], refs: ["clear_speech_partner_2016"] },
      { week: 7, focus: "consolidation", actions: ["full-speed speech (1.0x)", "group conversation with the remote microphone"], tv_content: tv[3], refs: ["remote_mic_2021", "choir_rct_2025"] },
      { week: 8, focus: "final re-test and maintenance", actions: ["repeat QuickSIN-like estimate and HHIE-S", "set the long-term routine: music + 20 min/day of listening practice", "book a full audiometry review"], tv_content: tv[3], refs: ["hhie_s_screening", "humes_dosage_2014", "music_mci_2024"] }
    ];
  }

  function progressMarkers() {
    return [
      { when: "day 1", marker: "TV volume lower and fewer requests to repeat" },
      { when: "weeks 2-3", marker: "tolerates background noise without irritation" },
      { when: "weeks 4-6", marker: "follows a soap opera without captions" },
      { when: "week 8", marker: "SNR loss reduced by >=2-3 dB on re-test" }
    ];
  }

  function buildProtocol(p) {
    const d = dosage(p);
    const agents = [signalChain(p), d, transfer(p), partner(p), safety(p)];
    const refs = new Set();
    agents.forEach(a => (a.refs || []).forEach(r => refs.add(r)));
    const plan = planWeeks(p, d);
    plan.forEach(w => (w.refs || []).forEach(r => refs.add(r)));
    return {
      profile_summary: {
        hearing_aid: p.hearing_aid,
        streaming: p.hearing_aid_streaming,
        living: p.living,
        complaints: p.top_complaints,
        favourite_program: p.favourite_program,
        favourite_time: p.favourite_time
      },
      agents: agents,
      plan: plan,
      progress_markers: progressMarkers(),
      references: Array.from(refs).sort()
    };
  }

  const api = { buildProtocol: buildProtocol, classifySnrLoss: classifySnrLoss, COMPLAINTS: COMPLAINTS };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  global.SwarmEngine = api;
})(typeof window !== "undefined" ? window : this);
