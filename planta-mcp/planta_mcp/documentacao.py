"""Documentação consultável pelo agente: manual do CLP padrão e manual de falhas de cada máquina.

Tudo é gerado a partir do catálogo e dos modos de falha da especificação, para não divergir dos dados.
Exporta Markdown com:  python -m planta_mcp.documentacao  (grava em planta-mcp/docs/).
"""

from __future__ import annotations

import re
from pathlib import Path

from . import busca
from . import catalogo as cat
from . import clp
from .desvios import causa_acao

EFEITO_JUSANTE = {
    "forno_viga_caminhante": "Placa fria: força e torque do R1 +15–25 %, FDT baixa, risco de cobble. Skid mark: variação de "
                             "espessura e de força no acabador. Falha da água dos skids: parada de emergência.",
    "descarepador": "Carepa residual ou incrustada na tira; no acabador, mais desgaste dos cilindros F1–F2 e defeitos de carepa.",
    "desbastador": "Placa fria: risco de trip do motor. Camber: o esboço bate nas guias. Desgaste: força sobe lentamente.",
    "coil_box": "Falha de transferência ou esboço telescopado: parada da linha e sucata do esboço.",
    "tesoura": "Corte rasgado ou fora de posição: desponte longo, menor rendimento metálico.",
    "cadeira_acabadora": "Cobble: parada de 1–4 h, sucata, dano em cilindros e guias. Chatter: marcas na tira e risco de "
                         "ruptura. Looper instável: variação de largura, precursor de cobble. Fim de campanha: troca antecipada.",
    "medidores": "Medidor descalibrado faz o AGC corrigir errado (deriva de 10–30 µm por semana sem mudança de força ou gap).",
    "mesa_resfriamento": "CT fora do alvo: propriedades mecânicas fora da especificação, bobina desclassificada.",
    "bobinadeira": "Bobina telescopada, marcas de wrapper, ovalização; cobble na entrada com ~4 h de parada.",
}

MANUTENCAO = {
    "forno_viga_caminhante": "Turno: queimadores e analisadores O₂/CO. Semanal: termografia da carcaça. Mensal: curvas ar/gás "
                             "e termopares. Paradas: skids, refratário, recuperador e data logger para validar o nível 2.",
    "descarepador": "Inspeção de bicos e filtros; pré-carga do acumulador; manutenção preventiva das bombas.",
    "desbastador": "Cilindros de trabalho a cada 3–7 dias (30–60 min); encosto a cada 3–6 semanas; edger a cada 1–2 semanas.",
    "coil_box": "Inspeção do mandril e do sistema de transferência.",
    "tesoura": "Trocar ou girar as facas a cada 2–6 semanas.",
    "cadeira_acabadora": "Cilindros de trabalho a cada 4–8 h ou na transição largo → estreito (6–10 min por cadeira); "
                         "encosto a cada 1–3 semanas (45–90 min); revisão das servoválvulas dos loopers.",
    "medidores": "Calibração diária com padrões; limpeza das lentes dos pirômetros por turno.",
    "mesa_resfriamento": "Limpeza de headers e bicos; aferição do pirômetro de CT.",
    "bobinadeira": "A cada bobina: mancais e pressão do pinch. Turno: gap do pinch. Trimestral: vazamento do mandril. "
                   "Retífica de pinch e wrapper rolls a cada 2–4 semanas.",
}


def _secoes_area(e: cat.Equip) -> dict[str, dict]:
    """Por área do CLP: tags/variáveis da máquina, causas prováveis e ações (modos de falha)."""
    out: dict[str, dict] = {}
    tg = {t["var"]: t["tag"] for t in clp.tags(e)}
    for v in e.variaveis:
        area = clp.AREA_NOME[clp.area_de(v)]
        s = out.setdefault(area, {"area": area, "bit": clp.AREA_BIT[area], "tags": [], "causas": []})
        s["tags"].append({"tag": tg[v.id], "var": v.id, "nome": v.nome, "unidade": v.unidade, "ideal": v.ideal,
                          "faixa": list(v.faixa), "limite_alarme": list(v.limite_alarme)})
        ref = v.ideal if v.ideal is not None else (v.faixa[0] or 0)
        for x in (ref - 1e6, ref + 1e6) if v.sentido != "menor" else (ref + 1e6,):
            c, a = causa_acao(e, v, x)
            par = {"causa": c, "acao": a, "vars": [v.id]}
            achado = next((k for k in s["causas"] if k["causa"] == c), None)
            if achado:
                if v.id not in achado["vars"]:
                    achado["vars"].append(v.id)
            elif not c.startswith("Desvio sem modo"):
                s["causas"].append(par)
    for s in out.values():
        s["efeito_a_jusante"] = EFEITO_JUSANTE.get(e.tipo, "")
    return out


