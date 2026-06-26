"""Incident validation helpers."""

import re

SAFE_MITRE_TACTICS = frozenset(
    {
        "reconnaissance",
        "resource-development",
        "initial-access",
        "execution",
        "persistence",
        "privilege-escalation",
        "defense-evasion",
        "credential-access",
        "discovery",
        "lateral-movement",
        "collection",
        "command-and-control",
        "exfiltration",
        "impact",
    }
)

MITRE_TECHNIQUE_PATTERN = re.compile(r"^T\d{4}(?:\.\d{3})?$")


def normalize_tags(tags: list[str] | None) -> list[str]:
    """Normalize tags while preserving user-provided safe labels."""
    if tags is None:
        return []
    normalized: list[str] = []
    for tag in tags:
        stripped = tag.strip().lower()
        if stripped and stripped not in normalized:
            normalized.append(stripped)
    return normalized


def validate_mitre_tactic(tactic: str | None) -> str | None:
    """Validate a MITRE tactic against a static local allowlist."""
    if tactic is None:
        return None
    normalized = tactic.strip().lower()
    if normalized not in SAFE_MITRE_TACTICS:
        msg = "Invalid MITRE tactic."
        raise ValueError(msg)
    return normalized


def validate_mitre_technique(technique: str | None) -> str | None:
    """Validate a MITRE technique identifier shape without external calls."""
    if technique is None:
        return None
    normalized = technique.strip().upper()
    if not MITRE_TECHNIQUE_PATTERN.fullmatch(normalized):
        msg = "Invalid MITRE technique."
        raise ValueError(msg)
    return normalized
