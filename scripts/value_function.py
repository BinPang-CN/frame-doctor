#!/usr/bin/env python3
"""Human value function helpers for LDS candidate ranking."""

DEFAULT_PROFILE = {
    "readability": 0.8,
    "visual_impact": 0.5,
    "density": 0.5,
    "grid_strictness": 0.6,
    "editability": 0.7,
    "content_preservation": 0.8,
    "semantic_fidelity": 0.8,
    "only_fix_hard_errors": 0.0,
}


PATTERN_TRAITS = {
    "two_column": {
        "readability": 0.95,
        "visual_impact": 0.55,
        "density": 0.45,
        "grid_strictness": 0.8,
        "editability": 0.75,
        "content_preservation": 0.75,
        "semantic_fidelity": 0.85,
        "minimal_fix": 0.35,
    },
    "hero_plus_support": {
        "readability": 0.68,
        "visual_impact": 0.95,
        "density": 0.35,
        "grid_strictness": 0.55,
        "editability": 0.55,
        "content_preservation": 0.62,
        "semantic_fidelity": 0.65,
        "minimal_fix": 0.3,
    },
    "card_grid": {
        "readability": 0.75,
        "visual_impact": 0.55,
        "density": 0.82,
        "grid_strictness": 0.92,
        "editability": 0.88,
        "content_preservation": 0.7,
        "semantic_fidelity": 0.75,
        "minimal_fix": 0.42,
    },
    "dashboard": {
        "readability": 0.72,
        "visual_impact": 0.5,
        "density": 0.88,
        "grid_strictness": 0.86,
        "editability": 0.8,
        "content_preservation": 0.7,
        "semantic_fidelity": 0.82,
        "minimal_fix": 0.35,
    },
    "operational_dashboard": {
        "readability": 0.78,
        "visual_impact": 0.45,
        "density": 0.9,
        "grid_strictness": 0.9,
        "editability": 0.86,
        "content_preservation": 0.72,
        "semantic_fidelity": 0.9,
        "minimal_fix": 0.32,
    },
    "mobile_screen": {
        "readability": 0.82,
        "visual_impact": 0.55,
        "density": 0.62,
        "grid_strictness": 0.82,
        "editability": 0.82,
        "content_preservation": 0.74,
        "semantic_fidelity": 0.86,
        "minimal_fix": 0.38,
    },
    "comparison": {
        "readability": 0.78,
        "visual_impact": 0.5,
        "density": 0.65,
        "grid_strictness": 0.78,
        "editability": 0.72,
        "content_preservation": 0.72,
        "semantic_fidelity": 0.75,
        "minimal_fix": 0.4,
    },
    "process_pipeline": {
        "readability": 0.86,
        "visual_impact": 0.5,
        "density": 0.66,
        "grid_strictness": 0.84,
        "editability": 0.84,
        "content_preservation": 0.82,
        "semantic_fidelity": 0.95,
        "minimal_fix": 0.35,
    },
    "layered_system_graph": {
        "readability": 0.88,
        "visual_impact": 0.48,
        "density": 0.68,
        "grid_strictness": 0.88,
        "editability": 0.84,
        "content_preservation": 0.82,
        "semantic_fidelity": 0.94,
        "minimal_fix": 0.34,
    },
}


def normalize_profile(profile):
    normalized = dict(DEFAULT_PROFILE)
    if profile:
        normalized.update(profile)
    for key, value in list(normalized.items()):
        try:
            normalized[key] = min(1.0, max(0.0, float(value)))
        except (TypeError, ValueError):
            normalized[key] = DEFAULT_PROFILE.get(key, 0.5)
    return normalized


def _pattern_traits(pattern):
    if pattern.startswith("mobile_"):
        return PATTERN_TRAITS["mobile_screen"]
    return PATTERN_TRAITS.get(pattern, PATTERN_TRAITS["hero_plus_support"])


def score_candidate(candidate, profile, canvas):
    normalized = normalize_profile(profile)
    pattern = candidate.get("pattern", "hero_plus_support")
    traits = _pattern_traits(pattern)
    confidence = float(candidate.get("confidence", 0.5))

    value_keys = [
        "readability",
        "visual_impact",
        "density",
        "grid_strictness",
        "editability",
        "content_preservation",
        "semantic_fidelity",
    ]
    weighted = 0.0
    weight_total = 0.0
    for key in value_keys:
        preference = normalized.get(key, DEFAULT_PROFILE[key])
        weighted += preference * traits.get(key, 0.5)
        weight_total += max(preference, 0.05)
    value_score = weighted / weight_total if weight_total else 0.5

    only_hard = normalized.get("only_fix_hard_errors", 0.0)
    minimal_score = traits.get("minimal_fix", 0.4)
    final_score = confidence * 0.45 + value_score * 0.45 + only_hard * minimal_score * 0.1
    if only_hard >= 0.75 and pattern not in ("minimal_fix",):
        final_score -= 0.18 * (1.0 - minimal_score)
    if normalized.get("density", 0) >= 0.75 and pattern in ("dashboard", "card_grid", "operational_dashboard"):
        final_score += 0.08
    if normalized.get("readability", 0) >= 0.85 and pattern == "two_column":
        final_score += 0.08
    if normalized.get("visual_impact", 0) >= 0.8 and pattern == "hero_plus_support":
        final_score += 0.1

    scored = dict(candidate)
    scored["value_score"] = round(value_score, 4)
    scored["rank_score"] = round(max(0.0, min(1.0, final_score)), 4)
    scored["value_reasons"] = _candidate_reasons(pattern, normalized)
    return scored


