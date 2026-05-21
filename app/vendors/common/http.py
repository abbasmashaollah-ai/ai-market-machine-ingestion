from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from json import JSONDecodeError
from typing import Any, Protocol
from urllib import parse, request
from urllib.error import HTTPError, URLError

from app.vendors.common.errors import (
    InvalidVendorResponseError,
    VendorHttpStatusError,
    VendorTimeoutError,
    VendorUnavailableError,
)


@dataclass(frozen=True)
class RequestMetadata:
    method: str
    url: str
    timeout_seconds: float
    headers: dict[str, str] = field(default_factory=dict)
    query_params: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ResponseMetadata:
    status_code: int
    elapsed_seconds: float
    headers: dict[str, str] = field(default_factory=dict)
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class HttpResponse:
    metadata: ResponseMetadata
    text: str
    json: Any | None = None

    @property
    def status_code(self) -> int:
        return self.metadata.status_code

    @property
    def raw_text_length(self) -> int:
        return len(self.text)

    @property
    def parsed_json(self) -> Any | None:
        return self.json


class HttpClient(Protocol):
    def request(self, metadata: RequestMetadata) -> HttpResponse:
        ...


class UrlLibHttpClient:
    def request(self, metadata: RequestMetadata) -> HttpResponse:
        url = self._build_url(metadata.url, metadata.query_params)
        req = request.Request(url=url, method=metadata.method.upper(), headers=metadata.headers)
        started_at = datetime.now(timezone.utc)
        try:
            response = request.urlopen(req, timeout=metadata.timeout_seconds)
            return self._build_response(response, started_at)
        except TimeoutError as exc:
            raise VendorTimeoutError(str(exc) or "request timed out") from exc
        except HTTPError as exc:
            raise VendorHttpStatusError(f"unexpected http status: {exc.code}") from exc
        except URLError as exc:
            raise VendorUnavailableError(str(exc.reason) or "vendor unavailable") from exc
        except OSError as exc:
            raise VendorUnavailableError(str(exc) or "vendor unavailable") from exc

    def _build_url(self, url: str, query_params: dict[str, str]) -> str:
        if not query_params:
            return url
        parsed = parse.urlsplit(url)
        existing = parse.parse_qsl(parsed.query, keep_blank_values=True)
        merged = existing + list(query_params.items())
        encoded_query = parse.urlencode(merged)
        return parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, encoded_query, parsed.fragment))

    def _build_response(self, response: Any, started_at: datetime) -> HttpResponse:
        raw = response.read()
        text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
        headers = dict(getattr(response, "headers", {}) or {})
        status_code = int(getattr(response, "status", 200))
        elapsed_seconds = max((datetime.now(timezone.utc) - started_at).total_seconds(), 0.0)
        metadata = ResponseMetadata(
            status_code=status_code,
            elapsed_seconds=elapsed_seconds,
            headers=headers,
        )
        parsed_json = self._try_parse_json(text)
        return HttpResponse(metadata=metadata, text=text, json=parsed_json)

    def _try_parse_json(self, text: str) -> Any | None:
        try:
            from json import loads

            return loads(text)
        except JSONDecodeError:
            return None


def build_request_metadata(
    url: str,
    *,
    timeout_seconds: float,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    query_params: dict[str, str] | None = None,
) -> RequestMetadata:
    return RequestMetadata(
        method=method,
        url=url,
        timeout_seconds=timeout_seconds,
        headers=headers or {},
        query_params=query_params or {},
    )
