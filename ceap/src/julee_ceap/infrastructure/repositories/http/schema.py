from typing import Any

import httpx

from julee_ceap.domain.oracles.schema import SchemaOracle
from julee_ceap.domain.values.schema import JsonSchema


class HttpSchemaOracle(SchemaOracle):
    async def fetch(self, url: str) -> JsonSchema:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            schema: dict[str, Any] = response.json()
            return JsonSchema(schema)
