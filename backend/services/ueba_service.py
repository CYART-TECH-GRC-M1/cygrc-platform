"""Statistical-Threshold User & Entity Behavior Analytics (UEBA) Service.

Implements MVP statistical baseline profiling:
- Computes mean, variance, and standard deviation over historical baseline windows.
- Calculates dynamic statistical threshold: mean + (k * std_dev).
- Handles sparse data and missing features explicitly (rejects false positives when N < 5).
- Produces traceable anomaly reports with baseline window, threshold, observed value, and rationale.
"""
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple


class UEBAEngine:
    MIN_OBSERVATIONS_REQUIRED = 5
    DEFAULT_SIGMA_MULTIPLIER = 2.0  # 2-sigma threshold (~95% confidence interval)

    SUPPORTED_FEATURES = {
        "failed_logins": {"min_floor": 3.0, "unit": "attempts"},
        "data_transfer_mb": {"min_floor": 50.0, "unit": "MB"},
        "off_hours_events": {"min_floor": 2.0, "unit": "events"},
        "api_call_rate": {"min_floor": 60.0, "unit": "calls/min"},
    }

    @classmethod
    def calculate_baseline(cls, historical_values: List[float]) -> Tuple[float, float]:
        """Calculates arithmetic mean and sample standard deviation."""
        n = len(historical_values)
        if n == 0:
            return 0.0, 0.0
        mean = sum(historical_values) / n
        if n < 2:
            return mean, 0.0
        variance = sum((x - mean) ** 2 for x in historical_values) / (n - 1)
        std_dev = math.sqrt(variance)
        return mean, std_dev

    @classmethod
    def analyze_event_anomaly(
        cls,
        entity_id: str,
        feature_name: str,
        observed_value: float,
        historical_baseline: List[float],
        baseline_window: str = "7d",
        k_sigma: float = DEFAULT_SIGMA_MULTIPLIER,
    ) -> Dict[str, Any]:
        """
        Evaluates an observed metric against the entity's statistical baseline.
        Explicitly handles sparse data to prevent arbitrary false anomaly labeling.
        """
        now_ts = datetime.now(timezone.utc).isoformat()
        feature_meta = cls.SUPPORTED_FEATURES.get(feature_name, {"min_floor": 5.0, "unit": "units"})
        min_floor = feature_meta["min_floor"]
        unit = feature_meta["unit"]

        # Check for sparse data
        if len(historical_baseline) < cls.MIN_OBSERVATIONS_REQUIRED:
            return {
                "status": "INSUFFICIENT_BASELINE_DATA",
                "entity_id": entity_id,
                "feature": feature_name,
                "observed_value": observed_value,
                "observations_count": len(historical_baseline),
                "min_observations_required": cls.MIN_OBSERVATIONS_REQUIRED,
                "is_anomaly": False,
                "anomaly_score": 0,
                "reason": (
                    f"Sparse data: {len(historical_baseline)} observation(s) recorded in {baseline_window}. "
                    f"Minimum {cls.MIN_OBSERVATIONS_REQUIRED} required to establish statistically reliable baseline."
                ),
                "timestamp": now_ts,
            }

        mean, std_dev = cls.calculate_baseline(historical_baseline)
        statistical_threshold = mean + (k_sigma * std_dev)
        # Apply minimum floor threshold to avoid alerting on near-zero baseline fluctuations
        effective_threshold = max(statistical_threshold, min_floor)

        is_anomaly = observed_value > effective_threshold

        if is_anomaly:
            ratio = observed_value / max(1.0, effective_threshold)
            anomaly_score = min(100, int(50 + (ratio - 1.0) * 25))
            reason = (
                f"Statistical anomaly detected for {entity_id}: observed {feature_name} of "
                f"{observed_value:.1f} {unit} exceeds {baseline_window} baseline threshold of "
                f"{effective_threshold:.1f} {unit} (mean: {mean:.1f}, std: {std_dev:.1f}, k: {k_sigma})."
            )
        else:
            anomaly_score = 0
            reason = f"Normal behavior: observed value {observed_value:.1f} {unit} is within threshold {effective_threshold:.1f} {unit}."

        return {
            "status": "EVALUATED",
            "entity_id": entity_id,
            "feature": feature_name,
            "baseline_window": baseline_window,
            "observations_count": len(historical_baseline),
            "baseline_mean": round(mean, 2),
            "baseline_std": round(std_dev, 2),
            "threshold_value": round(effective_threshold, 2),
            "observed_value": round(observed_value, 2),
            "anomaly_score": anomaly_score,
            "is_anomaly": is_anomaly,
            "reason": reason,
            "timestamp": now_ts,
        }
