"""Verifica o contrato MCP dos dois endpoints sem abrir portas nem iniciar o Agora."""
import json
import unittest

import httpx

from planta_mcp.server import _BearerAuth, documentos, telemetria


class PlantContracts(unittest.IsolatedAsyncioTestCase):
    async def check_endpoint(self, server, tools, calls):
        app = server.streamable_http_app()
        transport = httpx.ASGITransport(app=_BearerAuth(app, "teste"))
        async with app.router.lifespan_context(app), httpx.AsyncClient(
            transport=transport, base_url="http://127.0.0.1:8011",
            headers={"Accept": "application/json, text/event-stream"},
        ) as client:
            async def rpc(method, params):
                return await client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params})

            self.assertEqual((await rpc("tools/list", {})).status_code, 401)
            client.headers["Authorization"] = "Bearer teste"
            initialized = await rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                                   "clientInfo": {"name": "teste", "version": "1"}})
            self.assertEqual(initialized.json()["result"]["serverInfo"]["name"], server.name)
            listed = await rpc("tools/list", {})
            self.assertEqual({t["name"] for t in listed.json()["result"]["tools"]}, tools)
            for name, arguments, expected in calls:
                response = await rpc("tools/call", {"name": name, "arguments": arguments})
                result = response.json()["result"]
                self.assertFalse(result.get("isError"), result)
                self.assertIn(expected, json.loads(result["content"][0]["text"]))

    async def test_telemetria(self):
        await self.check_endpoint(telemetria, {"status_clp", "status_maquina", "historico"}, [
            ("status_clp", {"equipamento_id": "F5"}, "alarmes"),
            ("status_maquina", {"equipamento_id": "F5"}, "variaveis"),
            ("historico", {"equipamento_id": "F5", "variavel": "vibracao"}, "estatisticas"),
        ])

    async def test_documentacao(self):
        await self.check_endpoint(documentos, {"consultar_documentacao_equipamento_ltq", "consultar_manual_clp"}, [
            ("consultar_documentacao_equipamento_ltq", {"equipamento_id": "F5", "tag": "AI012"}, "tag"),
            ("consultar_documentacao_equipamento_ltq", {"equipamento_id": "F5", "texto": "vibrando"}, "referencia_tecnica"),
            ("consultar_manual_clp", {"codigo": "0602"}, "codigo"),
        ])