def manual_maquina(e: cat.Equip) -> dict:
    return {"eq": e.id, "nome": e.nome, "clp": clp.clp_id(e.id), "linha": f"{e.linha} — {e.linha_nome}",
            "descricao": e.descricao, "fabricantes_referencia": list(e.fabricantes),
            "manutencao": MANUTENCAO.get(e.tipo, ""), "areas": list(_secoes_area(e).values())}


def manual_clp() -> dict:
    return {
        "titulo": "Manual do CLP padrão da usina (fictício)",
        "perfil": clp.PERFIL,
        "principio": "O CLP não diagnostica: acende a lanterna, liga bits de área nas palavras de falha/aviso e registra "
                     "alarmes (id, categoria, área, tag). O diagnóstico vem do manual da máquina + dados.",
        "lanterna_iec_60073": {"vermelho": "alarme ativo (falha / intervenção necessária)",
                               "amarelo": "aviso: valor fora da faixa normal (condição anormal)",
                               "azul": "manutenção requerida ou máquina em manutenção (ação obrigatória)",
                               "verde": "produzindo, sem alarme"},
        "palavras": "palavra_falha e palavra_aviso: inteiros de 16 bits; bit = 1 → área com problema. "
                    "Ex.: palavra_falha 192 = 0000000011000000 → bits 6 e 7 → MECANICA_VIBRACAO e POSICAO_GEOMETRIA.",
        "areas": [{"bit": b, "area": n, "descricao": d} for b, n, d in clp.AREAS],
        "codigos": {"formato": "AAKK: AA = bit da área (00–15), KK = tipo. Ex.: 0602 = vibração acima do limite de alarme.",
                    "tipos": {f"{k:02d}": {"categoria": c, "significado": s} for k, (c, s) in clp.TIPOS.items()}},
        "estados_packml": clp.ESTADOS_PACKML,
        "tags": "AInnn = entrada analógica, DInn = entrada digital, DI90/DI91 = status de parada. O mapa tag → variável "
                "de cada máquina está no manual dela (buscar_documentacao(id)).",
        "procedimento_diagnostico": [
            "1. status_clp(): ver quais CLPs estão com lanterna vermelha/amarela/azul e as áreas com bit 1.",
            "2. status_clp(id): ler os alarmes (id do código, área, tag).",
            "3. buscar_documentacao(id, codigo=..., tag=...): o que o tag mede, faixa/ideal, causas e ações da área.",
            "4. verificar_parametros(id) e historico(...): confirmar com os dados e datar o início.",
            "5. Seguir o fluxo a montante/jusante e testar com correlacionar; relatorio_desvios resume o turno.",
        ],
        "referencias_publicas": ["ANSI/ISA-TR88.00.02 (PackML): estados, modos e tags Admin.Alarm[#] (ID, Value, "
                                 "Message, Category, DateTime)", "IEC 60073: cores de indicadores e lanternas",
                                 "OPC 30050 (PackML companion specification, OPC UA)"],
    }


# ------------------------------------------------------------------ busca
def _secao_compacta(s: dict, foco_var: str | None = None) -> dict:
    causas = s["causas"]
    if foco_var:
        causas = sorted(causas, key=lambda c: foco_var not in c["vars"])
    return {"area": s["area"], "bit": s["bit"],
            "tags": [{k: t[k] for k in ("tag", "var", "nome", "unidade", "ideal", "faixa", "limite_alarme")}
                     for t in s["tags"] if not foco_var or t["var"] == foco_var] or s["tags"],
            "causas_e_acoes": [{"causa": c["causa"], "acao": c["acao"]} for c in causas[:3]],
            "efeito_a_jusante": s["efeito_a_jusante"],
            "confirmar_com": f"verificar_parametros(id) e historico(id, {foco_var or s['tags'][0]['var']}, 120)"}


