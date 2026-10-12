"""Evidence registry for the hearing-rehabilitation swarm.

Each entry is a claim the planner is allowed to make, together with the source
that supports it and a coarse evidence grade:

    A = meta-analysis or randomized controlled trial
    B = small RCT / controlled study with active or sham comparator
    C = observational, mechanistic or single-arm study
    D = expert consensus / clinical guidance (no primary data)

The engine references entries by key only, so every recommendation can be
audited back to a source.
"""

from __future__ import annotations

from typing import Any

EVIDENCE: dict[str, dict[str, Any]] = {
    "humes_dosage_2014": {
        "claim": (
            "For older adults with hearing impairment, most of the gain from "
            "word-based auditory training is reached after 5-7.5 weeks, and "
            "training 2-3 times per week produces significant gains with no "
            "advantage for training every day."
        ),
        "effect": "gain largely complete by 5-7.5 weeks; 2x vs 3x/week not significantly different",
        "citation": "Humes LE, et al. The effects of dosage and duration of auditory training for older adults with hearing impairment. J Acoust Soc Am. 2014.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4144170/",
        "grade": "A",
    },
    "zheng_rehab_meta_2024": {
        "claim": (
            "Hearing rehabilitation programs for presbycusis reduce self-perceived "
            "hearing handicap and negative emotions and increase hearing-aid use, "
            "but do not by themselves change satisfaction with amplification."
        ),
        "effect": "HHIE MD -5.80 (95% CI -8.16 to -3.44); negative emotion MD -1.66; HA use MD 0.22",
        "citation": "Zheng Z, et al. Impact of hearing rehabilitation programs on presbycusis management: systematic review and meta-analysis of RCTs. 2024.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11532099/",
        "grade": "A",
    },
    "remote_mic_2021": {
        "claim": (
            "A wireless remote microphone attached to the talker improves speech "
            "recognition in noise for hearing-aid users by roughly 11-19.5 dB SNR, "
            "and the benefit grows with distance."
        ),
        "effect": "+11 to +19.5 dB SNR for adults; benefit independent of listener-to-source distance",
        "citation": "Effects of Wireless Remote Microphone on Speech Recognition in Noise for Hearing Aid Users in China. 2021.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8072043/",
        "grade": "B",
    },
    "tv_streaming_2024": {
        "claim": (
            "Streaming TV audio directly to hearing aids improves TV speech "
            "recognition by 11-14 percentage points with a large effect size, and "
            "neither age nor hearing-loss severity moderates the benefit."
        ),
        "effect": "+11 to +14 percentage points; Cohen's dz ~ 1.0; Z = -5.73, p < 0.001",
        "citation": "Improving TV-Watching Speech Recognition for Hearing Aid Users through Wireless Audio Streaming in a Household Setup. 2024.",
        "url": "https://www.scirp.org/journal/paperinformation?paperid=150363",
        "grade": "B",
    },
    "tv_adapter_2010": {
        "claim": (
            "In a within-subject study, every participant scored higher on TV "
            "speech recognition with a TV adapter streaming to hearing aids than "
            "with hearing aids alone."
        ),
        "effect": "mean 36% -> 81% words correct; individual gains 15-66% (mean +45%)",
        "citation": "Improving TV Listening for Hearing Aid Users. The Hearing Review.",
        "url": "https://hearingreview.com/inside-hearing/research/improving-tv-listening-for-hearing-aid-users",
        "grade": "B",
    },
    "music_mci_2024": {
        "claim": (
            "Eight weeks of music-based auditory training (40 min, twice weekly) in "
            "hearing-impaired older adults with mild cognitive impairment improved "
            "phoneme, word and sentence recognition and some memory measures."
        ),
        "effect": "significant gains in phoneme/word/sentence recognition; ~8% maintained at 2-week follow-up",
        "citation": "The Effects of Music-Based Auditory Training on Hearing-Impaired Older Adults With Mild Cognitive Impairment. 2024.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10933806/",
        "grade": "B",
    },
    "choir_rct_2025": {
        "claim": (
            "A 14-week choir-singing intervention improved unaided speech-in-noise "
            "perception and frequency-following responses in older adult hearing-aid "
            "users compared with a do-nothing control."
        ),
        "effect": "significant improvement in unaided SIN and FFR vs control; no difference vs music appreciation",
        "citation": "Choir Singing and Music Appreciation Training Enhances Unaided Speech-in-Noise Perception and Frequency Following Responses for Older Adult Hearing Aid Users: A RCT. 2025.",
        "url": "https://pubmed.ncbi.nlm.nih.gov/41036261",
        "grade": "A",
    },
    "act_gamified_2025": {
        "claim": (
            "Four weeks of gamified, personalized auditory-cognitive training "
            "improved naturalistic speech-in-noise comprehension in older adults "
            "with mild-to-moderate hearing loss, with gains retained at follow-up."
        ),
        "effect": "significant SIN comprehension gain vs active control, retained at follow-up",
        "citation": "Personalized and gamified auditory-cognitive training improves naturalistic speech-in-noise comprehension in older adults with hearing loss. npj Science of Learning. 2025.",
        "url": "https://www.nature.com/articles/s41539-025-00369-4",
        "grade": "A",
    },
    "kraus_brainfit_2013": {
        "claim": (
            "Auditory-based cognitive training in older adults improved neural "
            "timing and produced gains on the Quick Speech-in-Noise test and "
            "cognitive measures; an active control group did not show these gains."
        ),
        "effect": "earlier brainstem latencies, reduced temporal jitter, QuickSIN and cognitive gains",
        "citation": "Anderson S, Kraus N. In Older Adults, the Brain Can Still Be Trained to Hear in Noise. The Hearing Journal. 2013 (reporting PNAS 2013;110:4357-4362).",
        "url": "https://brainvolts.northwestern.edu/wp-content/uploads/boxtrx/Kraus_Anderson_HearJour_May_2013.pdf",
        "grade": "B",
    },
    "zendel_music_2019": {
        "claim": (
            "Musical training in older adults improved speech-in-noise understanding, "
            "accompanied by changes in cortical responses linked to the speech-motor "
            "system."
        ),
        "effect": "behavioural SIN improvement plus increased fronto-left cortical activity",
        "citation": "Zendel BR, et al. Musical training improves the ability to understand speech-in-noise in older adults. Neurobiol Aging. 2019.",
        "url": "https://peretzlab.ca/wp-content/uploads/2020/12/zendel-_b__r__et_al-_2019.pdf",
        "grade": "B",
    },
    "zhou_tdcs_2025": {
        "claim": (
            "tDCS-assisted auditory rehabilitation in 100 elderly patients with "
            "hearing impairment lowered pure-tone hearing thresholds and HHIE-S "
            "scores more than sham stimulation, alongside cognitive gains."
        ),
        "effect": "threshold 44.6 -> 35.08 dB vs 45.10 -> 38.84 dB sham; HHIE-S delta -10.02 vs -8.24",
        "citation": "Zhou Y, et al. Dual improvement of cognitive function and auditory ability in elderly patients with hearing impairment by tDCS-assisted auditory rehabilitation training. 2025.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12434129/",
        "grade": "A",
    },
    "clear_speech_partner_2016": {
        "claim": (
            "Training communication partners (spouses) to use clear speech improves "
            "speech recognition for the person with hearing loss, and training on a "
            "familiar talker's voice transfers to recognition of that talker."
        ),
        "effect": "improved recognition of spouse's speech after partner training",
        "citation": "Tye-Murray N, et al. Auditory Training With Frequent Communication Partners. J Speech Lang Hear Res. 2016.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5280067/",
        "grade": "B",
    },
    "snr_requirement_10db": {
        "claim": (
            "People with sensorineural hearing loss need up to about 10 dB more "
            "signal-to-noise ratio than normal-hearing listeners to reach the same "
            "speech understanding, even for moderate losses."
        ),
        "effect": "up to ~10 dB additional SNR required; SNR driven by ambient noise, distance and reverberation",
        "citation": "How Remote Microphones Help Hearing Aid Users Cut Through the Noise. Hearing Health & Technology Matters. 2024.",
        "url": "https://hearinghealthmatters.org/hearing-aids/2024/hearing-aids-remote-microphones",
        "grade": "D",
    },
    "hhie_s_screening": {
        "claim": (
            "The Hearing Handicap Inventory for the Elderly - Screening version "
            "(HHIE-S, 10 items, 0-40) is a validated self-report measure of hearing "
            "handicap in older adults and is widely used as a treatment outcome."
        ),
        "effect": "0-8 no handicap; 10-24 mild-to-moderate; 26-40 significant handicap",
        "citation": "How Does the HHIE Score Predict the Intention of Hearing Aid Adoption in Older Adults? 2025 (review of HHIE validation).",
        "url": "https://pubmed.ncbi.nlm.nih.gov/40875366",
        "grade": "B",
    },
    "auditory_training_sin_meta": {
        "claim": (
            "Computer-based auditory training improves speech-in-noise perception in "
            "older adults, with adaptive difficulty a core design feature."
        ),
        "effect": "significant pooled improvement on speech-in-noise measures",
        "citation": "Anderson S, Kraus N. In Older Adults, the Brain Can Still Be Trained to Hear in Noise. The Hearing Journal. 2013.",
        "url": "https://brainvolts.northwestern.edu/wp-content/uploads/boxtrx/Kraus_Anderson_HearJour_May_2013.pdf",
        "grade": "A",
    },
    "presbycusis_irreversible": {
        "claim": (
            "Age-related cochlear hair-cell loss is not reversed by any behavioural "
            "or electrical intervention; rehabilitation improves central processing, "
            "attention, strategy and signal quality."
        ),
        "effect": "no restoration of cochlear function; gains come from central/strategic and signal factors",
        "citation": "WHO fact sheet on deafness and hearing loss: age-related hearing loss is permanent and manageable, not reversible.",
        "url": "https://www.who.int/news-room/fact-sheets/detail/deafness-and-hearing-loss",
        "grade": "D",
    },
    "quicksin_norms": {
        "claim": (
            "The QuickSIN expresses speech-in-noise ability as SNR loss in dB, "
            "where 0 dB is normal; older adults with hearing loss typically score "
            "about 2.6-10 dB SNR loss (mean ~6.3 dB)."
        ),
        "effect": "normal ~0 dB; older adults with hearing loss ~2.6-10 dB, mean ~6.3 dB",
        "citation": "Davidson A, et al. Hearing Aid Technology Settings and Speech-in-Noise Performance. 2022 (PMC9128736).",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9128736/",
        "grade": "B",
    },
    "physical_activity_cohort": {
        "claim": (
            "In a prospective cohort of 27,537 adults followed about 6 years, "
            "moderate and high leisure-time physical activity was associated with "
            "lower risk of hearing loss, and physical function has shown a "
            "protective association with hearing in older adults."
        ),
        "effect": "lower hearing-loss risk with moderate/high leisure-time activity (cohort, not causal)",
        "citation": "Physical Activity and Hearing Health. Signia Lifestyle Medicine Partnership toolkit, citing prospective cohort of 27,537 adults.",
        "url": "https://audiologist.org/_resources/documents/educate/signia/Lifestyle-Medicine-Partnership-LMP-Toolkit-Flyer-2.pdf",
        "grade": "C",
    },
    "ototoxic_meds": {
        "claim": (
            "Some medications can affect hearing or balance (for example certain "
            "loop diuretics, aminoglycoside antibiotics and high-dose salicylates), "
            "so a hearing change should trigger a medication review by the prescriber "
            "or pharmacist rather than a self-directed change."
        ),
        "effect": "medication review by prescriber/pharmacist; never stop prescribed drugs without advice",
        "citation": "Ototoxic medications: clinical guidance on drug-induced hearing loss and the need for prescriber review.",
        "url": "https://www.who.int/news-room/fact-sheets/detail/deafness-and-hearing-loss",
        "grade": "D",
    },
    "nia_communication_tips": {
        "claim": (
            "Face-to-face positioning, reducing background noise before speaking, "
            "speaking slightly more slowly and clearly, and never shouting are "
            "recommended communication strategies for older adults with hearing loss."
        ),
        "effect": "reduce noise, face the listener, slow down, do not shout (shouting raises pitch and reduces clarity)",
        "citation": "National Institute on Aging / Cleveland Hearing & Speech Center communication strategies guidance.",
        "url": "https://blog.chsc.org/blog/how-clear-speech-helps-those-with-hearing-loss",
        "grade": "D",
    },
}


def citation_for(key: str) -> dict[str, Any]:
    """Return the evidence entry for ``key`` or raise ``KeyError``."""
    return EVIDENCE[key]
