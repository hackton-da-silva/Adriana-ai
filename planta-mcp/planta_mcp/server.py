"""Servidores MCP de leitura da planta LTQ simulada."""
from __future__ import annotations

import argparse
import hmac
import os
from functools import lru_cache
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from . import clp, consultas, documentacao
from .sim import Planta

telemetria = FastMCP("TelemetriaCLPLTQ", stateless_http=True, json_response=True, instructions="Leituras e alarmes simulados da planta de demonstração.")
documentos = FastMCP("DocumentacaoPlantaLTQ", stateless_http=True, json_response=True, instructions="Documentação do CLP e dos equipamentos da planta simulada.")
planta = lru_cache(maxsize=1)(Planta)


@telemetria.tool()
def status_clp(equipamento_id: str | None = None) -> dict:
    """Lista os alarmes ativos da planta simulada. Passe o equipamento para ver códigos, tags e início."""
    return clp.status_clp(planta(), equipamento_id)


@telemetria.tool()
def status_maquina(equipamento_id: str) -> dict:
    """Leituras atuais de um equipamento da simulação, com identificadores de variáveis, unidades e faixas."""
    return consultas.status_maquina(planta(), equipamento_id)


@telemetria.tool()
def historico(equipamento_id: str, variavel: str, minutos: Annotated[int, Field(ge=1, le=480)] = 60) -> dict:
    """Histórico de uma variável simulada. Use o identificador de variável de status_maquina, por exemplo vibracao."""
    return consultas.historico(planta(), equipamento_id, variavel, minutos)


@documentos.tool()
def consultar_documentacao_equipamento_ltq(equipamento_id: str, codigo: str | None = None,
                                            tag: str | None = None, texto: str | None = None) -> dict:
    """Consulta o manual de um equipamento identificado, como F5, por código, tag ou descrição do sintoma."""
    if not equipamento_id.strip():
        raise ValueError("Informe o equipamento da planta.")
    return documentacao.buscar(equipamento_id, codigo, tag, texto)


@documentos.tool()
def consultar_manual_clp(codigo: str | None = None) -> dict:
    """Consulta a convenção geral do CLP simulado: códigos, bits e sinalização comuns aos equipamentos."""
    return documentacao.buscar(codigo=codigo)


class _BearerAuth:
    """Protege todas as chamadas HTTP, inclusive descoberta das ferramentas."""

    def __init__(self, app, token: str):
        self.app = app
        self.authorization = ("Bearer " + token).encode()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            supplied = dict(scope["headers"]).get(b"authorization", b"")
            if not hmac.compare_digest(supplied, self.authorization):
                await send({"type": "http.response.start", "status": 401,
                            "headers": [(b"www-authenticate", b"Bearer")]})
                await send({"type": "http.response.body", "body": b""})
                return
        await self.app(scope, receive, send)


def main() -> None:
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("servico", choices=["telemetria", "documentacao"])
    args = parser.parse_args()
    token = os.environ.get("PLANTA_MCP_TOKEN")
    if not token:
        parser.error("configure PLANTA_MCP_TOKEN")
    if args.servico == "telemetria":
        planta()
        servidor, porta = telemetria, 8011
    else:
        servidor, porta = documentos, 8012
    app = servidor.streamable_http_app()
    uvicorn.run(_BearerAuth(app, token), host="127.0.0.1", port=porta)
