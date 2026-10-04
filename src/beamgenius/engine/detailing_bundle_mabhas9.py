"""Mabhas 9 (1399) verified Phase 2F Stage B bundled-bar evaluators.

Verified production rules (visually verified 2026-10-03 from Mabhas 9,
1399 5th ed. source-page captures, re-confirmed 2026-10-05;
Printed pp. 441-442 / PDF pp. 462-463, footers '۴۴۱'/'۴۴۲' visible):

- ``BG-DETAIL-BUNDLE-001``: maximum number of bars per bundle (n <= 4),
  Clause 9-21-5-1
- ``BG-DETAIL-BUNDLE-002``: transverse enclosure of bundles; compressed
  bundles require transverse bar diameter >= 12 mm, Clause 9-21-5-2
- ``BG-DETAIL-BUNDLE-003``: beam bundle bar diameter prohibition
  (db > 34 mm not permitted in beam bundles), Clause 9-21-5-3
- ``BG-DETAIL-BUNDLE-004``: cutoff point staggering of bundle bars in
  flexural members (>= 40*db between each pair), Clause 9-21-5-4
- ``BG-DETAIL-BUNDLE-005``: plane arrangement limit (bundles with more than
  two bars: at most two bars per plane, except at splice locations),
  Clause 9-21-5-5
- ``BG-DETAIL-BUNDLE-006``: bundle equivalent bar diameter
  (d_eq = db*sqrt(n) for n identical bars), Clause 9-21-5-6
- ``BG-DETAIL-BUNDLE-007``: bundle development length multiplier
  (2-bar 1.00 / 3-bar 1.20 / 4-bar 1.33, tension and compression),
  Clause 9-21-5-7
- ``BG-DETAIL-BUNDLE-008``: bundle lap splice rules (per-bar lap =
  single-bar ld with the 9-21-5-7 multiplier; individual laps must not
  overlap; bundle-to-bundle lap prohibited), Clause 9-21-5-8

Deterministic contract of every evaluator (in order):

1. Central Gatekeeper check (``evaluate_rule_gate``) runs FIRST.
2. Missing required engineering inputs return ``UNVERIFIED_RULE_BLOCKED``
   (BLOCKED) with ``MISSING_*`` diagnostics — missing values are never
   assumed or defaulted.
3. Malformed input values (non-finite, non-positive, wrong type) return
   ``INVALID_INPUT``.
4. Unsupported configurations (mixed-diameter bundles under 9-21-5-6)
   return ``UNVERIFIED_RULE_BLOCKED`` (BLOCKED) — BLOCKED never becomes
   PASS.
5. A bundle bar count of 1 (single bar) is ``NOT_APPLICABLE`` in every
   bundle rule; a count above 4 violates Clause 9-21-5-1 (FAIL under
   ``BG-DETAIL-BUNDLE-001``) and is ``NOT_APPLICABLE`` under the satellite
   rules, which defer to ``BG-DETAIL-BUNDLE-001``.
6. The underlying single-bar development length (Clause 9-21-3) and lap
   rules (Clause 9-21-4) are NEVER computed here: rules 007/008 apply only
   the verified bundle multipliers to a caller-provided verified single-bar
   ld, and return BLOCKED when it is missing.
7. Every step attaches the registry ``RuleReference``, a
   ``CalculationTraceStep``, and explicit diagnostic codes.

Import explicitly, e.g.::

    from beamgenius.engine.detailing_bundle_mabhas9 import (
        evaluate_bundle_bar_count,
    )
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

from beamgenius.domain.enums import (
    ConcreteCoverMemberClass,
    DiagnosticSeverity,
    EvaluationOutcome,
    JurisdictionMode,
)
from beamgenius.domain.trace import (
    CalculationTraceStep,
    EngineeringDiagnostic,
    ScalarInputValue,
)
from beamgenius.engine.detailing_spacing_mabhas9 import (
    _blocked_step,
    _invalid_step,
    _malformed_value_diagnostic,
    _missing_input_diagnostic,
)
from beamgenius.registry.catalog import (
    RULE_BG_DETAIL_BUNDLE_001,
    RULE_BG_DETAIL_BUNDLE_002,
    RULE_BG_DETAIL_BUNDLE_003,
    RULE_BG_DETAIL_BUNDLE_004,
    RULE_BG_DETAIL_BUNDLE_005,
    RULE_BG_DETAIL_BUNDLE_006,
    RULE_BG_DETAIL_BUNDLE_007,
    RULE_BG_DETAIL_BUNDLE_008,
)
from beamgenius.registry.gatekeeper import GatekeeperDecision, evaluate_rule_gate

# Constants tied to BG-DETAIL-BUNDLE-001 (Mabhas 9 Clause 9-21-5-1,
# PDF p. 462 / Printed p. 441)
BG_DETAIL_BUNDLE_001_MAX_BARS: int = 4

# Constants tied to BG-DETAIL-BUNDLE-002 (Clause 9-21-5-2,
# PDF p. 463 / Printed p. 442)
BG_DETAIL_BUNDLE_002_COMPRESSED_MIN_TRANSVERSE_DIAMETER_MM: float = 12.0

# Constants tied to BG-DETAIL-BUNDLE-003 (Clause 9-21-5-3,
# PDF p. 463 / Printed p. 442)
BG_DETAIL_BUNDLE_003_BEAM_MAX_BUNDLED_DB_MM: float = 34.0

# Constants tied to BG-DETAIL-BUNDLE-004 (Clause 9-21-5-4,
# PDF p. 463 / Printed p. 442)
BG_DETAIL_BUNDLE_004_CUTOFF_STAGGER_FACTOR: int = 40

# Constants tied to BG-DETAIL-BUNDLE-005 (Clause 9-21-5-5,
# PDF p. 463 / Printed p. 442)
BG_DETAIL_BUNDLE_005_MAX_BARS_PER_PLANE: int = 2

# Constants tied to BG-DETAIL-BUNDLE_007/008 (Clauses 9-21-5-7/8,
# PDF p. 463 / Printed p. 442): development/lap multiplier by bundle size
BG_DETAIL_BUNDLE_007_LD_MULTIPLIERS: Dict[int, float] = {
    2: 1.00,
    3: 1.20,
    4: 1.33,
}


def _not_applicable_step(
    gate: GatekeeperDecision,
    *,
    raw_inputs: Dict[str, ScalarInputValue],
    unit: str,
    message: str,
) -> CalculationTraceStep:
    """Build a NOT_APPLICABLE step through an allowed gate."""
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={},
        final_result=None,
        unit=unit,
        outcome=EvaluationOutcome.NOT_APPLICABLE,
        diagnostics=(),
        message=message,
    )


def _resolve_bundle_scope(
    gate: GatekeeperDecision,
    *,
    raw_inputs: Dict[str, ScalarInputValue],
    bundle_n_bars: Optional[int],
    unit: str,
    not_applicable_above_max: bool = True,
) -> Tuple[Optional[int], Optional[CalculationTraceStep]]:
    """Validate the bundle bar count and apply the common scope guards.

    Returns ``(n, None)`` when evaluation must proceed, or ``(None, step)``
    when a terminal step (BLOCKED / INVALID_INPUT / NOT_APPLICABLE) has
    already been produced:

    - missing count -> BLOCKED (``MISSING_BUNDLE_BAR_COUNT``),
    - malformed count (bool / non-int / < 1) -> ``INVALID_INPUT``,
    - n == 1 (single bar) -> ``NOT_APPLICABLE`` (not a bundle),
    - n > 4 with ``not_applicable_above_max=True`` -> ``NOT_APPLICABLE``:
      the bundle violates Clause 9-21-5-1 and is flagged FAIL by
      ``BG-DETAIL-BUNDLE-001``; satellite bundle clauses defer to it.
    """
    rule = gate.rule
    if bundle_n_bars is None:
        return None, _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_BUNDLE_BAR_COUNT",
                    (
                        "Bundle bar count n is required for every bundled-bar "
                        "clause 9-21-5-x (a single bar is not a bundle; the "
                        "maximum count is 4). Missing required inputs are "
                        "never assumed; BLOCKED."
                    ),
                    rule=rule,
                    field_name="bundle_n_bars",
                )
            ],
        )
    if (
        isinstance(bundle_n_bars, bool)
        or not isinstance(bundle_n_bars, int)
        or bundle_n_bars < 1
    ):
        return None, _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_BUNDLE_BAR_COUNT",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "bundle_n_bars must be an integer >= 1, got "
                        f"{bundle_n_bars!r}."
                    ),
                    rule_id=rule.rule_id,
                    field_name="bundle_n_bars",
                )
            ],
        )
    if bundle_n_bars == 1:
        return None, _not_applicable_step(
            gate,
            raw_inputs=raw_inputs,
            unit=unit,
            message=(
                "NOT_APPLICABLE: a single bar is not a bar bundle "
                "(Clauses 9-21-5-1..8 apply to bundles acting as one unit)."
            ),
        )
    if bundle_n_bars > BG_DETAIL_BUNDLE_001_MAX_BARS and not_applicable_above_max:
        return None, _not_applicable_step(
            gate,
            raw_inputs=raw_inputs,
            unit=unit,
            message=(
                f"NOT_APPLICABLE: a bundle of {bundle_n_bars} bars exceeds "
                "the maximum of 4 bars per Clause 9-21-5-1 (evaluate "
                "BG-DETAIL-BUNDLE-001; the satellite bundled-bar clauses "
                "defer to it for prohibited bundle sizes)."
            ),
        )
    return bundle_n_bars, None


def evaluate_bundle_bar_count(
    *,
    bundle_n_bars: Optional[int] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the maximum bar count per bundle (BG-DETAIL-BUNDLE-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-5-1, PDF p. 462 /
    Printed p. 441: the number of bars in a bar bundle (group of bars
    acting as one unit) is limited to four (n_bundle <= 4).

    The count is a required typed input (never assumed). n == 1 is
    NOT_APPLICABLE; 2..4 -> PASS; n > 4 -> FAIL
    (``BUNDLE_BAR_COUNT_EXCEEDS_MAXIMUM``).
    """
    rule_id = RULE_BG_DETAIL_BUNDLE_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {"bundle_n_bars": bundle_n_bars}

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="1")
    rule = gate.rule

    n, terminal = _resolve_bundle_scope(
        gate,
        raw_inputs=raw_inputs,
        bundle_n_bars=bundle_n_bars,
        unit="1",
        not_applicable_above_max=False,
    )
    if terminal is not None:
        return terminal
    assert n is not None

    # 2. Enforce the Clause 9-21-5-1 maximum of four bars per bundle
    if n > BG_DETAIL_BUNDLE_001_MAX_BARS:
        fail_diag = EngineeringDiagnostic(
            code="BUNDLE_BAR_COUNT_EXCEEDS_MAXIMUM",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: bundle of {n} bars exceeds the maximum of "
                f"{BG_DETAIL_BUNDLE_001_MAX_BARS} bars per bundle per "
                "Clause 9-21-5-1."
            ),
            rule_id=rule_id,
            field_name="bundle_n_bars",
        )
        return CalculationTraceStep.from_rule(
            rule,
            normalized_inputs=raw_inputs,
            intermediate_values={
                "bundle_n_bars": float(n),
                "max_bars_per_bundle": float(BG_DETAIL_BUNDLE_001_MAX_BARS),
            },
            final_result=float(n),
            unit="1",
            outcome=EvaluationOutcome.FAIL,
            diagnostics=(fail_diag,),
            message=fail_diag.message,
        )

    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values={
            "bundle_n_bars": float(n),
            "max_bars_per_bundle": float(BG_DETAIL_BUNDLE_001_MAX_BARS),
        },
        final_result=float(n),
        unit="1",
        outcome=EvaluationOutcome.PASS,
        diagnostics=(),
        message=(
            f"PASS: bundle of {n} bars does not exceed the maximum of "
            f"{BG_DETAIL_BUNDLE_001_MAX_BARS} bars per bundle per "
            "Clause 9-21-5-1."
        ),
    )


