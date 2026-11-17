# Leak-Free Frontier Pricer (Project 06)

Product-family group-split frontier fine-tuning pipeline with zero test-price prompt leakage and price-band error stratification.

## Architecture

- **Product-Family Group Split**: Deterministically partitions catalog records by `family_id` so product variants never span train, validation, and test splits.
- **Zero Test-Price Leakage Guard**: Sanitizes descriptions and validates serialized prompts to guarantee target prices are stripped prior to training or inference.
- **JSONL Schema Validator**: Enforces strict input/output JSONL contracts for frontier fine-tuning jobs and batch evaluation.
- **Price-Band Evaluation**: Reports MAE and MAPE stratified across budget (`<$50`), mid (`$50-$200`), and premium (`>=$200`) price bands.

## 6-Stage Workflow

1. **Ingest & Normalize**: Load raw product records into `ProductRecord` schema (`sku`, `family_id`, `title`, `description`, `category`, `price_usd`).
2. **Product-Family Group Split**: Partition records via deterministic SHA-256 hashing on `family_id` into 70% train / 15% val / 15% test.
3. **Overlap Verification**: Assert zero `family_id` intersection across splits (`SplitSummary.leakage_detected == False`).
4. **Leak-Free Prompt Serialization**: Redact embedded price tokens and verify target `price_usd` is absent from every prompt.
5. **Frontier Fine-Tuning & Inference**: Export validated JSONL payloads for frontier model fine-tuning and batch prediction.
6. **Stratified Band Evaluation**: Compute overall and per-band MAE/MAPE via `FrontierPricerEngine.evaluate_by_band`.

## Data Contract

- **Input Record**: `sku` (str), `family_id` (str), `title` (str), `description` (str), `category` (str), `price_usd` (float > 0).
- **Evaluation Artifact**: `evaluation/eval_cases.json` containing representative multi-family `records` and expected price bands.

## Production Controls

- Automated CI (`pytest`) on every push and pull request.
- Hard failure (`ValueError`) on any detected prompt price leakage.
- Deterministic hashing for reproducible group splits across environments.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
python -m pricer.cli --eval-file evaluation/eval_cases.json
```

## Attribution

Adapted and productionized from [ed-donner/llm_engineering](https://github.com/ed-donner/llm_engineering) (`week6`).
