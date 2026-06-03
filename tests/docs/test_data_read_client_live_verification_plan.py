from pathlib import Path


def test_data_read_client_live_verification_plan_covers_openapi_and_safety() -> None:
    text = Path("docs/data_read_client_live_verification_plan.md").read_text(encoding="utf-8")
    required_phrases = [
        "AI_MARKET_MACHINE_DATA_BASE_URL",
        "OPS_INTERNAL_TOKEN",
        "X-Ops-Internal-Token",
        "OpenAPI",
        "/openapi.json",
        "certified OHLCV",
        "historical_ohlcv",
        "401",
        "403",
        "404",
        "500",
        "no DB writes",
        "no vendor calls",
        "no scheduler activation",
        "no AI Machine changes",
        "human approval",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"