def evaluate_bundle_transverse_reinforcement(
    *,
    bundle_n_bars: Optional[int] = None,
    bundle_has_transverse_enclosure: Optional[bool] = None,
    bundle_is_compressed: Optional[bool] = None,
    transverse_bar_diameter_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate bundle transverse reinforcement (BG-DETAIL-BUNDLE-002).

    Verified source: Mabhas 9 (1399), Clause 9-21-5-2, PDF p. 463 /
    Printed p. 442: a bar bundle must be enclosed by transverse
    reinforcement; the transverse bars of bundles under compression must
    be at least 12 mm in diameter.

    Missing enclosure/compression inputs are never assumed (BLOCKED);
    ``transverse_bar_diameter_mm`` is required only for compressed bundles.
    Unenclosed bundle -> FAIL (``BUNDLE_TRANSVERSE_ENCLOSURE_MISSING``);
    compressed bundle with dbt < 12 mm -> FAIL
    (``BUNDLE_COMPRESSED_TRANSVERSE_DIAMETER_BELOW_MINIMUM``). The
    unresolved transverse-spacing details of Clause 9-21-6 remain outside
    this rule (no dependency is invented).
    """
    rule_id = RULE_BG_DETAIL_BUNDLE_002.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bundle_n_bars": bundle_n_bars,
        "bundle_has_transverse_enclosure": bundle_has_transverse_enclosure,
        "bundle_is_compressed": bundle_is_compressed,
        "transverse_bar_diameter_mm": transverse_bar_diameter_mm,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    n, terminal = _resolve_bundle_scope(
        gate, raw_inputs=raw_inputs, bundle_n_bars=bundle_n_bars, unit="mm"
    )
    if terminal is not None:
        return terminal
    assert n is not None

    # 2. Input validation: malformed -> INVALID_INPUT; missing -> BLOCKED
    invalid_diagnostics: List[EngineeringDiagnostic] = []
    missing_diagnostics: List[EngineeringDiagnostic] = []

    enclosure_raw: object = bundle_has_transverse_enclosure
    if enclosure_raw is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_TRANSVERSE_ENCLOSURE",
                (
                    "Whether the bundle is enclosed by transverse "
                    "reinforcement is required (Clause 9-21-5-2); it is never "
                    "assumed. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="bundle_has_transverse_enclosure",
            )
        )
    elif not isinstance(enclosure_raw, bool):
        invalid_diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_TRANSVERSE_ENCLOSURE",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "bundle_has_transverse_enclosure must be a bool, got "
                    f"{enclosure_raw!r}."
                ),
                rule_id=rule_id,
                field_name="bundle_has_transverse_enclosure",
            )
        )

    compressed_raw: object = bundle_is_compressed
    if compressed_raw is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_COMPRESSION_STATE",
                (
                    "Whether the bundle is under compression is required "
                    "(Clause 9-21-5-2 compressed-bundle diameter rule); it "
                    "is never assumed. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="bundle_is_compressed",
            )
        )
    elif not isinstance(compressed_raw, bool):
        invalid_diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_COMPRESSION_STATE",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "bundle_is_compressed must be a bool, got "
                    f"{compressed_raw!r}."
                ),
                rule_id=rule_id,
                field_name="bundle_is_compressed",
            )
        )

    if transverse_bar_diameter_mm is not None and (
        not math.isfinite(transverse_bar_diameter_mm)
        or transverse_bar_diameter_mm <= 0.0
    ):
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                transverse_bar_diameter_mm,
                field_name="transverse_bar_diameter_mm",
                rule=rule,
            )
        )

    if (
        isinstance(compressed_raw, bool)
        and compressed_raw
        and transverse_bar_diameter_mm is None
    ):
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_TRANSVERSE_BAR_DIAMETER",
                (
                    "Transverse bar diameter dbt is required for bundles "
                    "under compression (Clause 9-21-5-2: dbt >= 12 mm); it is "
                    "never assumed. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="transverse_bar_diameter_mm",
            )
        )

    if invalid_diagnostics:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics
        )
    if missing_diagnostics:
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=missing_diagnostics
        )
    bundle_has_transverse_enclosure_typed: bool = enclosure_raw  # type: ignore[assignment]
    bundle_is_compressed_typed: bool = compressed_raw  # type: ignore[assignment]

    # 3. Enclosure requirement
    intermediates: Dict[str, float] = {
        "bundle_n_bars": float(n),
        "min_compressed_transverse_diameter_mm": (
            BG_DETAIL_BUNDLE_002_COMPRESSED_MIN_TRANSVERSE_DIAMETER_MM
        ),
    }
    if transverse_bar_diameter_mm is not None:
        intermediates["transverse_bar_diameter_mm"] = transverse_bar_diameter_mm

    if not bundle_has_transverse_enclosure_typed:
        fail_diag = EngineeringDiagnostic(
            code="BUNDLE_TRANSVERSE_ENCLOSURE_MISSING",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: the bundle is not enclosed by transverse "
                "reinforcement, violating Clause 9-21-5-2."
            ),
            rule_id=rule_id,
            field_name="bundle_has_transverse_enclosure",
        )
        return CalculationTraceStep.from_rule(
            rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.FAIL,
            diagnostics=(fail_diag,),
            message=fail_diag.message,
        )

    # 4. Compressed-bundle transverse diameter >= 12 mm
    if bundle_is_compressed_typed and (
        transverse_bar_diameter_mm is not None
        and transverse_bar_diameter_mm
        < BG_DETAIL_BUNDLE_002_COMPRESSED_MIN_TRANSVERSE_DIAMETER_MM
    ):
        fail_diag = EngineeringDiagnostic(
            code="BUNDLE_COMPRESSED_TRANSVERSE_DIAMETER_BELOW_MINIMUM",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: transverse bar diameter dbt = "
                f"{transverse_bar_diameter_mm} mm of the compressed bundle "
                f"< 12 mm minimum per Clause 9-21-5-2."
            ),
            rule_id=rule_id,
            field_name="transverse_bar_diameter_mm",
        )
        return CalculationTraceStep.from_rule(
            rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=transverse_bar_diameter_mm,
            unit="mm",
            outcome=EvaluationOutcome.FAIL,
            diagnostics=(fail_diag,),
            message=fail_diag.message,
        )

    if bundle_is_compressed_typed:
        message = (
            f"PASS: bundle is enclosed by transverse reinforcement and "
            f"compressed-bundle transverse diameter dbt = "
            f"{transverse_bar_diameter_mm} mm >= 12 mm per Clause 9-21-5-2."
        )
        final_result: Optional[float] = transverse_bar_diameter_mm
    else:
        message = (
            "PASS: bundle is enclosed by transverse reinforcement per "
            "Clause 9-21-5-2 (not under compression; the >= 12 mm "
            "compressed-bundle diameter rule is not triggered)."
        )
        final_result = None
    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=final_result,
        unit="mm",
        outcome=EvaluationOutcome.PASS,
        diagnostics=(),
        message=message,
    )


def evaluate_bundle_beam_bar_diameter(
    *,
    bundle_n_bars: Optional[int] = None,
    member_class: Optional[ConcreteCoverMemberClass] = None,
    bundle_bar_diameter_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the beam bundle bar diameter prohibition (BG-DETAIL-BUNDLE-003).

    Verified source: Mabhas 9 (1399), Clause 9-21-5-3, PDF p. 463 /
    Printed p. 442: in beams, bars with diameter larger than 34 mm are not
    permitted in bundles (beam-specific clause).

    Non-beam member classes -> NOT_APPLICABLE; unknown member class ->
    INVALID_INPUT; missing member class or diameter -> BLOCKED; a bundled
    beam bar with db > 34 mm -> FAIL
    (``BUNDLE_BEAM_BAR_DIAMETER_EXCEEDS_MAXIMUM``); db == 34 mm -> PASS.
    """
    rule_id = RULE_BG_DETAIL_BUNDLE_003.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bundle_n_bars": bundle_n_bars,
        "member_class": (
            member_class.value
            if isinstance(member_class, ConcreteCoverMemberClass)
            else member_class
        ),
        "bundle_bar_diameter_mm": bundle_bar_diameter_mm,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    n, terminal = _resolve_bundle_scope(
        gate, raw_inputs=raw_inputs, bundle_n_bars=bundle_n_bars, unit="mm"
    )
    if terminal is not None:
        return terminal
    assert n is not None

    # 2. Member class: Clause 9-21-5-3 is beam-specific
    member_class_raw: object = member_class
    if member_class_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_MEMBER_CLASS",
                    (
                        "The member class is required to apply the "
                        "beam-specific Clause 9-21-5-3; it is never assumed. "
                        "Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="member_class",
                )
            ],
        )
    if not isinstance(member_class_raw, ConcreteCoverMemberClass):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="UNKNOWN_MEMBER_CLASS",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "member_class must be a ConcreteCoverMemberClass "
                        f"enumeration value, got {member_class_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="member_class",
                )
            ],
        )
    member_class_typed: ConcreteCoverMemberClass = member_class_raw
    if member_class_typed is not ConcreteCoverMemberClass.BEAM:
        return _not_applicable_step(
            gate,
            raw_inputs=raw_inputs,
            unit="mm",
            message=(
                "NOT_APPLICABLE: Clause 9-21-5-3 (bundled-bar diameter "
                f"prohibition) is beam-specific; member class "
                f"'{member_class_typed.value}' is out of scope."
            ),
        )

    # 3. Diameter validation: malformed -> INVALID_INPUT; missing -> BLOCKED
    if bundle_bar_diameter_mm is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_GOVERNING_BAR_DIAMETER",
                    (
                        "The governing bundle bar diameter db is required "
                        "(Clause 9-21-5-3: beam bundled db > 34 mm "
                        "prohibited); it is never assumed. Missing required "
                        "input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="bundle_bar_diameter_mm",
                )
            ],
        )
    if not math.isfinite(bundle_bar_diameter_mm) or bundle_bar_diameter_mm <= 0.0:
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _malformed_value_diagnostic(
                    bundle_bar_diameter_mm,
                    field_name="bundle_bar_diameter_mm",
                    rule=rule,
                )
            ],
        )

    intermediates: Dict[str, float] = {
        "bundle_n_bars": float(n),
        "bundle_bar_diameter_mm": bundle_bar_diameter_mm,
        "beam_max_bundled_db_mm": BG_DETAIL_BUNDLE_003_BEAM_MAX_BUNDLED_DB_MM,
    }
    if bundle_bar_diameter_mm > BG_DETAIL_BUNDLE_003_BEAM_MAX_BUNDLED_DB_MM:
        fail_diag = EngineeringDiagnostic(
            code="BUNDLE_BEAM_BAR_DIAMETER_EXCEEDS_MAXIMUM",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: bundled beam bar diameter db = "
                f"{bundle_bar_diameter_mm} mm > "
                f"{BG_DETAIL_BUNDLE_003_BEAM_MAX_BUNDLED_DB_MM} mm, "
                "prohibited in beams per Clause 9-21-5-3."
            ),
            rule_id=rule_id,
            field_name="bundle_bar_diameter_mm",
        )
        return CalculationTraceStep.from_rule(
            rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=bundle_bar_diameter_mm,
            unit="mm",
            outcome=EvaluationOutcome.FAIL,
            diagnostics=(fail_diag,),
            message=fail_diag.message,
        )

    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=bundle_bar_diameter_mm,
        unit="mm",
        outcome=EvaluationOutcome.PASS,
        diagnostics=(),
        message=(
            f"PASS: bundled beam bar diameter db = {bundle_bar_diameter_mm} "
            f"mm <= {BG_DETAIL_BUNDLE_003_BEAM_MAX_BUNDLED_DB_MM} mm per "
            "Clause 9-21-5-3."
        ),
    )


