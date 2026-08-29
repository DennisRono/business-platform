"""Shared Pydantic custom types used across the project's schemas.

Why LooseEmail?
---------------
Pydantic's ``EmailStr`` (backed by ``email-validator``) enforces RFC-5321
deliverability rules, including requiring a TLD-qualified domain.  The
OpenAPI ``format: email`` specification only requires the structural
``<local-part>@<domain>`` form.  Schemathesis generates structurally valid
addresses such as ``__main__@dev`` or ``user@localhost`` that satisfy the
schema but are rejected by ``EmailStr``.

``LooseEmail`` accepts any string that matches ``^[^@\\s]+@[^@\\s]+$`` —
the same constraint implied by ``format: email`` in JSON Schema — so the
server's validation is in alignment with the documented OpenAPI contract.

The ``WithJsonSchema`` annotation ensures FastAPI emits ``{"type": "string",
"format": "email"}`` in the generated OpenAPI spec so Schemathesis and other
tooling continue to generate valid email-shaped test strings.
"""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator
from pydantic.json_schema import WithJsonSchema

_LOOSE_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+$")


def _validate_loose_email(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Email must be a string.")
    if not _LOOSE_EMAIL_RE.match(value):
        raise ValueError(
            f"{value!r} is not a valid email address. "
            "Expected format: <local-part>@<domain>"
        )
    return value.lower()


# Drop-in replacement for EmailStr that matches format: email in JSON Schema.
# WithJsonSchema ensures FastAPI emits {"type": "string", "format": "email"}
# in the generated OpenAPI document.
LooseEmail = Annotated[
    str,
    AfterValidator(_validate_loose_email),
    WithJsonSchema({"type": "string", "format": "email"}),
]
