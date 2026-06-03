import json

from app.features.breadth.breadth_builder import build_breadth_observation
from app.features.breadth.breadth_report import build_breadth_report
from app.features.breadth.breadth_writer import BreadthMockWriter, write_breadth_payloads
from tests.fixtures.breadth_ohlcv import build_breadth_ohlcv_fixtures


def test_report_is_json_friendly_and_includes_writer_counts() -> None:
    fixtures = build_breadth_ohlcv_fixtures()
    volume_histories = {symbol: [{"volume": row["volume"]} for row in history] for symbol, history in fixtures.items()}
    observation = build_breadth_observation("SP500", fixtures, volume_histories, "2026-01-15")
    writer = BreadthMockWriter()
    writer_result = write_breadth_payloads([observation], writer=writer)

    report = build_breadth_report(observation, writer_result=writer_result)

    assert report["accepted_count"] == 1
    assert report["rejected_count"] == 0
    assert report["no_db_writes"] is True
    assert report["no_vendor_calls"] is True
    assert report["no_scheduler_activation"] is True
    json.dumps(report)
