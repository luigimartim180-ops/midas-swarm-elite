"""Deterministic personalization engine for the hearing-rehabilitation swarm.

Design rule: the planner is a pure function of the validated profile. It never
calls a language model and never writes free text that is not tied to an
evidence key. Language models may only *narrate* the JSON this module returns,
which is what keeps the system from inventing clinical claims.

Agents (each is a deterministic policy with explicit triggers):
    A1 SignalChainAgent   - fastest wins: signal engineering and device audit
    A2 DosageAgent        - adaptive training dose, fatigue control
    A3 TransferAgent      - ecological transfer: TV ladder, music, conversation
    A4 PartnerAgent       - communication partner (family) training
    A5 SafetyAgent        - red flags, medical escalation, contraindications
"""

from __future__ import annotations

from typing import Any

from .evidence import EVIDENCE
from .schema import Profile

# --- reference constants ---------------------------------------------------

# QuickSIN-like SNR loss bands in dB. Source: quicksin_norms.
SNR_LOSS_BANDS = (
    (2.0, "normal_0_2db"),
    (7.0, "mild_3_7db"),
    (15.0, "moderate_8_15db"),
    (float("inf"), "severe_gt_15db"),
)

# TV ladder: signal first, then progressively harder content.
TV_LADDER = ("news_anchor", "interview", "soap_opera_with_questions", "film_with_music")

# Music dose from music_mci_2024 / choir_rct_2025.
MUSIC_DOSE_MIN_PER_SESSION = 15
MUSIC_SESSIONS_PER_WEEK = 2

# Default training dose from humes_dosage_2014.
DEFAULT_MICRO_SESSIONS_PER_DAY = 3
DEFAULT_MINUTES_PER_SESSION = 6


def _refs(*keys: str) -> list[str]:
    missing = [k for k in keys if k not in EVIDENCE]
    if missing:
        raise KeyError("unknown evidence keys: " + ", ".join(missing))
    return list(keys)


def classify_snr_loss(snr_loss_db: float) -> str:
    """Map an SNR loss value in dB to a band key (quicksin_norms)."""
    for threshold, name in SNR_LOSS_BANDS:
        if snr_loss_db <= threshold:
            return name
    return SNR_LOSS_BANDS[-1][1]  # pragma: no cover - inf covers all


def _signal_chain(profile: Profile) -> dict[str, Any]:
    """A1: signal engineering. Fastest, largest, most reliable effect."""
    actions: list[dict[str, Any]] = []

    if profile.hearing_aid_streaming == "none":
        actions.append(
            {
                "action": "enable_tv_audio_streaming",
                "detail": (
                    "Add a TV adapter or Bluetooth streaming path so TV audio goes "
                    "directly to the hearing aids instead of through the room."
                ),
                "why": "bypasses room acoustics, noise and distance in one step",
                "refs": _refs("tv_streaming_2024", "tv_adapter_2010"),
            }
        )
    elif profile.hearing_aid_streaming == "unknown":
        actions.append(
            {
                "action": "verify_streaming_capability",
                "detail": (
                    "Check the hearing-aid model for TV adapter or Bluetooth "
                    "streaming support; this is the single fastest available win."
                ),
                "why": "capability unknown; verify before planning around it",
                "refs": _refs("tv_streaming_2024"),
            }
        )

    if profile.tv_can_configure:
        actions.append(
            {
                "action": "configure_tv_streaming_today",
                "detail": (
                    "Configure the TV streaming path on day 1 and confirm the aids "
                    "are on the correct program for streamed audio."
                ),
                "why": "visible improvement on day 1 builds adherence",
                "refs": _refs("tv_streaming_2024"),
            }
        )

    if "noise" in profile.top_complaints or "group" in profile.top_complaints:
        actions.append(
            {
                "action": "introduce_remote_microphone",
                "detail": (
                    "For restaurants, family gatherings and car rides, place a "
                    "remote microphone on the talker rather than relying on the "
                    "hearing-aid microphones."
                ),
                "why": "+11 to +19.5 dB SNR, benefit independent of distance",
                "refs": _refs("remote_mic_2021", "snr_requirement_10db"),
            }
        )

    actions.append(
        {
            "action": "audit_room_acoustics",
            "detail": (
                "Reduce competing noise at the source (hard floors, running TV or "
                "radio, kitchen appliances) before increasing volume."
            ),
            "why": "SNR is driven by ambient noise, distance and reverberation",
            "refs": _refs("snr_requirement_10db"),
        }
    )

    if profile.medications_ototoxic:
        actions.append(
            {
                "action": "medication_review",
                "detail": (
                    "Ask the prescriber or pharmacist to review current medicines "
                    "for ototoxic effects. Do not stop any prescribed drug without "
                    "medical advice."
                ),
                "why": "some drugs affect hearing or balance",
                "refs": _refs("ototoxic_meds"),
            }
        )

    return {
        "agent": "A1_signal_chain",
        "objective": "maximise signal-to-noise ratio and device configuration first",
        "actions": actions,
    }