def evaluate_bundle_cutoff_stagger(
    *,
    bundle_n_bars: Optional[int] = None,
    bundle_has_cutoffs: Optional[bool] = None,
    bundle_bar_diameter_mm: Optional[float] = None,
    bundle_cutoff_positions_mm: Optional[Sequence[float]] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate bundle cutoff point staggering (BG-DETAIL-BUNDLE-004).

    Verified source: Mabhas 9 (1399), Clause 9-21-5-4, PDF p. 463 /
    Printed p. 442: along the span of flexural members, the cutoff point
    of each bar of a bundle must be at least 40 bar diameters from the
    cutoff points of the other bars of the bundle.

    The cutoff configuration is a required typed input (never assumed):
    ``bundle_has_cutoffs=False`` -> NOT_APPLICABLE; with cutoffs, the bar
    diameter and cutoff positions are required (missing -> BLOCKED); fewer
    than two cut bars -> NOT_APPLICABLE (no pair to stagger); any pair of
    cutoff points closer than 40*db -> FAIL
    (``BUNDLE_CUTOFF_STAGGER_BELOW_MINIMUM``).
    """
    rule_id = RULE_BG_DETAIL_BUNDLE_004.rule_id
    positions_snapshot: Optional[str] = None
    if bundle_cutoff_positions_mm is not None:
        positions_snapshot = ",".join(repr(p) for p in bundle_cutoff_positions_mm)
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bundle_n_bars": bundle_n_bars,
        "bundle_has_cutoffs": bundle_has_cutoffs,
        "bundle_bar_diameter_mm": bundle_bar_diameter_mm,
        "bundle_cutoff_positions_mm": positions_snapshot,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    n, terminal = _resolve_bundle_scope(
        gate, raw_inputs=raw_inputs, bundle_n_bars=bundle_n_bars, unit="mm"
    )
    if terminal is not None:
        return terminal
    assert n is not None

    # 2. Cutoff configuration flag (never assumed)
    cutoffs_raw: object = bundle_has_cutoffs
    if cutoffs_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_CUTOFF_CONFIGURATION",
                    (
                        "Whether bars of the bundle are cut off along the "
                        "span is required (Clause 9-21-5-4); it is never "
                        "assumed. Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="bundle_has_cutoffs",
                )
            ],
        )
    if not isinstance(cutoffs_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_CUTOFF_CONFIGURATION",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "bundle_has_cutoffs must be a bool, got "
                        f"{cutoffs_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="bundle_has_cutoffs",
                )
            ],
        )
    bundle_has_cutoffs_typed: bool = cutoffs_raw
    if not bundle_has_cutoffs_typed:
        return _not_applicable_step(
            gate,
            raw_inputs=raw_inputs,
            unit="mm",
            message=(
                "NOT_APPLICABLE: no bar of the bundle is cut off along the "
                "span; the cutoff staggering of Clause 9-21-5-4 does not "
                "apply."
            ),
        )

    # 3. With cutoffs: diameter and positions are required
    invalid_diagnostics: List[EngineeringDiagnostic] = []
    missing_diagnostics: List[EngineeringDiagnostic] = []

    if bundle_bar_diameter_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_GOVERNING_BAR_DIAMETER",
                (
                    "The bundle bar diameter db is required for the 40*db "
                    "staggering of Clause 9-21-5-4; it is never assumed. "
                    "Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="bundle_bar_diameter_mm",
            )
        )
    elif not math.isfinite(bundle_bar_diameter_mm) or bundle_bar_diameter_mm <= 0.0:
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                bundle_bar_diameter_mm,
                field_name="bundle_bar_diameter_mm",
                rule=rule,
            )
        )

    if bundle_cutoff_positions_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_BUNDLE_CUTOFF_POSITIONS",
                (
                    "The axial positions of the bundle bar cutoff points are "
                    "required (Clause 9-21-5-4); they are never assumed. "
                    "Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="bundle_cutoff_positions_mm",
            )
        )
    else:
        for index, position in enumerate(bundle_cutoff_positions_mm):
            position_raw: object = position
            if (
                not isinstance(position_raw, (int, float))
                or isinstance(position_raw, bool)
                or not math.isfinite(position_raw)
            ):
                invalid_diagnostics.append(
                    EngineeringDiagnostic(
                        code="INVALID_BUNDLE_CUTOFF_POSITIONS",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            "Each bundle cutoff position must be a finite "
                            f"number (mm), got {position_raw!r} at index {index}."
                        ),
                        rule_id=rule_id,
                        field_name="bundle_cutoff_positions_mm",
                    )
                )

    if invalid_diagnostics:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics
        )
    if missing_diagnostics:
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=missing_diagnostics
        )
    assert bundle_bar_diameter_mm is not None
    assert bundle_cutoff_positions_mm is not None

    positions = sorted(float(p) for p in bundle_cutoff_positions_mm)
    if len(positions) < 2:
        return _not_applicable_step(
            gate,
            raw_inputs=raw_inputs,
            unit="mm",
            message=(
                "NOT_APPLICABLE: fewer than two bars of the bundle are cut "
                "off along the span; no cutoff-point pair requires the "
                "40*db staggering of Clause 9-21-5-4."
            ),
        )

    # 4. Minimum pairwise cutoff distance >= 40*db
    stagger_required_mm = BG_DETAIL_BUNDLE_004_CUTOFF_STAGGER_FACTOR * bundle_bar_diameter_mm
    min_distance_mm = min(
        positions[i + 1] - positions[i] for i in range(len(positions) - 1)
    )

    intermediates: Dict[str, float] = {
        "bundle_n_bars": float(n),
        "bundle_bar_diameter_mm": bundle_bar_diameter_mm,
        "cutoff_count": float(len(positions)),
        "stagger_factor": float(BG_DETAIL_BUNDLE_004_CUTOFF_STAGGER_FACTOR),
        "stagger_required_mm": stagger_required_mm,
        "min_cutoff_pair_distance_mm": min_distance_mm,
    }

    if min_distance_mm < stagger_required_mm:
        fail_diag = EngineeringDiagnostic(
            code="BUNDLE_CUTOFF_STAGGER_BELOW_MINIMUM",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: closest bundle bar cutoff points are "
                f"{min_distance_mm} mm apart < 40*db = "
                f"{stagger_required_mm} mm required by Clause 9-21-5-4."
            ),
            rule_id=rule_id,
            field_name="bundle_cutoff_positions_mm",
        )
        return CalculationTraceStep.from_rule(
            rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=stagger_required_mm,
            unit="mm",
            outcome=EvaluationOutcome.FAIL,
            diagnostics=(fail_diag,),
            message=fail_diag.message,
        )

    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=stagger_required_mm,
        unit="mm",
        outcome=EvaluationOutcome.PASS,
        diagnostics=(),
        message=(
            f"PASS: closest bundle bar cutoff points are {min_distance_mm} "
            f"mm apart >= 40*db = {stagger_required_mm} mm per Clause "
            "9-21-5-4."
        ),
    )


def evaluate_bundle_plane_arrangement(
    *,
    bundle_n_bars: Optional[int] = None,
    bundle_max_bars_in_single_plane: Optional[int] = None,
    bundle_is_splice_location: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the bundle bar plane arrangement limit (BG-DETAIL-BUNDLE-005).

    Verified source: Mabhas 9 (1399), Clause 9-21-5-5, PDF p. 463 /
    Printed p. 442: in bundles with more than two bars, not all bar axes
    may lie in one plane, and at most two bars may lie in one plane,
    except at splice locations.

    Bundles of two bars or fewer -> NOT_APPLICABLE; the plane arrangement
    and splice-location status are required typed inputs (never assumed);
    more than two bars in one plane at a non-splice location -> FAIL
    (``BUNDLE_BARS_PER_PLANE_EXCEEDED``); at a splice location the
    exception applies -> PASS (noted in the message).
    """
    rule_id = RULE_BG_DETAIL_BUNDLE_005.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bundle_n_bars": bundle_n_bars,
        "bundle_max_bars_in_single_plane": bundle_max_bars_in_single_plane,
        "bundle_is_splice_location": bundle_is_splice_location,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="1")
    rule = gate.rule

    # Clause 9-21-5-5 applies only to bundles with more than two bars
    if bundle_n_bars is not None and isinstance(bundle_n_bars, int) and not isinstance(bundle_n_bars, bool) and bundle_n_bars == 2:
        return _not_applicable_step(
            gate,
            raw_inputs=raw_inputs,
            unit="1",
            message=(
                "NOT_APPLICABLE: Clause 9-21-5-5 plane arrangement applies "
                "only to bundles with more than two bars."
            ),
        )

    n, terminal = _resolve_bundle_scope(
        gate, raw_inputs=raw_inputs, bundle_n_bars=bundle_n_bars, unit="1"
    )
    if terminal is not None:
        return terminal
    assert n is not None and n >= 3

    # 2. Input validation: malformed -> INVALID_INPUT; missing -> BLOCKED
    invalid_diagnostics: List[EngineeringDiagnostic] = []
    missing_diagnostics: List[EngineeringDiagnostic] = []

    plane_raw: object = bundle_max_bars_in_single_plane
    if plane_raw is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_BUNDLE_PLANE_ARRANGEMENT",
                (
                    "The maximum number of bundle bars lying in one plane is "
                    "required (Clause 9-21-5-5); it is never assumed. "
                    "Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="bundle_max_bars_in_single_plane",
            )
        )
    elif (
        isinstance(plane_raw, bool)
        or not isinstance(plane_raw, int)
        or plane_raw < 1
        or plane_raw > n
    ):
        invalid_diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_BUNDLE_PLANE_ARRANGEMENT",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "bundle_max_bars_in_single_plane must be an integer in "
                    f"[1, {n}] for a bundle of {n} bars, got "
                    f"{plane_raw!r}."
                ),
                rule_id=rule_id,
                field_name="bundle_max_bars_in_single_plane",
            )
        )

    splice_raw: object = bundle_is_splice_location
    if splice_raw is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_SPLICE_LOCATION_STATUS",
                (
                    "Whether the section is at a splice location is required "
                    "for the Clause 9-21-5-5 splice exception; it is never "
                    "assumed. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="bundle_is_splice_location",
            )
        )
    elif not isinstance(splice_raw, bool):
        invalid_diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_SPLICE_LOCATION_STATUS",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "bundle_is_splice_location must be a bool, got "
                    f"{splice_raw!r}."
                ),
                rule_id=rule_id,
                field_name="bundle_is_splice_location",
            )
        )

    if invalid_diagnostics:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics
        )
    if missing_diagnostics:
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=missing_diagnostics
        )
    bundle_max_bars_in_single_plane_typed: int = plane_raw  # type: ignore[assignment]
    bundle_is_splice_location_typed: bool = splice_raw  # type: ignore[assignment]

    intermediates: Dict[str, float] = {
        "bundle_n_bars": float(n),
        "max_bars_per_plane": float(BG_DETAIL_BUNDLE_005_MAX_BARS_PER_PLANE),
        "provided_max_bars_in_single_plane": float(
            bundle_max_bars_in_single_plane_typed
        ),
    }

    if (
        bundle_max_bars_in_single_plane_typed
        > BG_DETAIL_BUNDLE_005_MAX_BARS_PER_PLANE
        and not bundle_is_splice_location_typed
    ):
        fail_diag = EngineeringDiagnostic(
            code="BUNDLE_BARS_PER_PLANE_EXCEEDED",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: {bundle_max_bars_in_single_plane_typed} bars of the "
                f"{n}-bar bundle lie in one plane > "
                f"{BG_DETAIL_BUNDLE_005_MAX_BARS_PER_PLANE} maximum per "
                "Clause 9-21-5-5 (splice exception not applicable here)."
            ),
            rule_id=rule_id,
            field_name="bundle_max_bars_in_single_plane",
        )
        return CalculationTraceStep.from_rule(
            rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=float(bundle_max_bars_in_single_plane_typed),
            unit="1",
            outcome=EvaluationOutcome.FAIL,
            diagnostics=(fail_diag,),
            message=fail_diag.message,
        )

    if (
        bundle_max_bars_in_single_plane_typed
        > BG_DETAIL_BUNDLE_005_MAX_BARS_PER_PLANE
        and bundle_is_splice_location_typed
    ):
        message = (
            f"PASS: {bundle_max_bars_in_single_plane_typed} bars in one plane "
            "exceeds the general limit of "
            f"{BG_DETAIL_BUNDLE_005_MAX_BARS_PER_PLANE}, but the section is "
            "at a splice location, where Clause 9-21-5-5 permits the "
            "exception."
        )
    else:
        message = (
            f"PASS: at most {bundle_max_bars_in_single_plane_typed} bars of the "
            f"{n}-bar bundle lie in one plane (<= "
            f"{BG_DETAIL_BUNDLE_005_MAX_BARS_PER_PLANE}) per Clause 9-21-5-5."
        )
    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=float(bundle_max_bars_in_single_plane_typed),
        unit="1",
        outcome=EvaluationOutcome.PASS,
        diagnostics=(),
        message=message,
    )