def buscar(eq_id: str | None = None, codigo: str | None = None, tag: str | None = None,
           texto: str | None = None) -> dict:
    man = manual_clp()
    sig = None
    if codigo:
        c = re.sub(r"\D", "", codigo).zfill(4)
        area, tipo = int(c[:2]), int(c[2:])
        if area not in clp.AREA_NOME or tipo not in clp.TIPOS:
            raise ValueError(f"Código '{codigo}' inválido. Formato AAKK; tipos: {', '.join(f'{k:02d}' for k in clp.TIPOS)}")
        sig = {"codigo": c, "area": clp.AREA_NOME[area], "categoria": clp.TIPOS[tipo][0],
               "significado": clp.TIPOS[tipo][1]}
    if not eq_id:
        if sig:
            return {"fonte": "manual do CLP padrão", "codigo": sig,
                    "nota": "passe id da máquina para ver os tags e as causas dessa área nela"}
        out = {k: man[k] for k in ("titulo", "principio", "lanterna_iec_60073", "palavras", "codigos",
                                   "estados_packml", "procedimento_diagnostico")}
        out["areas"] = [f"{a['bit']}: {a['area']}" for a in man["areas"]]
        return out
    e = cat.equip(eq_id)
    secoes = _secoes_area(e)
    out: dict = {"fonte": f"manual da máquina {e.id} ({clp.clp_id(e.id)})", "eq": e.id, "nome": e.nome}
    if tag:
        t = tag.strip().upper()
        mapa = {x["tag"]: x for x in clp.tags(e)}
        if t in ("DI90", "DI91"):
            out["tag"] = {"tag": t, "significado": "status de parada da máquina (ver paradas(id=...))"}
            out["secao"] = _secao_compacta(secoes.get("MATERIAL_FLUXO") or next(iter(secoes.values())))
            return out
        if t not in mapa:
            raise ValueError(f"Tag '{tag}' não existe em {e.id}. Tags: {', '.join(mapa)}")
        v = e.var(mapa[t]["var"])
        out["tag"] = {"tag": t, "var": v.id, "nome": v.nome, "unidade": v.unidade}
        out["secao"] = _secao_compacta(secoes[mapa[t]["area"]], v.id)
        if sig:
            out["codigo"] = sig
        return out
    if sig:
        out["codigo"] = sig
        s = secoes.get(sig["area"])
        out["secao"] = _secao_compacta(s) if s else {"nota": f"{e.id} não tem tags na área {sig['area']}"}
        return out
    if texto:
        lista = list(secoes.values())
        corpos = tuple(" ".join([s["area"], s["area"].replace("_", " "), s["efeito_a_jusante"]]
                                + [t["nome"] + " " + t["var"].replace("_", " ") for t in s["tags"]]
                                + [c["causa"] + " " + c["acao"] for c in s["causas"]]) for s in lista)
        melhores = busca.indice(corpos).melhores(texto, 2)
        out["consulta"] = texto
        out["resultados"] = [_secao_compacta(lista[i]) for i, _ in melhores] or "nenhuma seção encontrada"
        ref = buscar_referencia(e.id, texto)
        if ref:
            out["referencia_tecnica"] = ref
        return out
    mm = manual_maquina(e)
    out.update(descricao=mm["descricao"], manutencao=mm["manutencao"], efeito_a_jusante=EFEITO_JUSANTE.get(e.tipo, ""),
               mapa_de_tags=[f"{t['tag']}={t['var']} ({t['area']})" for t in clp.tags(e)],
               nota="passe codigo, tag ou texto para a seção de diagnóstico da área",
               referencia_tecnica=(f"planta://docs/referencia/{e.id}" if referencia_md(e.id) else None))
    return out


# ------------------------------------------------------------------ referência técnica (pesquisa)
REF_DIR = Path(__file__).resolve().parent / "referencia"


def referencia_md(eq_id: str) -> str | None:
    """Documento técnico de referência da máquina (docs/referencia/<id>.md), se existir."""
    f = REF_DIR / f"{cat.equip(eq_id).id}.md"
    return f.read_text(encoding="utf-8") if f.exists() else None


def _trechos_ref(md: str) -> list[tuple[str, str]]:
    """Quebra o Markdown em trechos (seção, texto): parágrafos, itens de lista e linhas de tabela."""
    out, sec = [], ""
    for bloco in re.split(r"\n\s*\n", md):
        for ln in bloco.splitlines():
            ln = ln.strip()
            if ln.startswith("## "):
                sec = ln[3:].strip()
        corpo = [ln.strip() for ln in bloco.splitlines() if ln.strip() and not ln.strip().startswith("#")
                 and not re.fullmatch(r"\|?[\s:|-]+\|?", ln.strip())]
        if not corpo or sec.lower() == "fontes":
            continue
        if all(l.startswith("|") for l in corpo) or all(l[:2] in ("- ", "* ") or l[:1].isdigit() for l in corpo):
            out += [(sec, l) for l in corpo[1 if corpo[0].startswith("|") else 0:]]
        else:
            out.append((sec, " ".join(corpo)))
    return out