def _dosage(profile: Profile) -> dict[str, Any]:
    """A2: training dose. 2-3 sessions/week, most gain by 5-7.5 weeks."""
    sessions = DEFAULT_MICRO_SESSIONS_PER_DAY
    minutes = DEFAULT_MINUTES_PER_SESSION
    notes: list[str] = []

    if profile.cognitive_impairment:
        sessions = 2
        minutes = 5
        notes.append("shorter, more frequent sessions; stop at the first sign of fatigue")

    if profile.falls_last_year >= 1:
        notes.append("sit during training; keep the walk inside and supervised")

    return {
        "agent": "A2_dosage",
        "objective": "reach the therapeutic window without inducing auditory fatigue",
        "micro_sessions_per_day": sessions,
        "minutes_per_session": minutes,
        "days_per_week": 3,
        "expected_plateau_weeks": "5-7.5",
        "ending_rule": "always end the session on a correct response",
        "escalation_rule": "raise difficulty after 3 consecutive correct responses without hesitation",
        "notes": notes,
        "refs": _refs("humes_dosage_2014", "act_gamified_2025"),
    }


def _transfer(profile: Profile) -> dict[str, Any]:
    """A3: ecological transfer. TV ladder + music + conversation practice."""
    ladder = list(TV_LADDER)
    if profile.uses_captions:
        ladder_note = (
            "Captions stay OFF during the training block only; keep them available "
            "outside training so leisure TV remains enjoyable."
        )
    else:
        ladder_note = "Introduce captions only if a week of the ladder stalls."

    return {
        "agent": "A3_transfer",
        "objective": "move gains from exercises into TV, phone and real conversation",
        "tv_ladder": ladder,
        "favourite_program": profile.favourite_program,
        "favourite_time": profile.favourite_time,
        "tv_note": ladder_note,
        "music": {
            "minutes_per_session": MUSIC_DOSE_MIN_PER_SESSION,
            "sessions_per_week": MUSIC_SESSIONS_PER_WEEK,
            "detail": "music from the participant's era, singing along where possible",
            "refs": _refs("music_mci_2024", "choir_rct_2025", "zendel_music_2019"),
        },
        "active_ingredients": [
            "adaptive speech-in-noise",
            "time-compressed speech (0.85x -> 1.0x)",
            "competing talker",
            "gap detection (temporal resolution)",
            "auditory working memory",
        ],
        "refs": _refs("act_gamified_2025", "auditory_training_sin_meta", "kraus_brainfit_2013"),
    }


def _partner(profile: Profile) -> dict[str, Any]:
    """A4: communication partner training. The family is treatment equipment."""
    if profile.living == "alone":
        mode = "self_and_remote"
        detail = "train the main remote contact by phone and any regular visitor"
    elif profile.living == "care_facility":
        mode = "staff_briefing"
        detail = "brief the care staff on clear speech and on the hearing-aid routine"
    else:
        mode = "household_partner"
        detail = "train the household partner who speaks with him most often"

    return {
        "agent": "A4_partner",
        "objective": "raise intelligibility by changing how others speak, not only how he listens",
        "mode": mode,
        "detail": detail,
        "caregiver_hours_per_day": profile.caregiver_hours_per_day,
        "rules": [
            "face him before speaking",
            "reduce background noise first",
            "speak slightly slower and slightly louder, not shouted",
            "never shout: it raises pitch and lowers clarity",
            "confirm understanding by asking him to repeat the key point",
        ],
        "refs": _refs("clear_speech_partner_2016", "nia_communication_tips"),
    }


