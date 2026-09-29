from typing import Any

import httpx

from julee_ceap.domain.models.schema import JsonSchema
from julee_ceap.domain.oracles.schema import SchemaOracle


class HttpSchemaOracle(SchemaOracle):
    async def fetch(self, url: str) -> JsonSchema:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            schema: dict[str, Any] = response.json()
            return JsonSchema(schema)
