"""Desvios do nível ideal de operação: verificar_parametros e relatorio_desvios.

Causas prováveis e ações sugeridas vêm dos modos de falha de docs/planta/organizacao-laminacao.md.
"""

from __future__ import annotations

from statistics import mean

from . import catalogo as cat
from . import consultas as q
from .sim import EQUIP_LINHA, Planta

# ------------------------------------------------------------------ causas × ações (modos de falha)
# (tipos ou ids de equipamento, prefixos de variável, direção: "baixo" | "alto" | None, causa, ação)
_REGRAS: list[tuple[set[str], tuple[str, ...], str | None, str, str]] = [
    ({"forno_viga_caminhante"}, ("queimadores_em_trip",), None,
     "Queimador em trip ou falha de chama.",
     "Verificar queimador e detector de chama e rearmar; até a zona voltar ao setpoint, reduzir o ritmo de desenfornamento."),
    ({"forno_viga_caminhante"}, ("t_zona_",), "baixo",
     "Zona abaixo do setpoint: queimador em trip, ritmo alto ou variação do gás misto.",
     "Conferir queimadores e o poder calorífico do gás; segurar placas no forno (mais residência)."),
    ({"forno_viga_caminhante"}, ("t_zona_",), "alto",
     "Zona acima do setpoint: compensação de outra zona ou malha de controle.",
     "Conferir a malha de controle da zona e a distribuição de carga entre zonas."),
    ({"forno_viga_caminhante"}, ("t_desenfornamento", "desvio_modelo_n2"), None,
     "Placa fria: ritmo alto, queimador em trip ou residência curta; efeito: força do R1 +15–25 % e FDT baixa.",
     "Aumentar a residência ou reduzir o ritmo; validar termopares e o modelo nível 2."),
    ({"forno_viga_caminhante"}, ("o2_fumos",), "alto",
     "Excesso de ar: deriva do analisador de O₂ ou ar de combustão sem chama (queimador em trip); sobe o GJ/t e a carepa.",
     "Calibrar o analisador de O₂ e corrigir a relação ar/gás."),
    ({"forno_viga_caminhante"}, ("o2_fumos", "co_fumos"), None,
     "Combustão fora da relação ar/gás (falta de ar ou CO alto).",
     "Ajustar a relação ar/gás e conferir o analisador de CO."),
    ({"forno_viga_caminhante"}, ("consumo_especifico", "t_fumos"), None,
     "Consumo de gás alto: excesso de ar, zona compensando queimador em trip ou placa fria.",
     "Corrigir a combustão (O₂) e rearmar o queimador; conferir o recuperador."),
    ({"forno_viga_caminhante"}, ("dt_skid_mark",), None,
     "Skid mark acentuada: isolamento do skid danificado ou hot riders gastos.",
     "Programar inspeção dos skids na próxima parada; aumentar o tempo de encharque."),
    ({"forno_viga_caminhante"}, ("dt_agua_skids", "t_agua_skids"), None,
     "Falha da água dos skids: bomba ou entupimento (risco de parada de emergência).",
     "Verificar bomba e vazão da água dos skids imediatamente."),
    ({"forno_viga_caminhante"}, ("pressao_forno",), None,
     "Pressão do forno fora: damper ou controle de tiragem.", "Conferir damper e malha de pressão."),
    ({"descarepador"}, ("pressao_header", "nivel_acumulador"), "baixo",
     "Perda de pressão: bomba degradada ou acumulador sem pré-carga; deixa carepa residual na tira.",
     "Passar para a bomba reserva, verificar a pré-carga do acumulador e programar a manutenção da bomba."),
    ({"descarepador"}, ("corrente_bomba_",), None,
     "Corrente anômala da bomba: bomba degradada (desgaste ou cavitação).",
     "Comparar com a outra bomba, inspecionar a bomba e trocar para a reserva."),
    ({"descarepador"}, ("vazao_ciclo",), "baixo",
     "Bico entupido (vazão cai com pressão estável) ou perda de pressão.", "Inspecionar e limpar os bicos."),
    ({"descarepador"}, ("dp_filtro",), None, "Filtro saturado.", "Retrolavar ou trocar o filtro."),
    ({"R1"}, ("forca_laminacao", "torque", "corrente_motor", "t_placa_entrada", "t_esboco_saida"), None,
     "Placa fria vinda do forno (força +15–25 %) ou desgaste do cilindro; risco de trip do motor.",
     "Conferir a T de desenfornamento do forno de origem (bobinas por forno) e a campanha do cilindro."),
    ({"R1"}, ("delta_forca_lados", "camber", "forca_edger"), None,
     "Camber: assimetria de gap ou de temperatura; o esboço bate nas guias.",
     "Nivelar o gap entre lados e conferir as guias e o edger."),
    ({"R1"}, ("vibracao_mancais",), None, "Mancal com desgaste ou lubrificação ruim.",
     "Inspecionar a lubrificação e a temperatura dos mancais."),
    ({"coil_box"}, ("t_entrada", "t_saida"), "baixo", "Esboço frio vindo do desbaste (placa fria no forno).",
     "Investigar o forno de origem."),
    ({"coil_box"}, ("dt_cabeca_cauda", "tempo_enrol_desenrol"), None,
     "Falha de equalização ou de transferência do mandril.", "Inspecionar o mandril e a transferência."),
    ({"tesoura"}, ("",), None, "Lâmina gasta ou corte fora de posição (desponte longo).",
     "Girar ou trocar as facas; conferir o posicionamento."),
    ({"cadeira_acabadora"}, ("vibracao", "freq_pico_vibracao"), None,
     "Chatter (vibração de 3ª oitava, 100–250 Hz): mecanismo regenerativo, velocidade alta, lubrificação ruim, "
     "cilindro em fim de campanha.",
     "Reduzir a velocidade da cadeira, conferir a lubrificação do roll gap e antecipar a troca do cilindro de trabalho."),
    ({"cadeira_acabadora"}, ("angulo_looper", "amplitude_oscilacao_looper", "tensao_entre_cadeiras"), None,
     "Instabilidade do looper: servoválvula ou sintonia da malha, agravada por vibração da cadeira; precursor de cobble.",
     "Verificar a servoválvula e ressintonizar a malha do looper; atacar a vibração da cadeira."),
    ({"cadeira_acabadora"}, ("delta_forca_lados",), None,
     "Pré-cobble: gradiente térmico, guia desalinhada (~2 mm), camber ou perda de altura do looper.",
     "Conferir as guias e o looper a montante; reduzir a velocidade."),
    ({"cadeira_acabadora"}, ("km_campanha_cilindro",), None,
     "Fim de campanha do cilindro de trabalho (força +5–10 %, defeito periódico).",
     "Programar a troca do cilindro de trabalho (6–10 min por cadeira)."),
    ({"cadeira_acabadora"}, ("forca_laminacao", "corrente_motor"), None,
     "Força ou corrente alta: fim de campanha, placa fria ou pico pré-cobble.",
     "Conferir a campanha do cilindro e a temperatura de entrada."),
    ({"MED-01"}, ("amplitude_oscilacao_espessura", "desvio_espessura"), None,
     "Espessura oscilando: chatter ou looper instável no acabador, ou limite do AGC.",
     "Investigar a vibração das cadeiras e os loopers (F4–F6)."),
    ({"MED-01"}, ("fdt", "gradiente_borda_centro"), None,
     "FDT fora do alvo: placa ou esboço frio a montante.", "Investigar o forno de origem e o desbaste."),
    ({"MED-01"}, ("desvio_calibracao", "tensao_tubo", "corrente_tubo", "t_cabecote"), None,
     "Descalibração do medidor (o AGC corrige errado).", "Calibrar com os padrões."),
    ({"MED-01"}, ("coroa_c40", "cunha", "planicidade", "sobrelargura"), None,
     "Perfil ou planicidade fora: setup de coroa/bending ou desgaste de cilindro.", "Revisar o setup e a campanha."),
    ({"mesa_resfriamento"}, ("vazao_banco_",), "baixo",
     "Banco entupido: vazão abaixo do setpoint; CT +20–50 °C e propriedades fora da especificação.",
     "Desentupir o header e conferir a válvula do banco; compensar com os bancos vizinhos no modelo CTC."),
    ({"mesa_resfriamento"}, ("erro_ct", "taxa_resf"), None,
     "CT fora do alvo: banco entupido, pirômetro de CT sujo ou aceleração do trem.",
     "Conferir a vazão por banco e limpar o pirômetro de CT."),
    ({"mesa_resfriamento"}, ("t_agua", "pressao_header", "vazao_total"), None,
     "Água de resfriamento fora do ideal.", "Conferir a torre de resfriamento e as bombas."),
    ({"bobinadeira"}, ("assimetria_gap_pinch", "telescopia", "forca_pinch"), None,
     "Pinch assimétrico: causa bobina telescopada.", "Ajustar o gap do pinch roll."),
    ({"bobinadeira"}, ("erro_posicao_wrapper",), None, "Marcas de wrapper: pico de força no degrau.",
     "Revisar o step control dos wrapper rolls."),
    ({"bobinadeira"}, ("pressao_expansao_mandril",), None, "Falha do mandril: a bobina ovaliza.",
     "Testar vazamento do mandril."),
    ({"bobinadeira"}, ("t_mancal_wrapper",), None, "Mancal do wrapper aquecendo.", "Inspecionar a lubrificação."),
]


