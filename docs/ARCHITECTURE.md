# Architecture — Leak-Free Frontier Pricer (Project 06)

## Overview
`leak-free-frontier-pricer` is a product-family group-split frontier fine-tuning pipeline designed to eliminate test-price prompt leakage and evaluate predictions across stratified price bands.

## Core Modules
- `pricer/models.py`: Defines `ProductRecord` (`sku`, `family_id`, `title`, `description`, `category`, `price_usd`).
- `pricer/guard.py`: Implements `PromptLeakageGuard` with regex-based currency/price pattern scrubbing (`scrub`) and leakage detection (`contains_price_leak`).
- `pricer/engine.py`: Implements `FrontierPricerEngine`:
  - `split_by_family`: Deterministically partitions `ProductRecord` items into `train`, `val`, and `test` splits grouped by `family_id` so variants never cross split boundaries.
  - `has_family_overlap`: Verifies zero `family_id` overlap across `train`, `val`, and `test`.
  - `build_leak_free_prompt`: Formats title, category, and scrubbed description into a zero-leakage prompt.
  - `evaluate_by_band`: Computes MAE and RMSE stratified across `<50`, `50-200`, and `200+` USD bands.
- `pricer/cli.py`: Command-line entrypoint for running splits, leakage checks, and price-band evaluation.
