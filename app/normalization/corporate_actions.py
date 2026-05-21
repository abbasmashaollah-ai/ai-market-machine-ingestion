from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CorporateActionPayload:
    """Placeholder structure for future corporate action normalization."""

    raw: dict[str, object]


def normalize_corporate_actions(*_args: object, **_kwargs: object) -> None:
    raise NotImplementedError("Corporate action normalization is not implemented yet.")