def causa_acao(e: cat.Equip, v: cat.Var, x: float | None) -> tuple[str, str]:
    direcao = None
    if x is not None and v.ideal is not None:
        direcao = "baixo" if x < v.ideal else "alto"
    for alvos, prefixos, dirr, causa, acao in _REGRAS:
        if (e.tipo in alvos or e.id in alvos) and any(v.id.startswith(px) for px in prefixos):
            if dirr is None or dirr == direcao:
                return causa, acao
    return "Desvio sem modo de falha catalogado.", "Acompanhar a tendência e inspecionar o equipamento."


# ------------------------------------------------------------------ medidas do desvio
def _dist(v: cat.Var, x: float) -> float:
    if v.ideal is None:
        lo, hi = v.faixa
        return max(0.0, (lo - x) if lo is not None and x < lo else (x - hi) if hi is not None and x > hi else 0.0)
    return max(0.0, x - v.ideal) if v.sentido == "menor" else abs(x - v.ideal)


def tendencia(p: Planta, e: cat.Equip, v: cat.Var, m: int) -> str:
    s = p.series[(e.id, v.id)]
    rec = [x for x in s[max(0, m - 10): m + 1] if x is not None]
    old = [x for x in s[max(0, m - 60): max(0, m - 30)] if x is not None]
    if not old:
        old = [x for x in s[max(0, m - 150): max(0, m - 30)] if x is not None]
    if not rec or not old:
        return "estavel"
    d_rec, d_old = mean(_dist(v, x) for x in rec), mean(_dist(v, x) for x in old)
    ref = v.tol_ideal if v.tol_ideal else (abs(v.ideal) * 0.05 if v.ideal else 1.0)
    thr = max(0.15 * ref, 0.05 * d_old, 1e-9)
    if d_rec - d_old > thr:
        return "piorando"
    if d_old - d_rec > thr:
        return "melhorando"
    return "estavel"