def evaluate_bundle_equivalent_diameter(
    *,
    bundle_n_bars: Optional[int] = None,
    bundle_bar_diameter_mm: Optional[float] = None,
    bundle_bars_identical: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the bundle equivalent bar diameter (BG-DETAIL-BUNDLE-006).

    Verified source: Mabhas 9 (1399), Clause 9-21-5-6, PDF p. 463 /
    Printed p. 442: for checks whose calculation is based on bar diameter
    — spacing limits, minimum cover, confinement coefficient of
    Clause 9-21-3-2-1 and coating factor of Clause 9-21-3-2-2 — a bundle
    is treated as one equivalent bar of equal total area whose centroid
    coincides with the bundle centroid; for ``n`` identical bars:

        d_eq = db * sqrt(n)

    Only the identical-bar form is implemented (verified numeric rule).
    Mixed-diameter bundles return BLOCKED (``UNSUPPORTED_CONFIGURATION``):
    the equal-area/coincident-centroid construction exists in the source,
    but no verified closed-form diameter for mixed bundles is applied.
    Development length is NEVER computed from d_eq (Clause 9-21-5-7
    provides its own multipliers; see ``evaluate_bundle_development_length``).
    """
    rule_id = RULE_BG_DETAIL_BUNDLE_006.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bundle_n_bars": bundle_n_bars,
        "bundle_bar_diameter_mm": bundle_bar_diameter_mm,
        "bundle_bars_identical": bundle_bars_identical,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    n, terminal = _resolve_bundle_scope(
        gate, raw_inputs=raw_inputs, bundle_n_bars=bundle_n_bars, unit="mm"
    )
    if terminal is not None:
        return terminal
    assert n is not None

    # 2. Input validation: malformed -> INVALID_INPUT; missing -> BLOCKED
    invalid_diagnostics: List[EngineeringDiagnostic] = []
    missing_diagnostics: List[EngineeringDiagnostic] = []

    identical_raw: object = bundle_bars_identical
    if identical_raw is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_BUNDLE_BARS_IDENTICAL",
                (
                    "Whether all bars of the bundle have identical diameter "
                    "is required to select the verified identical-bar form "
                    "d_eq = db*sqrt(n) of Clause 9-21-5-6; it is never "
                    "assumed. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="bundle_bars_identical",
            )
        )
    elif not isinstance(identical_raw, bool):
        invalid_diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_BUNDLE_BARS_IDENTICAL",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "bundle_bars_identical must be a bool, got "
                    f"{identical_raw!r}."
                ),
                rule_id=rule_id,
                field_name="bundle_bars_identical",
            )
        )

    if bundle_bar_diameter_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_GOVERNING_BAR_DIAMETER",
                (
                    "The bundle bar diameter db is required (Clause 9-21-5-6: "
                    "d_eq = db*sqrt(n)); it is never assumed. Missing "
                    "required input -> BLOCKED."
                ),
                rule=rule,
                field_name="bundle_bar_diameter_mm",
            )
        )
    elif not math.isfinite(bundle_bar_diameter_mm) or bundle_bar_diameter_mm <= 0.0:
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                bundle_bar_diameter_mm,
                field_name="bundle_bar_diameter_mm",
                rule=rule,
            )
        )

    if invalid_diagnostics:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics
        )
    if missing_diagnostics:
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=missing_diagnostics
        )
    bundle_bars_identical_typed: bool = identical_raw  # type: ignore[assignment]
    assert bundle_bar_diameter_mm is not None

    if not bundle_bars_identical_typed:
        unsupported_diag = EngineeringDiagnostic(
            code="UNSUPPORTED_CONFIGURATION",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: only the identical-bar form "
                "d_eq = db*sqrt(n) of Clause 9-21-5-6 is implemented; the "
                "equal-area / coincident-centroid construction for "
                "mixed-diameter bundles has no verified closed-form "
                "implementation here. UNVERIFIED_RULE_BLOCKED "
                "(UNSUPPORTED_CONFIGURATION)."
            ),
            rule_id=rule_id,
            field_name="bundle_bars_identical",
            required_verification=(
                "Demand identical bar diameters, or supply a verified "
                "mixed-diameter equivalent-area construction before "
                "evaluating the equivalent diameter."
            ),
        )
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=[unsupported_diag]
        )

    # 3. d_eq = db * sqrt(n) with equal-area check
    d_eq_mm = bundle_bar_diameter_mm * math.sqrt(n)
    single_bar_area_mm2 = math.pi * bundle_bar_diameter_mm**2 / 4.0
    total_bundle_area_mm2 = single_bar_area_mm2 * n
    equivalent_bar_area_mm2 = math.pi * d_eq_mm**2 / 4.0

    intermediates: Dict[str, float] = {
        "bundle_n_bars": float(n),
        "bundle_bar_diameter_mm": bundle_bar_diameter_mm,
        "single_bar_area_mm2": single_bar_area_mm2,
        "total_bundle_area_mm2": total_bundle_area_mm2,
        "equivalent_bar_area_mm2": equivalent_bar_area_mm2,
        "area_equality_check_total_minus_equivalent_mm2": (
            total_bundle_area_mm2 - equivalent_bar_area_mm2
        ),
    }

    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=d_eq_mm,
        unit="mm",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(
            f"Computed equivalent bar diameter d_eq = db*sqrt(n) = "
            f"{bundle_bar_diameter_mm} * sqrt({n}) = {d_eq_mm} mm per "
            "Clause 9-21-5-6 (equal total area; centroid coincident with "
            "the bundle centroid). For development length use the Clause "
            "9-21-5-7 multipliers, never d_eq."
        ),
    )


def evaluate_bundle_development_length(
    *,
    bundle_n_bars: Optional[int] = None,
    single_bar_development_length_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the bundle development length multiplier (BG-DETAIL-BUNDLE-007).

    Verified source: Mabhas 9 (1399), Clause 9-21-5-7, PDF p. 463 /
    Printed p. 442: the development length of bars in a bundle, in tension
    or compression, equals the single-bar development length for a 2-bar
    bundle, and is 20% and 33% greater for 3-bar and 4-bar bundles:

        ld_bundle = factor * ld_single,  factor = {2: 1.00, 3: 1.20, 4: 1.33}

    This rule applies ONLY the verified bundle multipliers. The underlying
    single-bar development length of Clause 9-21-3 is NEVER computed here:
    a missing verified ``single_bar_development_length_mm`` deterministically
    returns BLOCKED (``MISSING_SINGLE_BAR_DEVELOPMENT_LENGTH``).
    """
    rule_id = RULE_BG_DETAIL_BUNDLE_007.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bundle_n_bars": bundle_n_bars,
        "single_bar_development_length_mm": single_bar_development_length_mm,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    n, terminal = _resolve_bundle_scope(
        gate, raw_inputs=raw_inputs, bundle_n_bars=bundle_n_bars, unit="mm"
    )
    if terminal is not None:
        return terminal
    assert n is not None

    # 2. Single-bar development length: required typed input (NEVER computed)
    if single_bar_development_length_mm is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_SINGLE_BAR_DEVELOPMENT_LENGTH",
                    (
                        "The verified single-bar development length ld "
                        "(Clause 9-21-3) is required input for the bundle "
                        "multipliers of Clause 9-21-5-7; Clause 9-21-3 is "
                        "NOT computed by this rule (VERIFY_PENDING). Missing "
                        "required input -> BLOCKED, never an invented value."
                    ),
                    rule=rule,
                    field_name="single_bar_development_length_mm",
                    required_verification=(
                        "Supply the single-bar development length from a "
                        "verified Clause 9-21-3 evaluation; the engine does "
                        "not compute Clause 9-21-3 development length."
                    ),
                )
            ],
        )
    if (
        not math.isfinite(single_bar_development_length_mm)
        or single_bar_development_length_mm <= 0.0
    ):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _malformed_value_diagnostic(
                    single_bar_development_length_mm,
                    field_name="single_bar_development_length_mm",
                    rule=rule,
                )
            ],
        )

    # 3. Apply the verified multiplier table
    factor = BG_DETAIL_BUNDLE_007_LD_MULTIPLIERS.get(n)
    assert factor is not None  # 2 <= n <= 4 guaranteed by scope resolution
    ld_bundle_mm = factor * single_bar_development_length_mm

    intermediates: Dict[str, float] = {
        "bundle_n_bars": float(n),
        "single_bar_development_length_mm": single_bar_development_length_mm,
        "bundle_development_length_factor": factor,
        "bundle_development_length_mm": ld_bundle_mm,
    }

    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=ld_bundle_mm,
        unit="mm",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(
            f"Computed bundled-bar development length (tension or "
            f"compression): ld_bundle = {factor} * {single_bar_development_length_mm} "
            f"= {ld_bundle_mm} mm per Clause 9-21-5-7 (2-bar 1.00 / 3-bar "
            "1.20 / 4-bar 1.33 multiplier)."
        ),
    )


