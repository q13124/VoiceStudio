from pydantic import BaseModel, ConfigDict

class StrictModel(BaseModel):
    """
    Project-wide base for public API models.
    - strict typing
    - forbid unknown fields
    - emit JSON Schema 2020-12 (OpenAPI 3.1)
    """
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        ser_json_schema="json-schema-2020-12",
    )