def _num(x: float | None, casas: int = 1):
    return None if x is None else round(x, casas)


def _desvio_item(p: Planta, e: cat.Equip, v: cat.Var, m: int, sev: str, lim: str | None) -> dict:
    x = p.valor(e.id, v.id, m)
    ref = v.ideal
    d: dict = {"var": v.id, "valor": x, "un": v.unidade, "ideal": ref, "faixa": list(v.faixa),
               "alarme": list(v.limite_alarme), "severidade": sev}
    if ref is not None and x is not None:
        d["desvio"] = _num(x - ref, v.casas + 1)
        if ref:
            d["desvio_pct"] = _num((x - ref) / abs(ref) * 100)
    ini = q.inicio_desvio(p, e, v, m)
    d["ha_min"] = m - ini
    d["tendencia"] = tendencia(p, e, v, m)
    return d


def verificar_parametros(p: Planta, eq_id: str | None = None, linha: str | None = None,
                         incluir_atencao: bool = True, max_equipamentos: int = 8) -> dict:
    m = p.garantir()
    n = q._linha_de(linha)
    if eq_id:
        eqs = [cat.equip(eq_id)]
    else:
        eqs = [e for e in cat.EQUIPAMENTOS if n is None or e.linha == n]
    sevs = {"alarme", "fora_da_faixa"} | ({"atencao"} if incluir_atencao else set())
    lp = p.linha_parada(m)
    tendencias = q._alertas_tendencia(p, m)
    grupos, cont = [], {"alarme": 0, "fora_da_faixa": 0, "atencao": 0}
    for e in eqs:
        itens = []
        for v in e.variaveis:
            sev, lim = q.classe(p, e, v, m)
            if sev in sevs:
                itens.append((v, sev, lim))
        eventos = [f"Parado desde {p.ts(par.inicio).strftime('%H:%M')}: {par.motivo}"
                   for par in p.paradas_ativas(m) if par.equip == e.id]
        tend = [t["mensagem"] for t in tendencias if t["equip"] == e.id]
        if not itens and not eventos and not tend:
            continue
        itens.sort(key=lambda t: q.SEV_ORDEM[t[1]])
        desv = [_desvio_item(p, e, v, m, sev, lim) for v, sev, lim in itens]
        for d in desv:
            cont[d["severidade"]] += 1
        desv.sort(key=lambda d: (q.SEV_ORDEM[d["severidade"]], -abs(d.get("desvio_pct") or 0)))
        causas, vistas = [], set()
        for v, sev, _ in itens:
            c, a = causa_acao(e, v, p.valor(e.id, v.id, m))
            if c not in vistas:
                vistas.add(c)
                causas.append({"causa": c, "acao": a})
        if tend and e.id == "F6" and not any(c["causa"].startswith("Pré-cobble") for c in causas):
            causas.append({"causa": "Cobbles recorrentes (motivo registrado: instabilidade do looper F5–F6).",
                           "acao": "Investigar a vibração do F5 e o looper F5–F6 (relatorio_desvios mostra a cadeia)."})
        sevs_g = [d["severidade"] for d in desv] + (["alarme"] if eventos else []) + (["fora_da_faixa"] if tend else [])
        pior = min(sevs_g, key=q.SEV_ORDEM.__getitem__)
        cheio = bool(eq_id)  # um equipamento só: tudo; planta/linha: os 3 piores desvios e 2 causas
        g = {"eq": e.id, "severidade": pior, "n_desvios": len(desv),
             "desvios": desv if cheio else desv[:3], "causas_provaveis": causas if cheio else causas[:2]}
        if not cheio and len(desv) > 3:
            g["mais"] = f"+{len(desv) - 3}: verificar_parametros(id='{e.id}')"
        if eventos or tend:
            g["eventos"] = eventos + tend
        grupos.append(g)
    grupos.sort(key=lambda g: (q.SEV_ORDEM[g["severidade"]],
                               -sum(d["severidade"] == "alarme" for d in g["desvios"]), -g["n_desvios"]))
    for g in grupos:
        if not g["desvios"]:
            g.pop("desvios")
    out = {"hora": p.ts_iso(m), "escopo": eq_id.upper() if eq_id else (cat.LINHAS[n] if n else "planta inteira"),
           "equipamentos_com_desvio": len(grupos), "contagem": cont,
           "equipamentos": grupos[:max_equipamentos]}
    if len(grupos) > max_equipamentos:
        out["nota"] = f"mostrando {max_equipamentos} de {len(grupos)} equipamentos; filtre por id ou linha"
    if lp is not None:
        out["linha_parada"] = {"equip": lp.equip, "motivo": lp.motivo, "desde": p.ts_iso(lp.inicio),
                               "nota": "variáveis de processo sem leitura enquanto a linha está parada"}
    return out


