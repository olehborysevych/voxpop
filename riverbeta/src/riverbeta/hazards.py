"""Find mentions of river hazards/landmarks in a transcript.

Pure keyword/regex matching over the transcript text (English, Ukrainian,
Russian) - no network calls, no LLM required. Each match becomes a
timestamped "comment" with a hazard type, optional river side, and a rough
severity hint.
"""

import re

# hazard_type -> list of regex patterns (case-insensitive, unicode)
HAZARD_KEYWORDS: dict[str, list[str]] = {
    "weir": [
        r"\bweirs?\b",
        r"гребл[яюіиі]",      # uk: гребля
        r"загат[аи]",         # uk/ru: загата
        r"плотин[аы]",        # ru: плотина
        r"запруд[аи]",
    ],
    "rapid": [
        r"\brapids?\b",
        r"пор[іо]г[іиа]?",    # uk/ru: поріг / порог
        r"бистрин[аи]",
        r"перекат[аи]?",
    ],
    "strainer": [
        r"\bstrainers?\b",
        r"\blog\s*jam\b",
        r"завал[иі]?",        # downed trees / log jam
        r"корч[іі]",
    ],
    "portage": [
        r"\bportages?\b",
        r"обнос",
        r"волок",
    ],
    "eddy": [
        r"\beddy\b|\beddies\b",
        r"завор[оі]т",
        r"улогов",
    ],
    "sieve": [
        r"\bsieves?\b",
        r"сито",
    ],
    "undercut": [
        r"\bundercuts?\b",
        r"підмив",
        r"подмыв",
    ],
    "hole": [
        r"\bhole\b|\bholes\b",
        r"\bbig water\b",
        r"\bям[аи]\b",
    ],
}

SIDE_KEYWORDS: dict[str, list[str]] = {
    "left": [r"\bleft\b", r"л[іи]в", r"слева", r"налево"],
    "right": [r"\bright\b", r"прав", r"справа", r"направо"],
}

SEVERITY_KEYWORDS: dict[str, list[str]] = {
    "high": [
        r"danger", r"careful", r"caution",
        r"небезпечн", r"обережн", r"уваг",
        r"опасн", r"осторожн", r"внимани",
    ],
}

_COMPILED_HAZARDS = {
    hazard_type: [re.compile(p, re.IGNORECASE | re.UNICODE) for p in patterns]
    for hazard_type, patterns in HAZARD_KEYWORDS.items()
}
_COMPILED_SIDES = {
    side: [re.compile(p, re.IGNORECASE | re.UNICODE) for p in patterns]
    for side, patterns in SIDE_KEYWORDS.items()
}
_COMPILED_SEVERITY = {
    level: [re.compile(p, re.IGNORECASE | re.UNICODE) for p in patterns]
    for level, patterns in SEVERITY_KEYWORDS.items()
}


def _first_match(text: str, compiled: dict[str, list[re.Pattern]]) -> str | None:
    for key, patterns in compiled.items():
        if any(p.search(text) for p in patterns):
            return key
    return None


def extract_hazards(segments: list[dict]) -> list[dict]:
    """Scan transcript segments and return one entry per hazard mention.

    ``segments`` is a list of ``{"start": float, "end": float, "text": str}``
    such as the ``original`` list from :mod:`riverbeta.transcribe`.
    """
    hazards = []
    for seg in segments:
        text = seg["text"]
        for hazard_type, patterns in _COMPILED_HAZARDS.items():
            if any(p.search(text) for p in patterns):
                hazards.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "hazard_type": hazard_type,
                    "side": _first_match(text, _COMPILED_SIDES),
                    "severity": _first_match(text, _COMPILED_SEVERITY) or "normal",
                    "text": text,
                })
    return hazards