def evaluate_bundle_lap_splice(
    *,
    bundle_n_bars: Optional[int] = None,
    single_bar_development_length_mm: Optional[float] = None,
    bundle_is_bundle_to_bundle_lap: Optional[bool] = None,
    bundle_laps_overlap: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate bundle lap splice constraints (BG-DETAIL-BUNDLE-008).

    Verified source: Mabhas 9 (1399), Clause 9-21-5-8, PDF p. 463 /
    Printed p. 442 (text continuing onto the following page):

    - the lap splice length of each bar in a bundle is computed from the
      single-bar development length including the Clause 9-21-5-7 bundle
      increase (multiplier {2: 1.00, 3: 1.20, 4: 1.33});
    - the laps of individual bars of a bundle must not overlap along the
      bars;
    - a lap splice of a whole bundle with another bundle is prohibited.

    Only these verified bundle-specific constraints are implemented. The
    underlying lap rules of Clause 9-21-4 are NOT computed here: a missing
    verified single-bar development length returns BLOCKED
    (``MISSING_SINGLE_BAR_DEVELOPMENT_LENGTH``), never an invented value.
    Bundle-to-bundle lap -> FAIL (``BUNDLE_TO_BUNDLE_LAP_SPLICE_PROHIBITED``);
    overlapping individual laps -> FAIL
    (``BUNDLE_INDIVIDUAL_LAPS_OVERLAP_PROHIBITED``); otherwise the per-bar
    lap length is COMPUTED.
    """
    rule_id = RULE_BG_DETAIL_BUNDLE_008.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bundle_n_bars": bundle_n_bars,
        "single_bar_development_length_mm": single_bar_development_length_mm,
        "bundle_is_bundle_to_bundle_lap": bundle_is_bundle_to_bundle_lap,
        "bundle_laps_overlap": bundle_laps_overlap,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    n, terminal = _resolve_bundle_scope(
        gate, raw_inputs=raw_inputs, bundle_n_bars=bundle_n_bars, unit="mm"
    )
    if terminal is not None:
        return terminal
    assert n is not None

    # 2. Input validation: malformed -> INVALID_INPUT; missing -> BLOCKED
    invalid_diagnostics: List[EngineeringDiagnostic] = []
    missing_diagnostics: List[EngineeringDiagnostic] = []

    if single_bar_development_length_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_SINGLE_BAR_DEVELOPMENT_LENGTH",
                (
                    "The verified single-bar development length ld "
                    "(Clause 9-21-3) is required input for the bundle lap "
                    "rule of Clause 9-21-5-8; Clauses 9-21-3/9-21-4 are NOT "
                    "computed by this rule (VERIFY_PENDING). Missing "
                    "required input -> BLOCKED, never an invented value."
                ),
                rule=rule,
                field_name="single_bar_development_length_mm",
                required_verification=(
                    "Supply the single-bar development length from a "
                    "verified Clause 9-21-3 evaluation; the engine does not "
                    "compute Clause 9-21-3 development length or the "
                    "underlying Clause 9-21-4 lap rules."
                ),
            )
        )
    elif (
        not math.isfinite(single_bar_development_length_mm)
        or single_bar_development_length_mm <= 0.0
    ):
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                single_bar_development_length_mm,
                field_name="single_bar_development_length_mm",
                rule=rule,
            )
        )

    b2b_raw: object = bundle_is_bundle_to_bundle_lap
    if b2b_raw is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_BUNDLE_LAP_TYPE",
                (
                    "Whether the lap splices whole bundles to each other is "
                    "required (Clause 9-21-5-8 prohibition); it is never "
                    "assumed. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="bundle_is_bundle_to_bundle_lap",
            )
        )
    elif not isinstance(b2b_raw, bool):
        invalid_diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_BUNDLE_LAP_TYPE",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "bundle_is_bundle_to_bundle_lap must be a bool, got "
                    f"{b2b_raw!r}."
                ),
                rule_id=rule_id,
                field_name="bundle_is_bundle_to_bundle_lap",
            )
        )

    overlap_raw: object = bundle_laps_overlap
    if overlap_raw is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_BUNDLE_LAP_OVERLAP_STATUS",
                (
                    "Whether the laps of individual bundle bars overlap "
                    "along the bars is required (Clause 9-21-5-8); it is "
                    "never assumed. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="bundle_laps_overlap",
            )
        )
    elif not isinstance(overlap_raw, bool):
        invalid_diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_BUNDLE_LAP_OVERLAP_STATUS",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "bundle_laps_overlap must be a bool, got "
                    f"{overlap_raw!r}."
                ),
                rule_id=rule_id,
                field_name="bundle_laps_overlap",
            )
        )

    if invalid_diagnostics:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics
        )
    if missing_diagnostics:
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=missing_diagnostics
        )
    assert single_bar_development_length_mm is not None
    bundle_is_bundle_to_bundle_lap_typed: bool = b2b_raw  # type: ignore[assignment]
    bundle_laps_overlap_typed: bool = overlap_raw  # type: ignore[assignment]

    # 3. Per-bar lap length (Clause 9-21-5-8 -> 9-21-5-7 multipliers)
    factor = BG_DETAIL_BUNDLE_007_LD_MULTIPLIERS.get(n)
    assert factor is not None  # 2 <= n <= 4 guaranteed by scope resolution
    lap_length_mm = factor * single_bar_development_length_mm

    intermediates: Dict[str, float] = {
        "bundle_n_bars": float(n),
        "single_bar_development_length_mm": single_bar_development_length_mm,
        "bundle_lap_splice_factor": factor,
        "bundle_bar_lap_length_mm": lap_length_mm,
    }

    if bundle_is_bundle_to_bundle_lap_typed:
        fail_diag = EngineeringDiagnostic(
            code="BUNDLE_TO_BUNDLE_LAP_SPLICE_PROHIBITED",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: a lap splice of a whole bundle with another bundle "
                "is prohibited per Clause 9-21-5-8."
            ),
            rule_id=rule_id,
            field_name="bundle_is_bundle_to_bundle_lap",
        )
        return CalculationTraceStep.from_rule(
            rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=lap_length_mm,
            unit="mm",
            outcome=EvaluationOutcome.FAIL,
            diagnostics=(fail_diag,),
            message=fail_diag.message,
        )

    if bundle_laps_overlap_typed:
        fail_diag = EngineeringDiagnostic(
            code="BUNDLE_INDIVIDUAL_LAPS_OVERLAP_PROHIBITED",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: the laps of individual bars of the bundle overlap "
                "along the bars, prohibited per Clause 9-21-5-8."
            ),
            rule_id=rule_id,
            field_name="bundle_laps_overlap",
        )
        return CalculationTraceStep.from_rule(
            rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=lap_length_mm,
            unit="mm",
            outcome=EvaluationOutcome.FAIL,
            diagnostics=(fail_diag,),
            message=fail_diag.message,
        )

    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=lap_length_mm,
        unit="mm",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(
            f"Computed per-bar bundle lap splice length: lap = {factor} * "
            f"{single_bar_development_length_mm} = {lap_length_mm} mm per "
            "Clauses 9-21-5-8/9-21-5-7; individual laps do not overlap and "
            "no bundle-to-bundle lap is used. The underlying Clause 9-21-4 "
            "lap rules are not computed here."
        ),
    )