# ------------------------------------------------------------------ relatório falado
FALADO = {"FRN-01": "forno 1", "FRN-02": "forno 2", "DSC-01": "descarepador primário", "R1": "desbastador R1",
          "CB-01": "coil box", "TES-01": "tesoura de pontas", "DSC-02": "descarepador do acabador",
          "MED-01": "medidor de espessura", "ROT-01": "mesa de resfriamento", "BOB-01": "bobinadeira 1",
          "BOB-02": "bobinadeira 2", **{f"F{i}": f"cadeira F{i}" for i in range(1, 7)}}


def _nome_falado(v: cat.Var) -> str:
    import re
    n = v.nome.replace(" [E]", "")
    n = re.sub(r"\s*\([^)]*[0-9|][^)]*\)", "", n)
    n = re.sub(r"^T ", "temperatura ", n).replace("ΔT", "delta T").replace("ΔF", "diferença de força")
    n = n.replace("O₂", "oxigênio").replace("F5–F6", "F5 F6")
    return n[0].lower() + n[1:]


def _f(x: float, casas: int = 1) -> str:
    s = f"{x:.{casas}f}" if casas else f"{round(x):d}"
    return s.replace(".", ",")


def _ligacoes(p: Planta, m: int, w0: float) -> list[dict]:
    lig = []
    bob = [b for b in p.bobinas if b.inicio >= w0 and b.fim <= m + 1]

    # 1. forno com zona/queimador → placa fria → R1 e FDT
    for f in ("FRN-01", "FRN-02"):
        e = cat.POR_ID[f]
        zonas = [v for v in e.variaveis if v.id.startswith("t_zona_") and q.classe(p, e, v, m)[0] == "alarme"]
        trip = p.valor(f, "queimadores_em_trip", m) or 0
        if not zonas and not trip:
            continue
        outro = "FRN-02" if f == "FRN-01" else "FRN-01"
        ini = max(w0, q.inicio_desvio(p, e, zonas[0] if zonas else e.var("queimadores_em_trip"), m) + 60)
        forca = {f: [], outro: []}
        for mm in range(int(ini), m + 1):
            b, x = p.bobina_em(mm), p.valor("R1", "forca_laminacao", mm)
            if b is not None and x is not None:
                forca[b.forno].append(x)
        fd = {k: [b.fdt for b in bob if b.forno == k and b.inicio >= ini and b.status != "sucata"] for k in (f, outro)}
        if not (forca[f] and forca[outro] and fd[f] and fd[outro]):
            continue
        dforca = (mean(forca[f]) / mean(forca[outro]) - 1) * 100
        dfdt = mean(fd[f]) - mean(fd[outro])
        desenf = p.ultimo_valido(f, "t_desenfornamento", m)[0]
        gas = [p.valor(k, "consumo_especifico", m) for k in (f, outro)]
        z = zonas[0] if zonas else None
        txt_z = f"{z.nome.replace('T zona ', 'zona ')} em {_f(p.valor(f, z.id, m), 0)} graus" if z else "queimador em trip"
        lig.append({
            "cadeia": [f, "R1", "MED-01"],
            "texto": f"{f}: {'queimador em trip, ' if trip else ''}{txt_z}; placas saem a {_f(desenf, 0)} graus, "
                     f"a força do R1 sobe {_f(dforca, 0)} por cento e a FDT cai {_f(-dfdt, 0)} graus nas placas dele.",
            "curto": f"No {FALADO[f]}, queimador em trip deixa as placas frias: o R1 faz {_f(dforca, 0)} por cento "
                     f"mais força e a FDT cai {_f(-dfdt, 0)} graus.",
            "evidencias": {"t_desenfornamento_c": desenf, "forca_r1_vs_outro_forno_pct": round(dforca, 1),
                           "fdt_vs_outro_forno_c": round(dfdt, 1), "gas_gj_t": {f: gas[0], outro: gas[1]}}})

    # 2. descarepador com pressão baixa → carepa
    for d in ("DSC-01", "DSC-02"):
        e = cat.POR_ID[d]
        sev = q.classe(p, e, e.var("pressao_header"), m)[0]
        if sev not in ("alarme", "fora_da_faixa"):
            continue
        ini = q.inicio_desvio(p, e, e.var("pressao_header"), m)
        antes = [b for b in bob if b.fim <= ini]
        depois = [b for b in bob if b.inicio >= ini]
        taxa = lambda bs: 100 * sum("carepa_secundaria" in b.defeitos for b in bs) / len(bs) if bs else 0  # noqa: E731
        bomba = max(("corrente_bomba_1", "corrente_bomba_2"), key=lambda v: abs((p.valor(d, v, m) or 0) - 87.5))
        lig.append({
            "cadeia": [d, "MED-01"],
            "texto": f"{d}: pressão caiu para {_f(p.valor(d, 'pressao_header', m), 0)} bar, com a "
                     f"{bomba.replace('corrente_', '').replace('_', ' ')} anômala; carepa secundária em "
                     f"{_f(taxa(depois), 0)} por cento das bobinas, contra {_f(taxa(antes), 0)} antes.",
            "curto": f"No {FALADO[d]}, a pressão caiu para {_f(p.valor(d, 'pressao_header', m), 0)} bar e a carepa "
                     f"aparece em {_f(taxa(depois), 0)} por cento das bobinas.",
            "evidencias": {"pressao_bar": p.valor(d, "pressao_header", m), "desde": p.ts(ini).strftime("%H:%M"),
                           bomba + "_pct": p.valor(d, bomba, m),
                           "carepa_pct_depois": round(taxa(depois)), "carepa_pct_antes": round(taxa(antes))}})

    # 3. chatter na cadeira i → looper i–i+1 → cobbles na cadeira i+1
    for i in range(1, 6):
        e = cat.POR_ID[f"F{i}"]
        vib, _ = p.ultimo_valido(e.id, "vibracao", m)
        if vib is None or vib <= e.var("vibracao").alarme_hi:
            continue
        amp, _ = p.ultimo_valido(e.id, "amplitude_oscilacao_looper", m)
        fq, _ = p.ultimo_valido(e.id, "freq_pico_vibracao", m)
        cob = [x for x in p.paradas if x.equip == f"F{i + 1}" and x.categoria == "cobble" and w0 <= x.inicio <= m]
        c = q.correlacionar(p, e.id, "vibracao", e.id, "amplitude_oscilacao_looper", int(m - w0))
        km = p.km(e.id, m)
        txt = (f"F{i}: chatter com vibração de {_f(vib)} milímetros por segundo em {_f(fq, 0)} hertz, cilindro com "
               f"{_f(km, 0)} de {cat.CAMPANHA_KM[e.id]} quilômetros; o looper F{i}–F{i + 1} oscila "
               f"{_f(amp, 0)} graus")
        if cob:
            txt += f" e houve {len(cob)} cobbles no F{i + 1}, {_f(sum(x.duracao for x in cob), 0)} minutos parados."
        else:
            txt += "."
        curto = (f"A cadeira F{i} está com chatter e cilindro no fim da campanha; isso desestabiliza o looper"
                 + (f" e causou {len(cob)} cobbles no F{i + 1}." if cob else "."))
        lig.append({"cadeia": [e.id, f"looper F{i}–F{i + 1}", f"F{i + 1}"] + (["MED-01"] if i >= 4 else []),
                    "texto": txt, "curto": curto,
                    "evidencias": {"vibracao_mm_s": vib, "freq_hz": fq, "km": round(km, 1),
                                   "amplitude_looper_graus": amp, "cobbles": len(cob),
                                   "r_vibracao_x_looper": c.get("r_pearson"),
                                   "oscilacao_espessura_um": p.ultimo_valido("MED-01", "amplitude_oscilacao_espessura", m)[0]}})

    # 4. banco da mesa com vazão baixa → CT alta no aço que usa a mesa toda
    rot = cat.POR_ID["ROT-01"]
    for v in rot.variaveis:
        if not v.id.startswith("vazao_banco_") or q.classe(p, rot, v, m)[0] != "alarme":
            continue
        ini = q.inicio_desvio(p, rot, v, m)
        x = p.valor("ROT-01", v.id, m)
        por_aco = {}
        for aco in cat.CT_VISADA:
            bs = [b for b in bob if b.aco == aco and b.inicio >= ini and b.status != "sucata"]
            if bs:
                por_aco[aco] = (round(mean(b.erro_ct for b in bs), 1),
                                round(100 * sum(abs(b.erro_ct) > 20 for b in bs) / len(bs)))
        pior = max(por_aco, key=lambda k: por_aco[k][0]) if por_aco else None
        if pior is None or por_aco[pior][0] < 10:
            continue
        banco = int(v.id[-2:])
        lig.append({
            "cadeia": ["ROT-01", f"banco {banco}", f"bobinas {pior}"],
            "texto": f"Mesa de resfriamento: banco {banco} com vazão {_f((1 - x / v.setpoint) * 100, 0)} por cento "
                     f"abaixo do setpoint; a CT das bobinas {pior} fica {_f(por_aco[pior][0], 0)} graus acima da visada.",
            "curto": f"Na mesa de resfriamento, o banco {banco} está entupido e a CT do {pior} sai "
                     f"{_f(por_aco[pior][0], 0)} graus acima.",
            "evidencias": {"vazao_m3h": x, "setpoint_m3h": v.setpoint, "desde": p.ts(ini).strftime("%H:%M"),
                           "erro_ct_medio_c_e_pct_fora_20_por_aco": por_aco}})
    return lig