def _limpa(t: str, n: int = 360) -> str:
    t = re.sub(r"\s*\|\s*", " | ", t.strip().strip("|")).replace("**", "").replace("`", "")
    return t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0] + "…"


def buscar_referencia(eq_id: str, texto: str, n: int = 3) -> list[dict]:
    md = referencia_md(eq_id)
    if not md:
        return []
    trechos = _trechos_ref(md)
    idx = busca.indice(tuple(sec + " " + t for sec, t in trechos))
    return [{"secao": trechos[i][0], "trecho": _limpa(trechos[i][1])} for i, _ in idx.melhores(texto, n)]


# ------------------------------------------------------------------ Markdown
def md_clp() -> str:
    m = manual_clp()
    L = [f"# {m['titulo']}", "", m["perfil"], "", m["principio"], "", "## Lanterna (IEC 60073)", ""]
    L += [f"- **{k}**: {v}" for k, v in m["lanterna_iec_60073"].items()]
    L += ["", "## Palavras de falha e de aviso", "", m["palavras"], "", "| Bit | Área | Descrição |", "|---|---|---|"]
    L += [f"| {a['bit']} | {a['area']} | {a['descricao']} |" for a in m["areas"]]
    L += ["", "## Códigos de alarme", "", m["codigos"]["formato"], "", "| Tipo (KK) | Categoria | Significado |", "|---|---|---|"]
    L += [f"| {k} | {v['categoria']} | {v['significado']} |" for k, v in m["codigos"]["tipos"].items()]
    L += ["", "## Estados (PackML)", ""] + [f"- **{k}**: {v}" for k, v in m["estados_packml"].items()]
    L += ["", "## Tags", "", m["tags"], "", "## Procedimento de diagnóstico", ""] + m["procedimento_diagnostico"]
    L += ["", "## Referências públicas", ""] + [f"- {r}" for r in m["referencias_publicas"]]
    return "\n".join(L) + "\n"


def md_maquina(e: cat.Equip) -> str:
    m = manual_maquina(e)
    L = [f"# {e.id} — {e.nome}", "", f"- CLP: {m['clp']}", f"- Linha: {m['linha']}",
         f"- Fabricantes de referência: {', '.join(m['fabricantes_referencia'])}", "", m["descricao"], "",
         "## Mapa de tags", "", "| Tag | Variável | Unidade | Ideal | Faixa normal | Limite de alarme | Área |",
         "|---|---|---|---|---|---|---|"]
    for t, v in zip(clp.tags(e), e.variaveis):
        L.append(f"| {t['tag']} | {v.nome} (`{v.id}`) | {v.unidade} | {v.ideal if v.ideal is not None else '—'} | "
                 f"{v.faixa[0]}–{v.faixa[1]} | {v.limite_alarme[0]} / {v.limite_alarme[1]} | {t['area']} |")
    L += ["", "## Diagnóstico por área do CLP", ""]
    for s in m["areas"]:
        L += [f"### Bit {s['bit']} — {s['area']}", "", "Tags: " + ", ".join(f"{t['tag']} `{t['var']}`" for t in s["tags"]), ""]
        for c in s["causas"]:
            L += [f"- **Causa:** {c['causa']}", f"  - **Ação:** {c['acao']}", f"  - Variáveis: {', '.join(c['vars'])}"]
        L += ["", f"Efeito a jusante: {s['efeito_a_jusante']}", ""]
    L += ["## Manutenção", "", m["manutencao"], ""]
    return "\n".join(L)


def exportar(destino: Path | None = None) -> list[Path]:
    destino = destino or Path(__file__).resolve().parent.parent / "docs"
    (destino / "maquinas").mkdir(parents=True, exist_ok=True)
    arqs = [destino / "manual_clp.md"]
    arqs[0].write_text(md_clp(), encoding="utf-8")
    for e in cat.EQUIPAMENTOS:
        f = destino / "maquinas" / f"{e.id}.md"
        f.write_text(md_maquina(e), encoding="utf-8")
        arqs.append(f)
    return arqs


if __name__ == "__main__":
    for f in exportar():
        print(f)