def _candidate_reasons(pattern, profile):
    reasons = []
    if profile.get("readability", 0) >= 0.8 and pattern in ("two_column", "process_pipeline", "layered_system_graph"):
        reasons.append("supports high readability with stable reading regions")
    if profile.get("visual_impact", 0) >= 0.75 and pattern == "hero_plus_support":
        reasons.append("supports high visual impact with a dominant lead region")
    if profile.get("density", 0) >= 0.7 and pattern in ("dashboard", "card_grid", "operational_dashboard"):
        reasons.append("supports density through repeated modules and compact grids")
    if profile.get("grid_strictness", 0) >= 0.75 and pattern in ("card_grid", "dashboard", "operational_dashboard", "two_column"):
        reasons.append("supports strict grid alignment and gutter normalization")
    if profile.get("semantic_fidelity", 0) >= 0.8 and pattern in ("process_pipeline", "layered_system_graph"):
        reasons.append("preserves semantic regions and connector meaning")
    if profile.get("only_fix_hard_errors", 0) >= 0.75:
        reasons.append("profile requests local hard-error repair over broad restructuring")
    return reasons or ["balanced candidate for the provided value profile"]


def rank_candidates(candidates, profile, canvas):
    scored = [score_candidate(candidate, profile, canvas) for candidate in candidates]
    return sorted(scored, key=lambda item: item.get("rank_score", 0), reverse=True)


def choose_grid_strategy(profile, canvas):
    normalized = normalize_profile(profile)
    frame = canvas.get("frame", {})
    width = float(frame.get("width", 0))
    density = normalized.get("density", 0)
    strictness = normalized.get("grid_strictness", 0)
    if strictness >= 0.85 and density >= 0.75:
        family = "32_field_modular"
        grid_size = 8
    elif density >= 0.7:
        family = "20_field_modular"
        grid_size = 8
    elif strictness >= 0.75:
        family = "8_field_grid"
        grid_size = 8
    else:
        family = "simple_column_grid"
        grid_size = 8 if width <= 800 else 12
    return {
        "family": family,
        "grid_size": grid_size,
        "strictness": round(strictness, 2),
        "density": round(density, 2),
    }


def build_decision_log(candidates, ranked_candidates, profile):
    normalized = normalize_profile(profile)
    log = [
        {
            "step": "profile_normalization",
            "message": "Human value profile normalized with LDS L2 keys.",
            "profile": normalized,
        }
    ]
    if ranked_candidates:
        winner = ranked_candidates[0]
        log.append(
            {
                "step": "candidate_ranking",
                "message": (
                    f"{winner['pattern']} ranked highest with score {winner['rank_score']} "
                    f"from confidence {winner.get('confidence', 0)} and value fit {winner.get('value_score', 0)}."
                ),
                "reasons": winner.get("value_reasons", []),
            }
        )
    if normalized.get("only_fix_hard_errors", 0) >= 0.75:
        log.append(
            {
                "step": "repair_scope",
                "message": "Minimal-fix mode is active; broad restacking should be avoided unless needed for critical conflicts.",
            }
        )
    log.append(
        {
            "step": "candidate_count",
            "message": f"{len(candidates)} structure candidates considered before ranking.",
        }
    )
    return log


def build_value_tradeoffs(profile, pattern):
    normalized = normalize_profile(profile)
    optimized = [
        key
        for key in (
            "readability",
            "visual_impact",
            "density",
            "grid_strictness",
            "editability",
            "content_preservation",
            "semantic_fidelity",
        )
        if normalized.get(key, 0) >= 0.75
    ]
    costs = []
    if "density" not in optimized and pattern in ("two_column", "hero_plus_support"):
        costs.append("lower density")
    if "visual_impact" not in optimized and pattern in ("dashboard", "card_grid", "operational_dashboard"):
        costs.append("less hero visual dominance")
    if normalized.get("only_fix_hard_errors", 0) >= 0.75:
        costs.append("less global restructuring")
    return {
        "optimized_for": optimized or ["balanced repair"],
        "accepted_costs": costs or ["none beyond normal layout tradeoffs"],
        "human_confirmation_required": False,
    }