def relatorio_desvios(p: Planta, periodo_horas: float = 8) -> dict:
    m = p.garantir()
    w0 = max(0, m - periodo_horas * 60)
    ver = verificar_parametros(p, incluir_atencao=False, max_equipamentos=17)
    res = q.resumo_producao(p)
    lig = _ligacoes(p, m, w0)
    par = q.paradas(p, periodo_horas)

    itens = []
    for g in ver["equipamentos"]:
        partes = []
        for d in g.get("desvios", [])[:2]:
            v = cat.POR_ID[g["eq"]].var(d["var"])
            val = d["valor"]
            if val is None:
                continue
            c = min(v.casas, 1)
            ideal = f", ideal {_f(v.ideal, c)}" if v.ideal is not None and v.sentido == "alvo" else ""
            ideal = f", ideal até {_f(v.ideal + v.tol_ideal, c)}" if v.sentido == "menor" else ideal
            partes.append(f"{_nome_falado(v)} em {_f(val, c)} {_unidade_falada(v.unidade)}{ideal}".replace("  ", " "))
        for ev in g.get("eventos", [])[:1]:
            partes.append(ev[0].lower() + ev[1:].split(" (")[0])
        nome = FALADO[g["eq"]]
        texto = (nome[0].upper() + nome[1:] + ": " + "; ".join(partes) + ".") if partes else f"{nome}: {g['severidade']}."
        tend = g["desvios"][0]["tendencia"] if g.get("desvios") else "estavel"
        if tend == "piorando":
            texto = texto[:-1] + ", piorando."
        itens.append({"severidade": g["severidade"], "eq": g["eq"], "texto": texto})
    itens = itens[:8]

    from . import clp as clpm

    vermelhos = [e.id for e in cat.EQUIPAMENTOS if "vermelho" in clpm.ler_clp(p, e, m)["lanterna"]]
    n_al = sum(g["severidade"] == "alarme" for g in ver["equipamentos"])
    topo = par["por_equipamento"][0] if par["por_equipamento"] else None
    frases = [
        f"Turno com {_f(res['atingimento_pct'], 0)} por cento da meta de produção, OEE de {_f(res['oee_area']['oee'], 0)} "
        f"por cento e rendimento metálico de {_f(res['rendimento_metalico_pct'])} por cento.",
        f"{ver['equipamentos_com_desvio']} equipamentos fora dos parâmetros, {n_al} em alarme.",
    ]
    if vermelhos:
        frases.append(f"Lanterna vermelha no CLP de: {', '.join(FALADO[x] for x in vermelhos)}.")
    if topo:
        frases.append(f"Quem mais parou foi a {FALADO[topo['equip']]}: {topo['n']} paradas, "
                      f"{_f(topo['minutos'], 0)} minutos." if FALADO[topo["equip"]].startswith(("cadeira", "mesa", "coil", "tesoura", "bobinadeira"))
                      else f"Quem mais parou foi o {FALADO[topo['equip']]}: {topo['n']} paradas, {_f(topo['minutos'], 0)} minutos.")
    frases += [x["curto"] for x in lig[:4]]
    return {
        "hora": p.ts_iso(m), "periodo_horas": periodo_horas,
        "resumo_falado": " ".join(frases),
        "ligacoes": lig,
        "itens": itens,
        "clp_lanterna_vermelha": vermelhos,
        "indicadores": {"producao_t": res["producao_t"], "meta_t": res["meta_t"],
                        "atingimento_pct": res["atingimento_pct"], "oee_pct": res["oee_area"]["oee"],
                        "rendimento_pct": res["rendimento_metalico_pct"], "ct_dentro_20_pct": res["ct_dentro_20_pct"],
                        "min_linha_parada": res["minutos_linha_parada"]},
    }


_UNIDADES = {"°C": "graus", "°": "graus", "mm/s RMS": "milímetros por segundo", "mm/s": "milímetros por segundo",
             "%": "por cento", "% nominal": "por cento da nominal", "% seco": "por cento", "m³/h": "metros cúbicos por hora",
             "km": "quilômetros", "µm": "mícrons", "kN": "quilonewtons", "MN": "meganewtons", "Hz": "hertz",
             "GJ/t": "gigajoules por tonelada", "un": "", "mm": "milímetros", "t": "toneladas", "MPa": "megapascal",
             "°C/s": "graus por segundo", "kN/mancal": "quilonewtons por mancal", "mm/10 m": "milímetros a cada 10 metros"}


def _unidade_falada(u: str) -> str:
    return _UNIDADES.get(u, u)
