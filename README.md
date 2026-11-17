# Leak-Free Frontier Pricer (K6)

Product pricing with frontier models featuring product-family group splits, zero test-price leakage guards, JSONL schema validation, and price-band evaluation.

## Architecture
- **Product-Family Group Split**: Ensures variants of the same product family never span train and test splits.
- **Zero Test-Price Leakage Guard**: Validates prompt serialization and feature pipelines to guarantee target prices are stripped prior to inference.
- **JSONL Schema Validator**: Enforces strict input/output JSONL contracts for fine-tuning and batch evaluation.
- **Price-Band Evaluation**: Reports MAE, RMSLE, and accuracy stratified across low, mid, and high price bands.
