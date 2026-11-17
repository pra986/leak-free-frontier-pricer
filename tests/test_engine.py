from pricer.engine import FrontierPricerEngine
from pricer.models import ProductRecord


def _sample_records() -> list[ProductRecord]:
    return [
        ProductRecord("SKU-1", "FAM-A", "Item A1", "Costs $25.00 retail", "Cat1", 25.0),
        ProductRecord("SKU-2", "FAM-A", "Item A2", "Variant USD 25.00", "Cat1", 25.0),
        ProductRecord("SKU-3", "FAM-B", "Item B1", "Midrange $110.00 unit", "Cat2", 110.0),
        ProductRecord("SKU-4", "FAM-C", "Item C1", "Pro $299.00 flagship", "Cat3", 299.0),
        ProductRecord("SKU-5", "FAM-D", "Item D1", "Budget $15.00 pack", "Cat1", 15.0),
    ]


def test_split_by_family_has_no_overlap() -> None:
    engine = FrontierPricerEngine()
    records = _sample_records()
    train, val, test = engine.split_by_family(records, seed=42)
    assert len(train) + len(val) + len(test) == len(records)
    assert engine.has_family_overlap(train, val, test) is False


def test_has_family_overlap_detects_leak() -> None:
    engine = FrontierPricerEngine()
    r1 = ProductRecord("SKU-1", "FAM-X", "Title", "Desc", "Cat", 10.0)
    r2 = ProductRecord("SKU-2", "FAM-X", "Title 2", "Desc 2", "Cat", 12.0)
    assert engine.has_family_overlap([r1], [r2], []) is True


def test_build_leak_free_prompt_scrubs_prices() -> None:
    engine = FrontierPricerEngine()
    rec = ProductRecord("SKU-1", "FAM-A", "Earbuds", "MSRP $49.99 USD", "Audio", 49.99)
    prompt = engine.build_leak_free_prompt(rec)
    assert "49.99" not in prompt
    assert "Earbuds" in prompt
    assert "Audio" in prompt


def test_evaluate_by_band_metrics() -> None:
    engine = FrontierPricerEngine()
    actuals = [20.0, 100.0, 300.0]
    preds = [25.0, 90.0, 330.0]
    metrics = engine.evaluate_by_band(actuals, preds)
    assert metrics["<50"]["count"] == 1
    assert metrics["<50"]["mae"] == 5.0
    assert metrics["50-200"]["mae"] == 10.0
    assert metrics["200+"]["mae"] == 30.0
