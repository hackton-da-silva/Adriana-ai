"""Consultas sobre a planta simulada: estado, alertas, indicadores e séries.

Cada função devolve um dict pronto para JSON. O servidor MCP só repassa.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict

from . import catalogo as cat
from .sim import CAPACIDADE_TH, EQUIP_LINHA, META_TH, Bobina, Planta

TURNO_MIN = 480
META_RENDIMENTO = 97.0

# defeito → equipamento responsável (para qualidade/OEE)
CAUSA_DEFEITO = {
    "carepa_secundaria": "DSC-02",
    "marca_periodica_chatter_F5": "F5",
    "espessura_fora_tolerancia": "F5",
    "ct_fora_tolerancia": "ROT-01",
    "cobble_F6": "F6",
    "esboco_sucateado_coil_box": "CB-01",
}


def _r(x: float | None, n: int = 1):
    return None if x is None else round(x, n)


def _linha_de(linha: str | int | None) -> int | None:
    if linha is None or str(linha).strip() == "":
        return None
    s = str(linha).strip().lower()
    for n, nome in cat.LINHAS.items():
        if s in (str(n), f"linha {n}", nome.lower()) or s in nome.lower():
            return n
    raise ValueError(f"Linha '{linha}' não existe. Use 1–4 ou: {', '.join(cat.LINHAS.values())}")


def _var(e: cat.Equip, var_id: str) -> cat.Var:
    try:
        return e.var(var_id.strip())
    except KeyError:
        raise ValueError(f"Variável '{var_id}' não existe em {e.id}. Válidas: {', '.join(v.id for v in e.variaveis)}")


# ------------------------------------------------------------------ avaliação
SEV_ORDEM = {"alarme": 0, "fora_da_faixa": 1, "atencao": 2, "ideal": 3, "sem_material": 4}


def classe(p: Planta, e: cat.Equip, v: cat.Var, m: int) -> tuple[str, str | None]:
    """Classe da leitura no minuto m (ideal | atencao | fora_da_faixa | alarme | sem_material)."""
    x = p.valor(e.id, v.id, m)
    if v.id == "freq_pico_vibracao" and x is not None:
        vib = p.valor(e.id, "vibracao", m)
        if 100 <= x <= 250 and vib is not None and vib > 4:
            return "alarme", "pico em 100–250 Hz com vibração > 4 mm/s (chatter)"
    return cat.classificar(v, x)


def avaliar(v: cat.Var, x: float | None) -> tuple[str, str | None]:
    return cat.classificar(v, x)


def inicio_desvio(p: Planta, e: cat.Equip, v: cat.Var, m: int) -> int:
    """Primeiro minuto do desvio atual (fora do ideal), tolerando até 3 amostras ideais seguidas
    (variáveis oscilantes) e ignorando minutos sem material."""
    s = p.series[(e.id, v.id)]
    ini, ideais = m, 0
    for mm in range(m, max(-1, m - 1440), -1):
        if s[mm] is None:
            continue
        if classe(p, e, v, mm)[0] in ("ideal", "sem_material"):
            ideais += 1
            if ideais > 3:
                break
        else:
            ideais = 0
            ini = mm
    return ini


def _desde(p: Planta, e: cat.Equip, v: cat.Var, m: int) -> str:
    return p.ts_iso(inicio_desvio(p, e, v, m))


def _alertas_equip(p: Planta, e: cat.Equip, m: int, com_atencao: bool = False) -> list[dict]:
    out = []
    for v in e.variaveis:
        st, lim = classe(p, e, v, m)
        if st in ("alarme", "fora_da_faixa") or (com_atencao and st == "atencao"):
            x = p.valor(e.id, v.id, m)
            out.append({"equip": e.id, "severidade": st, "tipo": "variavel", "variavel": v.id,
                        "valor": x, "unidade": v.unidade, "limite": lim,
                        "mensagem": f"{v.nome} = {x} {v.unidade} ({lim})", "desde": _desde(p, e, v, m)})
    for par in p.paradas_ativas(m):
        if par.equip == e.id:
            out.append({"equip": e.id, "severidade": "alarme", "tipo": "evento",
                        "mensagem": f"Parado: {par.motivo}", "desde": p.ts_iso(par.inicio)})
    return out


def _alertas_tendencia(p: Planta, m: int) -> list[dict]:
    out = []
    ult60 = [b for b in p.bobinas if m - 60 <= b.inicio and b.fim <= m + 1]
    hsla = [b for b in p.bobinas if b.aco == "HSLA" and m - 90 <= b.inicio and b.fim <= m + 1]
    fora = [b for b in hsla if abs(b.erro_ct) > 20]
    if len(fora) >= 2:
        out.append({"equip": "ROT-01", "severidade": "fora_da_faixa", "tipo": "tendencia",
                    "mensagem": f"{len(fora)} de {len(hsla)} bobinas HSLA nos últimos 90 min com CT fora de ±20 °C "
                                f"(erro médio {sum(b.erro_ct for b in hsla) / len(hsla):+.0f} °C)",
                    "desde": p.ts_iso(min(b.inicio for b in fora))})
    if ult60:
        car = [b for b in ult60 if "carepa_secundaria" in b.defeitos]
        if len(car) / len(ult60) > 0.2:
            out.append({"equip": "MED-01", "severidade": "fora_da_faixa", "tipo": "tendencia",
                        "mensagem": f"Carepa secundária em {len(car)} de {len(ult60)} bobinas na última hora",
                        "desde": p.ts_iso(min(b.inicio for b in car))})
    cob = [x for x in p.paradas if x.categoria == "cobble" and m - TURNO_MIN <= x.inicio <= m]
    if len(cob) >= 2:
        out.append({"equip": "F6", "severidade": "fora_da_faixa", "tipo": "tendencia",
                    "mensagem": f"{len(cob)} cobbles no F6 nas últimas 8 h (motivo registrado: instabilidade do looper F5–F6)",
                    "desde": p.ts_iso(cob[0].inicio)})
    return out


def _estado(p: Planta, e: cat.Equip, m: int, alertas: list[dict]) -> str:
    """parado | parado_linha | alarme | fora_da_faixa | atencao | ideal"""
    if any(par.equip == e.id for par in p.paradas_ativas(m)):
        return "parado"
    if e.id in EQUIP_LINHA and p.linha_parada(m) is not None:
        return "parado_linha"
    if not alertas:
        return "ideal"
    return min((a["severidade"] for a in alertas), key=SEV_ORDEM.__getitem__)


# ------------------------------------------------------------------ indicadores
class _Ind:
    """Indicadores da janela [m - janela, m]."""

    def __init__(self, p: Planta, m: int, janela: int = TURNO_MIN):
        self.m, self.w0, self.janela = m, m - janela, janela
        self.bob = [b for b in p.bobinas if b.inicio >= self.w0 and b.fim <= m + 1]
        self.par = [x for x in p.paradas if x.fim > self.w0 and x.inicio < m + 1]
        clip = lambda x: max(0.0, min(x.fim, m + 1) - max(x.inicio, self.w0))  # noqa: E731
        self.clip = clip
        self.parado_linha = sum(clip(x) for x in self.par if x.para_linha)
        self.rodando = janela - self.parado_linha
        self.t_total = sum(b.peso_t for b in self.bob)
        self.t_prod = sum(b.peso_t for b in self.bob if b.status != "sucata")
        self.t_ok = sum(b.peso_t for b in self.bob if b.status == "ok")
        self.t_placa = sum(b.peso_t / 0.975 for b in self.bob)
        self.desempenho = self.t_total / (CAPACIDADE_TH * self.rodando / 60) if self.rodando > 0 else 0.0
        self.perda_eq: dict[str, float] = defaultdict(float)
        for b in self.bob:
            for eq in self._responsaveis(b):
                self.perda_eq[eq] += b.peso_t

    @staticmethod
    def _responsaveis(b: Bobina) -> set[str]:
        if b.status == "ok":
            return set()
        r = {CAUSA_DEFEITO[d] for d in b.defeitos if d in CAUSA_DEFEITO}
        if "telescopia" in b.defeitos:
            r.add(b.bobinadeira)
        return r

    def oee(self, eqs: set[str] | None) -> dict:
        if eqs is None:  # área
            disp = self.rodando / self.janela
            qual = self.t_ok / self.t_total if self.t_total else 1.0
        else:
            parado = sum(self.clip(x) for x in self.par if x.equip in eqs and (x.para_linha or len(eqs) == 1))
            disp = 1 - parado / self.janela
            perdas = sum(b.peso_t for b in self.bob if self._responsaveis(b) & eqs)
            qual = 1 - perdas / self.t_total if self.t_total else 1.0
        des = min(1.0, self.desempenho)
        return {"disponibilidade": _r(disp * 100), "desempenho": _r(des * 100), "qualidade": _r(qual * 100),
                "oee": _r(disp * des * qual * 100)}


# ------------------------------------------------------------------ ferramentas
def listar_maquinas(p: Planta, linha: str | None = None) -> dict:
    m = p.garantir()
    n = _linha_de(linha)
    ind = _Ind(p, m)
    out = []
    for e in cat.EQUIPAMENTOS:
        if n is not None and e.linha != n:
            continue
        al = _alertas_equip(p, e, m, com_atencao=True)
        out.append({"id": e.id, "nome": e.nome, "linha": e.linha, "estado": _estado(p, e, m, al),
                    "oee_pct": ind.oee({e.id})["oee"],
                    "alarmes": sum(a["severidade"] == "alarme" for a in al),
                    "fora_da_faixa": sum(a["severidade"] == "fora_da_faixa" for a in al),
                    "atencao": sum(a["severidade"] == "atencao" for a in al)})
    lp = p.linha_parada(m)
    return {"cenario": cat.CENARIO, "hora": p.ts_iso(m), "janela_oee": "últimas 8 h",
            "linha_parada": None if lp is None else {"equip": lp.equip, "motivo": lp.motivo, "desde": p.ts_iso(lp.inicio)},
            "maquinas": out}


def status_maquina(p: Planta, eq_id: str) -> dict:
    e = cat.equip(eq_id)
    m = p.garantir()
    al = _alertas_equip(p, e, m, com_atencao=True)
    variaveis, fora = [], []
    for v in e.variaveis:
        x = p.valor(e.id, v.id, m)
        st, lim = classe(p, e, v, m)
        d = {"var": v.id, "valor": x, "unidade": v.unidade, "ideal": v.ideal, "faixa": list(v.faixa),
             "limite_alarme": list(v.limite_alarme), "status": st}
        variaveis.append(d)
        if st in ("atencao", "fora_da_faixa", "alarme"):
            fora.append({"var": v.id, "nome": v.nome, "valor": x, "ideal": v.ideal, "limite": lim, "severidade": st})
    fora.sort(key=lambda f: SEV_ORDEM[f["severidade"]])
    out = {"id": e.id, "nome": e.nome, "linha": f"{e.linha} — {e.linha_nome}", "hora": p.ts_iso(m),
           "estado": _estado(p, e, m, al), "fabricantes_referencia": list(e.fabricantes),
           "desvios": fora, "variaveis": variaveis}
    eventos = [a["mensagem"] for a in al if a["tipo"] == "evento"]
    if eventos:
        out["eventos"] = eventos
    lp = p.linha_parada(m)
    if lp is not None and e.id in EQUIP_LINHA:
        out["linha_parada"] = {"equip": lp.equip, "motivo": lp.motivo, "desde": p.ts_iso(lp.inicio),
                               "nota": "variáveis de processo ficam null (sem material)"}
    b = p.bobina_em(m)
    if b is not None and e.id in EQUIP_LINHA:
        out["bobina_em_processo"] = {"id": b.id, "aco": b.aco, "forno_origem": b.forno, "espessura_mm": b.espessura_mm}
    if e.tipo == "cadeira_acabadora" or e.id == "R1":
        km = p.km(e.id, m)
        lim = cat.CAMPANHA_KM.get(e.id, 450)
        out["campanha_cilindro"] = {"km": _r(km), "limite_km": lim, "pct": _r(km / lim * 100)}
    return out


def historico(p: Planta, eq_id: str, variavel: str, minutos: int = 60, agregacao: int | None = None) -> dict:
    e = cat.equip(eq_id)
    v = _var(e, variavel)
    m = p.garantir()
    minutos = max(1, min(int(minutos), m + 1))
    ini = m - minutos + 1
    s = p.serie(e.id, v.id, ini, m)
    auto = False
    if not agregacao and minutos > 120:
        agregacao, auto = math.ceil(minutos / 120), True
    validos = [x for x in s if x is not None]
    stats = {"n": len(s), "n_sem_material": len(s) - len(validos)}
    if validos:
        stats.update(min=min(validos), max=max(validos), media=_r(sum(validos) / len(validos), v.casas + 1),
                     primeiro=validos[0], ultimo=validos[-1],
                     n_fora_faixa=sum(avaliar(v, x)[0] in ("fora_da_faixa", "alarme") for x in validos),
                     n_fora_do_ideal=sum(avaliar(v, x)[0] != "ideal" for x in validos))
    out = {"id": e.id, "variavel": v.id, "nome": v.nome, "unidade": v.unidade, "ideal": v.ideal,
           "faixa_normal": list(v.faixa), "limite_alarme": list(v.limite_alarme),
           "inicio": p.ts_iso(ini), "fim": p.ts_iso(m), "estatisticas": stats}
    if agregacao and agregacao > 1:
        agregacao = int(agregacao)
        pts = []
        for k in range(0, len(s), agregacao):
            bloco = [x for x in s[k:k + agregacao] if x is not None]
            hora = p.ts(ini + k).strftime("%H:%M")
            if bloco:
                pts.append([hora, _r(sum(bloco) / len(bloco), v.casas), min(bloco), max(bloco)])
            else:
                pts.append([hora, None, None, None])
        out.update(agregacao_min=agregacao, formato_ponto=["hora", "media", "min", "max"], pontos=pts)
        if auto:
            out["nota"] = f"agregado automaticamente em {agregacao} min para caber no contexto; passe agregacao=1 para dados brutos"
    else:
        out.update(agregacao_min=1, formato_ponto=["hora", "valor"],
                   pontos=[[p.ts(ini + k).strftime("%H:%M"), x] for k, x in enumerate(s)])
    return out


def _sinais_pre(p: Planta, inicio: float) -> dict:
    a, b = int(inicio) - 10, int(inicio) - 1

    def ext(eq, var):
        xs = [x for x in p.serie(eq, var, a, b) if x is not None]
        return [min(xs), max(xs)] if xs else None

    return {"F6.delta_forca_lados_kN_min_max": ext("F6", "delta_forca_lados"),
            "F6.corrente_motor_pct_min_max": ext("F6", "corrente_motor"),
            "F5.angulo_looper_graus_min_max": ext("F5", "angulo_looper"),
            "F5.amplitude_oscilacao_looper_graus_min_max": ext("F5", "amplitude_oscilacao_looper"),
            "F5.vibracao_mm_s_min_max": ext("F5", "vibracao")}


def paradas(p: Planta, periodo_horas: float = 8, eq_id: str | None = None) -> dict:
    m = p.garantir()
    w0 = m - periodo_horas * 60
    filtro = cat.equip(eq_id).id if eq_id else None
    lst, por_eq = [], defaultdict(lambda: {"n": 0, "minutos": 0.0})
    for x in p.paradas:
        if x.fim <= w0 or x.inicio > m + 0.5:
            continue
        if filtro and x.equip != filtro:
            continue
        em_and = x.inicio <= m + 0.5 < x.fim
        dur = (min(x.fim, m + 1) - x.inicio)
        lst.append({"id": x.id, "equip": x.equip, "inicio": p.ts_iso(x.inicio),
                    "fim": None if em_and else p.ts_iso(x.fim), "duracao_min": round(dur),
                    "motivo": x.motivo, "tipo": x.tipo, "parou_linha": x.para_linha, "em_andamento": em_and})
        if x.categoria == "cobble":
            lst[-1]["sinais_10min_antes"] = _sinais_pre(p, x.inicio)
        por_eq[x.equip]["n"] += 1
        por_eq[x.equip]["minutos"] += round(dur)
    ranking = sorted(({"equip": k, **v} for k, v in por_eq.items()), key=lambda d: -d["minutos"])
    return {"periodo": {"inicio": p.ts_iso(max(0, w0)), "fim": p.ts_iso(m)},
            "total_paradas": len(lst), "total_min": sum(d["minutos"] for d in ranking),
            "min_linha_parada": round(sum(min(x.fim, m + 1) - max(x.inicio, w0) for x in p.paradas
                                          if x.para_linha and x.fim > w0 and x.inicio <= m + 0.5
                                          and (not filtro or x.equip == filtro))),
            "por_equipamento": ranking, "paradas": lst}


def alertas_ativos(p: Planta) -> dict:
    m = p.garantir()
    al = []
    for e in cat.EQUIPAMENTOS:
        al += _alertas_equip(p, e, m)
    al += _alertas_tendencia(p, m)
    al.sort(key=lambda a: (SEV_ORDEM[a["severidade"]], a["equip"]))
    return {"hora": p.ts_iso(m), "total": len(al),
            "alarmes": sum(a["severidade"] == "alarme" for a in al),
            "fora_da_faixa": sum(a["severidade"] == "fora_da_faixa" for a in al), "itens": al}


def resumo_producao(p: Planta) -> dict:
    m = p.garantir()
    ind = _Ind(p, m)
    meta = META_TH * TURNO_MIN / 60
    ct = [b for b in ind.bob if b.status != "sucata"]
    por_aco = {}
    for aco in cat.CT_VISADA:
        bs = [b for b in ct if b.aco == aco]
        if bs:
            por_aco[aco] = {"bobinas": len(bs), "ct_dentro_20_pct": _r(sum(abs(b.erro_ct) <= 20 for b in bs) / len(bs) * 100),
                            "erro_ct_medio_c": _r(sum(b.erro_ct for b in bs) / len(bs))}
    gas = {}
    for f in ("FRN-01", "FRN-02"):
        s = [x for x in p.serie(f, "consumo_especifico", m - 119, m) if x is not None]
        gas[f] = _r(sum(s) / len(s), 3) if s else None
    status = Counter(b.status for b in ind.bob)
    linhas = []
    for n, nome in cat.LINHAS.items():
        eqs = {e.id for e in cat.EQUIPAMENTOS if e.linha == n}
        linhas.append({"linha": n, "nome": nome, **ind.oee(eqs)})
    par_eq = Counter()
    for x in ind.par:
        if x.para_linha:
            par_eq[x.equip] += round(ind.clip(x))
    return {
        "cenario": cat.CENARIO,
        "turno": {"inicio": p.ts_iso(ind.w0), "fim": p.ts_iso(m), "horas": TURNO_MIN / 60},
        "producao_t": round(ind.t_prod), "meta_t": round(meta), "atingimento_pct": _r(ind.t_prod / meta * 100),
        "ritmo_medio_th": round(ind.t_prod / (TURNO_MIN / 60)),
        "ritmo_rodando_th": round(ind.t_total / (ind.rodando / 60)) if ind.rodando else 0,
        "minutos_linha_parada": round(ind.parado_linha),
        "linha_parada_por_equip_min": dict(par_eq.most_common()),
        "bobinas": {"total": len(ind.bob), "ok": status["ok"], "desclassificadas": status["desclassificada"],
                    "sucata": status["sucata"]},
        "oee_area": ind.oee(None),
        "oee_por_linha": linhas,
        "rendimento_metalico_pct": _r(ind.t_prod / ind.t_placa * 100 if ind.t_placa else 0),
        "meta_rendimento_pct": META_RENDIMENTO,
        "ct_dentro_20_pct": _r(sum(abs(b.erro_ct) <= 20 for b in ct) / len(ct) * 100 if ct else 0),
        "ct_por_aco": por_aco,
        "consumo_gas_gj_t_ultimas_2h": gas,
        "perda_qualidade_t_por_equip": {k: round(v) for k, v in sorted(ind.perda_eq.items(), key=lambda kv: -kv[1])},
    }


def campanha_cilindros(p: Planta) -> dict:
    m = p.garantir()
    out = []
    for cad in ("R1", "F1", "F2", "F3", "F4", "F5", "F6"):
        lim = cat.CAMPANHA_KM.get(cad, 450)
        km = p.km(cad, m)
        trocas = [t for t in p._trocas(cad) if t <= m + 0.5]
        ult = max(trocas) if trocas else None
        ini = max(m - 120, int(ult) if ult else 0)
        horas = (m - ini) / 60
        taxa = (km - p.km(cad, ini)) / horas if horas > 0.25 else 0
        if taxa <= 0:
            taxa = (sum(b.km_r1 if cad == "R1" else b.km_cadeira(int(cad[1])) for b in p.bobinas if m - 480 <= b.inicio <= m)) / 8
        rest = lim - km
        h_rest = rest / taxa if taxa > 0 else None
        d = {"cadeira": cad, "km": _r(km), "limite_km": lim, "pct_campanha": _r(km / lim * 100),
             "km_por_hora": _r(taxa), "km_restantes": _r(rest),
             "horas_ate_limite": _r(h_rest) if h_rest is not None and h_rest > 0 else 0,
             "previsao_troca": p.ts_iso(m + h_rest * 60) if h_rest and h_rest > 0 else "vencida",
             "ultima_troca": p.ts_iso(ult) if ult else "antes do início do histórico",
             "material": "aço fundido/forjado (desbaste)" if cad == "R1" else cat.POR_ID[cad].extra["material_cilindro_trabalho"]}
        if cad != "R1":
            vib = p.ultimo_valido(cad, "vibracao", m)[0]
            fq = p.ultimo_valido(cad, "freq_pico_vibracao", m)[0]
            d["vibracao_mm_s"] = vib
            d["freq_pico_hz"] = fq
            f_now = [x for x in p.serie(cad, "forca_laminacao", m - 59, m) if x is not None]
            ref0 = int(ult) if ult else 0
            f_ref = [x for x in p.serie(cad, "forca_laminacao", ref0, ref0 + 59) if x is not None]
            if f_now and f_ref and m - ref0 > 90:
                d["forca_vs_inicio_campanha_pct"] = _r((sum(f_now) / len(f_now)) / (sum(f_ref) / len(f_ref)) * 100 - 100)
            if km / lim >= 0.9 or (vib or 0) > 7:
                d["situacao"] = "trocar na próxima oportunidade"
            elif km / lim >= 0.75:
                d["situacao"] = "planejar troca"
            else:
                d["situacao"] = "ok"
        else:
            d["situacao"] = "ok" if km / lim < 0.75 else "planejar troca"
        out.append(d)
    return {"hora": p.ts_iso(m), "referencia": "campanha F1–F3: 60–120 km; F4–F6: 40–80 km; troca de cilindro de trabalho 6–10 min/cadeira",
            "cilindros_trabalho": out}


def bobinas(p: Planta, periodo_horas: float = 8, aco: str | None = None, limite: int = 40) -> dict:
    m = p.garantir()
    w0 = m - periodo_horas * 60
    if aco:
        mapa = {k.lower(): k for k in cat.CT_VISADA}
        a = aco.strip().lower().replace(" ", "_")
        if a not in mapa:
            raise ValueError(f"Aço '{aco}' não existe. Válidos: {', '.join(cat.CT_VISADA)}")
        aco = mapa[a]
    bs = [b for b in p.bobinas if b.inicio >= w0 and b.fim <= m + 1 and (not aco or b.aco == aco)]

    def resumo(grupo: list[Bobina]) -> dict:
        boas = [b for b in grupo if b.status != "sucata"]
        r = {"bobinas": len(grupo), "peso_t": round(sum(b.peso_t for b in grupo)),
             "ok": sum(b.status == "ok" for b in grupo), "desclassificadas": sum(b.status == "desclassificada" for b in grupo),
             "sucata": sum(b.status == "sucata" for b in grupo)}
        if boas:
            r.update(fdt_media_c=round(sum(b.fdt for b in boas) / len(boas)),
                     erro_ct_medio_c=_r(sum(b.erro_ct for b in boas) / len(boas)),
                     ct_dentro_20_pct=_r(sum(abs(b.erro_ct) <= 20 for b in boas) / len(boas) * 100))
        return r

    defeitos = Counter(d for b in bs for d in b.defeitos)
    lst = [{"id": b.id, "hora": p.ts(b.inicio).strftime("%H:%M"), "aco": b.aco, "esp_mm": b.espessura_mm,
            "larg_mm": b.largura_mm, "peso_t": b.peso_t, "forno": b.forno, "bob": b.bobinadeira,
            "t_desenf_c": b.t_desenf, "fdt_c": b.fdt, "ct_visada_c": b.ct_visada, "ct_medida_c": b.ct_medida,
            "erro_ct_c": b.erro_ct, "defeitos": b.defeitos, "status": b.status}
           for b in reversed(bs)]
    limite = max(1, int(limite))
    return {
        "periodo": {"inicio": p.ts_iso(max(0, w0)), "fim": p.ts_iso(m)}, "filtro_aco": aco,
        "resumo": resumo(bs),
        "por_aco": {k: resumo([b for b in bs if b.aco == k]) for k in cat.CT_VISADA if any(b.aco == k for b in bs)},
        "por_forno": {f: resumo([b for b in bs if b.forno == f]) for f in ("FRN-01", "FRN-02")},
        "defeitos": dict(defeitos.most_common()),
        "bobinas": lst[:limite],
        **({"nota": f"lista truncada nas {limite} mais recentes de {len(lst)}; use 'limite' ou filtre por aço"}
           if len(lst) > limite else {}),
    }


def correlacionar(p: Planta, id_a: str, var_a: str, id_b: str, var_b: str, minutos: int = 120,
                  defasagem_min: int = 0) -> dict:
    ea, eb = cat.equip(id_a), cat.equip(id_b)
    va, vb = _var(ea, var_a), _var(eb, var_b)
    m = p.garantir()
    lag = int(defasagem_min)
    minutos = max(5, min(int(minutos), m + 1 - abs(lag)))
    ini = m - minutos + 1
    a = p.serie(ea.id, va.id, ini - max(lag, 0), m - max(lag, 0))
    b = p.serie(eb.id, vb.id, ini + min(lag, 0), m + min(lag, 0))
    pares = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    out = {"a": f"{ea.id}.{va.id}", "b": f"{eb.id}.{vb.id}", "minutos": minutos, "defasagem_min": lag,
           "n_pares": len(pares)}
    if len(pares) < 10:
        out["erro"] = "pares insuficientes (linha parada ou janela curta); aumente 'minutos'"
        return out
    xs, ys = [x for x, _ in pares], [y for _, y in pares]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in pares)
    r = sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else 0.0
    ar = abs(r)
    forca = "forte" if ar >= 0.7 else "moderada" if ar >= 0.4 else "fraca" if ar >= 0.2 else "desprezível"
    sinal = "positiva" if r > 0 else "negativa"
    out.update(r_pearson=round(r, 3), interpretacao=f"correlação {forca} {sinal}" if forca != "desprezível" else "sem correlação relevante",
               media_a=_r(mx, 2), media_b=_r(my, 2),
               nota="correlação não é causalidade; defasagem_min > 0 compara A(t) com B(t + defasagem)")
    return out
