from typing import Dict, Any, Set

def assert_zero_price_leakage(prompt_payload: Dict[str, Any], forbidden_keys: Set[str] = {"price", "target_price"}) -> None:
    leaked = [k for k in prompt_payload if k.lower() in forbidden_keys]
    if leaked:
        raise ValueError(f"Test-price leakage detected in keys: {leaked}")