def _safety(profile: Profile) -> dict[str, Any]:
    """A5: safety and medical escalation."""
    flags: list[dict[str, str]] = []
    if profile.falls_last_year >= 1:
        flags.append(
            {
                "flag": "falls",
                "action": "refer for balance and hearing review; consider vestibular assessment",
            }
        )
    if profile.tinnitus:
        flags.append(
            {
                "flag": "tinnitus",
                "action": "mention tinnitus at the next audiology appointment; do not self-treat",
            }
        )
    if profile.medications_ototoxic:
        flags.append(
            {
                "flag": "ototoxic_medication",
                "action": "prescriber or pharmacist medication review before any change",
            }
        )

    return {
        "agent": "A5_safety",
        "objective": "never let a rehabilitation plan delay medical care",
        "escalation_rules": [
            "sudden hearing change in one ear -> urgent medical assessment",
            "ear pain, discharge or sudden dizziness -> medical assessment",
            "no measurable progress after 4 weeks at >=80% adherence -> new audiometry and device review",
        ],
        "flags": flags,
        "ceiling": (
            "Cochlear hair-cell loss is permanent. The plan targets central "
            "processing, attention, strategy and signal quality, not restoration."
        ),
        "refs": _refs("presbycusis_irreversible", "ototoxic_meds"),
    }


def _plan_weeks(profile: Profile, dosage: dict[str, Any]) -> list[dict[str, Any]]:
    """Eight-week schedule derived from the dosage and transfer policies."""
    micro = dosage["micro_sessions_per_day"]
    minutes = dosage["minutes_per_session"]
    tv = TV_LADDER
    return [
        {
            "week": 1,
            "focus": "signal + first win",
            "actions": [
                "configure TV streaming and confirm the correct hearing-aid program",
                "baseline QuickSIN-like SNR loss estimate and HHIE-S",
                "start music sessions and partner clear-speech training",
            ],
            "tv_content": tv[0],
            "refs": _refs("tv_streaming_2024", "hhie_s_screening", "clear_speech_partner_2016"),
        },
        {
            "week": 2,
            "focus": "establish the routine",
            "actions": [
                f"{micro} micro-sessions/day of {minutes} min, 3 days/week",
                "speech-in-noise at the easiest SNR",
                "end every session on a correct response",
            ],
            "tv_content": tv[0],
            "refs": _refs("humes_dosage_2014"),
        },
        {
            "week": 3,
            "focus": "add difficulty",
            "actions": [
                "speech compression 0.90x",
                "introduce the competing-talker task",
                "first mid-point check of the TV ladder",
            ],
            "tv_content": tv[1],
            "refs": _refs("act_gamified_2025"),
        },
        {
            "week": 4,
            "focus": "first re-test",
            "actions": [
                "repeat QuickSIN-like estimate and HHIE-S",
                "review adherence; if <80%, simplify rather than intensify",
            ],
            "tv_content": tv[1],
            "refs": _refs("hhie_s_screening", "zheng_rehab_meta_2024"),
        },
        {
            "week": 5,
            "focus": "temporal resolution",
            "actions": [
                "gap detection and time-compressed speech at 0.95x",
                "remote microphone in one real noisy setting",
            ],
            "tv_content": tv[2],
            "refs": _refs("remote_mic_2021"),
        },
        {
            "week": 6,
            "focus": "real-world transfer",
            "actions": [
                "TV content with questions after each block",
                "phone practice with a familiar speaker",
            ],
            "tv_content": tv[2],
            "refs": _refs("clear_speech_partner_2016"),
        },
        {
            "week": 7,
            "focus": "consolidation",
            "actions": [
                "full-speed speech (1.0x)",
                "group conversation with the remote microphone",
            ],
            "tv_content": tv[3],
            "refs": _refs("remote_mic_2021", "choir_rct_2025"),
        },
        {
            "week": 8,
            "focus": "final re-test and maintenance",
            "actions": [
                "repeat QuickSIN-like estimate and HHIE-S",
                "set the long-term routine: music + 20 min/day of listening practice",
                "book a full audiometry review",
            ],
            "tv_content": tv[3],
            "refs": _refs("hhie_s_screening", "humes_dosage_2014", "music_mci_2024"),
        },
    ]


