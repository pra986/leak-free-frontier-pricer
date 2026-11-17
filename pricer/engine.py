"""Core engine for leak-free product-family group splitting and stratified evaluation."""

import hashlib
import re
from typing import Dict, Iterable, List, Sequence, Tuple

from pricer.models import EvaluationReport, PriceBandMetric, ProductRecord, SplitSummary

PRICE_LEAK_PATTERN = re.compile(r"(\$?\d+(?:\.\d{1,2})?)")


class FrontierPricerEngine:
    """Pipeline engine enforcing group-level splits, leakage guards, and band stratification."""

    def __init__(self, bands: Sequence[Tuple[str, float, float]] | None = None) -> None:
        self.bands = list(bands) if bands else [
            ("budget (<$50)", 0.0, 50.0),
            ("mid ($50-$200)", 50.0, 200.0),
            ("premium (>=$200)", 200.0, float("inf")),
        ]

    def group_split(
        self,
        records: Iterable[ProductRecord],
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
    ) -> Tuple[List[ProductRecord], List[ProductRecord], List[ProductRecord], SplitSummary]:
        """Deterministically split records by family_id so no product family spans splits."""
        train, val, test = [], [], []
        families: Dict[str, str] = {}

        for record in records:
            if record.family_id not in families:
                digest = hashlib.sha256(record.family_id.encode("utf-8")).hexdigest()
                bucket = int(digest[:8], 16) / 0xFFFFFFFF
                if bucket < train_ratio:
                    families[record.family_id] = "train"
                elif bucket < train_ratio + val_ratio:
                    families[record.family_id] = "val"
                else:
                    families[record.family_id] = "test"

            target = families[record.family_id]
            if target == "train":
                train.append(record)
            elif target == "val":
                val.append(record)
            else:
                test.append(record)

        summary = SplitSummary(
            train_count=len(train),
            val_count=len(val),
            test_count=len(test),
            unique_families=len(families),
            leakage_detected=self.has_family_overlap(train, val, test),
        )
        return train, val, test, summary

    @staticmethod
    def has_family_overlap(
        train: Sequence[ProductRecord],
        val: Sequence[ProductRecord],
        test: Sequence[ProductRecord],
    ) -> bool:
        """Return True if any family_id appears in more than one split."""
        f_train = {r.family_id for r in train}
        f_val = {r.family_id for r in val}
        f_test = {r.family_id for r in test}
        return bool((f_train & f_val) or (f_train & f_test) or (f_val & f_test))

    @staticmethod
    def build_leak_free_prompt(record: ProductRecord) -> str:
        """Format a fine-tuning prompt and verify the ground-truth price is absent."""
        clean_desc = record.description.replace(f"${record.price_usd:.2f}", "[REDACTED]")
        clean_desc = clean_desc.replace(f"{record.price_usd:.2f}", "[REDACTED]")
        prompt = (
            f"Estimate the retail price in USD for the following product.\n"
            f"Category: {record.category}\n"
            f"Title: {record.title}\n"
            f"Details: {clean_desc}"
        )
        if f"{record.price_usd:.2f}" in prompt:
            raise ValueError(f"Price leakage detected for SKU {record.sku}")
        return prompt

    def evaluate_by_band(
        self,
        actuals: Sequence[float],
        predictions: Sequence[float],
    ) -> EvaluationReport:
        """Compute overall and price-band stratified MAE and MAPE."""
        if len(actuals) != len(predictions) or not actuals:
            raise ValueError("Actuals and predictions must be non-empty and equal length.")

        total_abs = sum(abs(a - p) for a, p in zip(actuals, predictions))
        total_pct = sum(abs(a - p) / max(a, 1e-6) * 100.0 for a, p in zip(actuals, predictions))

        band_metrics: List[PriceBandMetric] = []
        for label, low, high in self.bands:
            pairs = [(a, p) for a, p in zip(actuals, predictions) if low <= a < high]
            if not pairs:
                continue
            mae = sum(abs(a - p) for a, p in pairs) / len(pairs)
            mape = sum(abs(a - p) / max(a, 1e-6) * 100.0 for a, p in pairs) / len(pairs)
            band_metrics.append(
                PriceBandMetric(
                    band_label=label,
                    sample_count=len(pairs),
                    mae_usd=round(mae, 4),
                    mape_pct=round(mape, 2),
                )
            )

        return EvaluationReport(
            overall_mae_usd=round(total_abs / len(actuals), 4),
            overall_mape_pct=round(total_pct / len(actuals), 2),
            bands=band_metrics,
        )
