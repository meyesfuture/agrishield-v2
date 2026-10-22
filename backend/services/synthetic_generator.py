"""
Deterministic Synthetic Scenario Generator for Punjab GrainWatch.
Generates Scenarios A through E for offline, reproducible algorithm testing and demonstration.
Strictly isolates synthetic records with explicit metadata: is_synthetic=true, data_mode="SYNTHETIC_DEMO".
"""

import json
import random
from pathlib import Path
from datetime import date, timedelta
from typing import Dict, List, Optional
from backend.schemas.decision import (
    ScenarioSummary,
    ScenarioDetail,
    ObservationPoint,
    DecisionStatus,
)


class SyntheticScenarioGenerator:
    """Generates deterministic, versioned synthetic market scenarios."""

    SEED = 42

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (Path(__file__).resolve().parent.parent.parent / "data" / "synthetic" / "scenarios")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_dates(self, start_date: date, count: int) -> List[str]:
        return [(start_date + timedelta(days=i)).isoformat() for i in range(count)]

    def generate_scenario_a(self) -> ScenarioDetail:
        """Scenario A — Normal Baseline: ordinary price and arrival variations."""
        rng = random.Random(self.SEED + 101)
        start_d = date(2026, 9, 1)
        dates = self._generate_dates(start_d, 45)

        base_price = 2125.0   # Rs./Quintal (MSP baseline)
        base_arrival = 2500.0 # Quintals

        observations: List[ObservationPoint] = []
        for d in dates:
            p_noise = rng.gauss(0, 25.0)   # ±1.2%
            a_noise = rng.gauss(0, 100.0)  # ±4.0%
            observations.append(
                ObservationPoint(
                    date=d,
                    modal_price=round(base_price + p_noise, 1),
                    arrival_quantity=round(base_arrival + a_noise, 1),
                    is_anomaly_candidate=False,
                    notes="Expected seasonal variation within baseline IQR.",
                )
            )

        return ScenarioDetail(
            scenario_id="scenario_a_normal_baseline",
            title="Scenario A: Normal Market Baseline",
            description="Consistent historical price and arrival series with ordinary seasonal variation. All criteria satisfied without anomaly.",
            expected_decision_status=DecisionStatus.NO_MATERIAL_ANOMALY,
            location_name="Ludhiana Central Mandi (Synthetic)",
            commodity_name="Wheat (Common Foodgrain)",
            baseline_window="2026-09-01 to 2026-10-15 (45 days)",
            anomaly_window=None,
            observations=observations,
        )

    def generate_scenario_b(self, inject_anomaly: bool = True) -> ScenarioDetail:
        """Scenario B — Planted Convergent Anomaly: price surge + arrival collapse."""
        rng = random.Random(self.SEED + 102)
        start_d = date(2026, 9, 1)
        dates = self._generate_dates(start_d, 45)

        base_price = 2125.0
        base_arrival = 2500.0

        observations: List[ObservationPoint] = []
        for i, d in enumerate(dates):
            if i < 30 or not inject_anomaly:
                # Normal baseline (days 1–30)
                p_noise = rng.gauss(0, 25.0)
                a_noise = rng.gauss(0, 100.0)
                observations.append(
                    ObservationPoint(
                        date=d,
                        modal_price=round(base_price + p_noise, 1),
                        arrival_quantity=round(base_arrival + a_noise, 1),
                        is_anomaly_candidate=False,
                        notes="Normal pre-divergence baseline.",
                    )
                )
            else:
                # Planted anomaly event (days 31–45): Price surges +48%, Arrivals collapse -64%
                progress = (i - 30) / 14.0
                price_surge = base_price * (1.0 + 0.35 + 0.15 * progress) + rng.gauss(0, 30.0)
                arrival_drop = base_arrival * (1.0 - 0.50 - 0.15 * progress) + rng.gauss(0, 40.0)
                observations.append(
                    ObservationPoint(
                        date=d,
                        modal_price=round(price_surge, 1),
                        arrival_quantity=round(max(200.0, arrival_drop), 1),
                        is_anomaly_candidate=True,
                        notes="Planted convergent supply shock: simultaneous price spike and arrival collapse.",
                    )
                )

        status = DecisionStatus.CONVERGENT_SUPPLY_ANOMALY if inject_anomaly else DecisionStatus.NO_MATERIAL_ANOMALY
        title = "Scenario B: Planted Convergent Supply Anomaly" if inject_anomaly else "Scenario B: Restored Baseline (Anomaly Removed)"
        desc = (
            "Deliberately engineered divergence: significant price increase (+48%) paired with severe arrival collapse (-64%) across matching market dates."
            if inject_anomaly
            else "Planted anomaly removed; series restored to normal baseline."
        )

        return ScenarioDetail(
            scenario_id="scenario_b_convergent_anomaly" if inject_anomaly else "scenario_b_restored_baseline",
            title=title,
            description=desc,
            expected_decision_status=status,
            location_name="Khanna Grain Mandi (Synthetic)",
            commodity_name="Wheat (Common Foodgrain)",
            baseline_window="2026-09-01 to 2026-09-30 (30 days)",
            anomaly_window="2026-10-01 to 2026-10-15 (15 days)" if inject_anomaly else None,
            observations=observations,
        )

    def generate_scenario_c(self) -> ScenarioDetail:
        """Scenario C — Price-Only Spike: substantial price deviation without arrival collapse."""
        rng = random.Random(self.SEED + 103)
        start_d = date(2026, 9, 1)
        dates = self._generate_dates(start_d, 45)

        base_price = 2125.0
        base_arrival = 2500.0

        observations: List[ObservationPoint] = []
        for i, d in enumerate(dates):
            if i < 30:
                p_noise = rng.gauss(0, 25.0)
                a_noise = rng.gauss(0, 100.0)
                observations.append(
                    ObservationPoint(
                        date=d,
                        modal_price=round(base_price + p_noise, 1),
                        arrival_quantity=round(base_arrival + a_noise, 1),
                        is_anomaly_candidate=False,
                    )
                )
            else:
                # Price spikes +42%, but arrivals remain completely normal
                p_spike = base_price * 1.42 + rng.gauss(0, 35.0)
                a_normal = base_arrival + rng.gauss(0, 90.0)
                observations.append(
                    ObservationPoint(
                        date=d,
                        modal_price=round(p_spike, 1),
                        arrival_quantity=round(a_normal, 1),
                        is_anomaly_candidate=True,
                        notes="Isolated price spike. Arrival volume remains within historical median.",
                    )
                )

        return ScenarioDetail(
            scenario_id="scenario_c_price_spike_only",
            title="Scenario C: Isolated Price Spike",
            description="Substantial price deviation (+42%) while arrival flows remain completely normal. Yields a PRICE_SIGNAL, not convergent supply anomaly.",
            expected_decision_status=DecisionStatus.PRICE_SIGNAL,
            location_name="Jalandhar Mandi (Synthetic)",
            commodity_name="Wheat (Common Foodgrain)",
            baseline_window="2026-09-01 to 2026-09-30 (30 days)",
            anomaly_window="2026-10-01 to 2026-10-15 (15 days)",
            observations=observations,
        )

    def generate_scenario_d(self) -> ScenarioDetail:
        """Scenario D — Arrival-Only Decline: substantial arrivals collapse without price signal."""
        rng = random.Random(self.SEED + 104)
        start_d = date(2026, 9, 1)
        dates = self._generate_dates(start_d, 45)

        base_price = 2125.0
        base_arrival = 2500.0

        observations: List[ObservationPoint] = []
        for i, d in enumerate(dates):
            if i < 30:
                p_noise = rng.gauss(0, 25.0)
                a_noise = rng.gauss(0, 100.0)
                observations.append(
                    ObservationPoint(
                        date=d,
                        modal_price=round(base_price + p_noise, 1),
                        arrival_quantity=round(base_arrival + a_noise, 1),
                        is_anomaly_candidate=False,
                    )
                )
            else:
                # Price remains normal, but arrivals drop -58%
                p_normal = base_price + rng.gauss(0, 25.0)
                a_drop = base_arrival * 0.42 + rng.gauss(0, 40.0)
                observations.append(
                    ObservationPoint(
                        date=d,
                        modal_price=round(p_normal, 1),
                        arrival_quantity=round(a_drop, 1),
                        is_anomaly_candidate=True,
                        notes="Isolated arrival decline. Price quotes remain near MSP baseline.",
                    )
                )

        return ScenarioDetail(
            scenario_id="scenario_d_arrival_drop_only",
            title="Scenario D: Isolated Arrival Decline",
            description="Severe arrival contraction (-58%) without a corroborating price reaction. Yields an ARRIVAL_SIGNAL, not convergent supply anomaly.",
            expected_decision_status=DecisionStatus.ARRIVAL_SIGNAL,
            location_name="Bathinda Mandi (Synthetic)",
            commodity_name="Wheat (Common Foodgrain)",
            baseline_window="2026-09-01 to 2026-09-30 (30 days)",
            anomaly_window="2026-10-01 to 2026-10-15 (15 days)",
            observations=observations,
        )

    def generate_scenario_e(self) -> ScenarioDetail:
        """Scenario E — Insufficient / Corrupted Evidence: truncated history and null values."""
        start_d = date(2026, 10, 1)
        dates = self._generate_dates(start_d, 8) # Only 8 days! (below 14-day threshold)

        observations: List[ObservationPoint] = [
            ObservationPoint(date=dates[0], modal_price=2150.0, arrival_quantity=None, notes="Missing arrival"),
            ObservationPoint(date=dates[1], modal_price=2180.0, arrival_quantity=2400.0),
            ObservationPoint(date=dates[2], modal_price=None, arrival_quantity=2350.0, notes="Missing price"),
            ObservationPoint(date=dates[3], modal_price=2200.0, arrival_quantity=2300.0),
            ObservationPoint(date=dates[4], modal_price=2220.0, arrival_quantity=None),
            ObservationPoint(date=dates[5], modal_price=2250.0, arrival_quantity=2100.0),
            ObservationPoint(date=dates[6], modal_price=2300.0, arrival_quantity=2000.0),
            ObservationPoint(date=dates[7], modal_price=2400.0, arrival_quantity=1800.0),
        ]

        return ScenarioDetail(
            scenario_id="scenario_e_insufficient_evidence",
            title="Scenario E: Insufficient / Corrupted Evidence",
            description="Truncated 8-day history with multiple null cells, failing minimum 14-day baseline requirement. Yields INSUFFICIENT_DATA.",
            expected_decision_status=DecisionStatus.INSUFFICIENT_DATA,
            location_name="Moga Outpost (Synthetic)",
            commodity_name="Wheat (Common Foodgrain)",
            baseline_window="2026-10-01 to 2026-10-08 (8 days - INSUFFICIENT)",
            anomaly_window=None,
            observations=observations,
        )

    def get_all_scenarios(self) -> Dict[str, ScenarioDetail]:
        """Returns all canonical synthetic scenarios keyed by scenario_id."""
        return {
            "scenario_a_normal_baseline": self.generate_scenario_a(),
            "scenario_b_convergent_anomaly": self.generate_scenario_b(inject_anomaly=True),
            "scenario_c_price_spike_only": self.generate_scenario_c(),
            "scenario_d_arrival_drop_only": self.generate_scenario_d(),
            "scenario_e_insufficient_evidence": self.generate_scenario_e(),
        }

    def get_scenario_summaries(self) -> List[ScenarioSummary]:
        """Returns lightweight metadata summaries for scenario selection."""
        scenarios = self.get_all_scenarios()
        return [
            ScenarioSummary(
                scenario_id=s.scenario_id,
                title=s.title,
                description=s.description,
                expected_decision_status=s.expected_decision_status,
                location_name=s.location_name,
                commodity_name=s.commodity_name,
                total_observation_days=len(s.observations),
                is_synthetic=True,
                data_mode="SYNTHETIC_DEMO",
            )
            for s in scenarios.values()
        ]

    def export_all_to_disk(self) -> int:
        """Persists all scenarios to JSON fixtures in data/synthetic/scenarios/."""
        scenarios = self.get_all_scenarios()
        count = 0
        for sid, detail in scenarios.items():
            fpath = self.output_dir / f"{sid}.json"
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(detail.model_dump(), f, indent=2)
            count += 1
        return count