def _progress_markers() -> list[dict[str, str]]:
    return [
        {"when": "day 1", "marker": "TV volume lower and fewer requests to repeat"},
        {"when": "weeks 2-3", "marker": "tolerates background noise without irritation"},
        {"when": "weeks 4-6", "marker": "follows a soap opera without captions"},
        {"when": "week 8", "marker": "SNR loss reduced by >=2-3 dB on re-test"},
    ]


def build_protocol(profile: Profile) -> dict[str, Any]:
    """Build the full, auditable protocol for a validated profile."""
    dosage = _dosage(profile)
    agents = [
        _signal_chain(profile),
        dosage,
        _transfer(profile),
        _partner(profile),
        _safety(profile),
    ]

    references = sorted({key for agent in agents for key in agent.get("refs", [])})
    for week in _plan_weeks(profile, dosage):
        references.extend(week.get("refs", []))
    references = sorted(set(references))

    return {
        "profile_summary": {
            "hearing_aid": profile.hearing_aid,
            "streaming": profile.hearing_aid_streaming,
            "living": profile.living,
            "complaints": profile.top_complaints,
            "favourite_program": profile.favourite_program,
            "favourite_time": profile.favourite_time,
        },
        "agents": agents,
        "plan": _plan_weeks(profile, dosage),
        "progress_markers": _progress_markers(),
        "references": references,
        "evidence": {key: EVIDENCE[key] for key in references},
    }


def calibration_questions() -> list[dict[str, Any]]:
    """The questions the profile needs before the plan can be personalised."""
    return [
        {"id": "hearing_aid", "question": "Marca e modelo dos aparelhos auditivos?", "type": "text"},
        {"id": "hearing_aid_streaming", "question": "Os aparelhos ja transmitem audio da TV (Bluetooth, adaptador ou microfone remoto)?", "type": "choice", "options": ["none", "bluetooth", "tv_adapter", "remote_mic", "unknown"]},
        {"id": "tv_setup", "question": "Como e a TV da casa?", "type": "choice", "options": ["smart_tv", "cable_box", "old_tv", "streaming_stick", "unknown"]},
        {"id": "tv_can_configure", "question": "Alguem consegue configurar a TV hoje?", "type": "bool"},
        {"id": "favourite_program", "question": "Qual o programa favorito dele?", "type": "text"},
        {"id": "favourite_time", "question": "Em que horario ele costuma assistir?", "type": "text"},
        {"id": "living", "question": "Ele mora sozinho, com a familia ou em instituicao?", "type": "choice", "options": ["alone", "with_family", "care_facility"]},
        {"id": "caregiver_hours_per_day", "question": "Quantas horas por dia ha um cuidador por perto?", "type": "number"},
        {"id": "top_complaints", "question": "Quais as principais queixas, em ordem?", "type": "multi", "options": ["tv", "noise", "group", "phone", "quick_speech", "female_voice", "fatigue"]},
        {"id": "medications_ototoxic", "question": "Ele usa medicamentos que podem afetar a audicao ou o equilibrio?", "type": "bool"},
        {"id": "walk_minutes_per_day", "question": "Quantos minutos ele caminha por dia, em media?", "type": "number"},
        {"id": "uses_captions", "question": "Ele costuma usar legenda na TV?", "type": "bool"},
        {"id": "tinnitus", "question": "Ele tem zumbido?", "type": "bool"},
        {"id": "falls_last_year", "question": "Quantas quedas no ultimo ano?", "type": "number"},
        {"id": "cognitive_impairment", "question": "Existe diagnostico de declinio cognitivo?", "type": "bool"},
    ]
