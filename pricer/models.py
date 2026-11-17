"""Data models for leak-free frontier pricing."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class ProductRecord:
    """Normalized product listing for group-split fine-tuning."""

    sku: str
    family_id: str
    title: str
    description: str
    category: str
    price_usd: float


@dataclass(frozen=True)
class SplitSummary:
    """Summary of train/validation/test product-family group split."""

    train_count: int
    val_count: int
    test_count: int
    unique_families: int
    leakage_detected: bool


@dataclass(frozen=True)
class PriceBandMetric:
    """Stratified error metrics for a specific price band."""

    band_label: str
    sample_count: int
    mae_usd: float
    mape_pct: float


@dataclass
class EvaluationReport:
    """Overall evaluation report across price bands."""

    overall_mae_usd: float
    overall_mape_pct: float
    bands: List[PriceBandMetric] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
