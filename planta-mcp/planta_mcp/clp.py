"""CLP padrão da usina (fictício): um por máquina, mesmo perfil para todo tipo de equipamento.

Inspirado em padrões públicos:
- PackML / ANSI/ISA-TR88.00.02 (OMAC): estados da máquina, modos e tags de alarme (Admin.Alarm[#]: ID, Value,
  Message, Category, DateTime);
- IEC 60073: cores da lanterna (vermelho = falha/intervenção, amarelo = condição anormal, verde = normal,
  azul = ação obrigatória/manutenção).

O CLP NÃO diagnostica: ele acende a lanterna, liga bits de área (0/1) nas palavras de falha e de aviso e registra
códigos de alarme com o tag (endereço) que disparou. Quem interpreta é o agente, consultando a documentação
(consultar_documentacao_equipamento_ltq) e os dados (verificar_parametros, historico).
"""

from __future__ import annotations

from . import catalogo as cat
from . import consultas as q
from .sim import EQUIP_LINHA, Planta

PERFIL = "CLP padrão da usina — perfil PackML (ISA-TR88.00.02), lanterna IEC 60073 (fictício)"

# ------------------------------------------------------------------ áreas padronizadas (bit da palavra de 16 bits)
AREAS: list[tuple[int, str, str]] = [
    (0, "ACIONAMENTO", "Motores, inversores e bombas: corrente, torque, velocidade."),
    (1, "HIDRAULICA", "Sistemas hidráulicos: AGC, viga caminhante, mandril."),
    (2, "LUBRIFICACAO", "Lubrificação e temperatura de mancais."),
    (3, "AGUA", "Água de processo e refrigeração: vazões, temperatura, skids, bancos da mesa."),
    (4, "TERMICA", "Temperaturas do material e de processo: zonas, placa, esboço, FDT, CT."),
    (5, "COMBUSTAO", "Queimadores, chama, O₂/CO, pressão do forno, consumo de gás."),
    (6, "MECANICA_VIBRACAO", "Vibração e frequência de vibração da estrutura e dos mancais."),
    (7, "POSICAO_GEOMETRIA", "Gap, guias, looper, camber, simetria entre lados, posição de rolos e lâminas."),
    (8, "INSTRUMENTACAO", "Saúde de sensores e medidores, calibração, desvio de modelo."),
    (9, "QUALIDADE", "Espessura, perfil, planicidade, erro de CT, telescopia."),
    (10, "SEGURANCA", "Emergências e intertravamentos de segurança."),
    (11, "COMUNICACAO", "Comunicação do CLP com remotas e com o nível 2."),
    (12, "MATERIAL_FLUXO", "Fluxo de material: ritmo, tempos de ciclo, cobble, sem material."),
    (13, "PRESSAO_FLUIDO", "Pressão de água/fluido de processo: descarepação, acumulador, filtros, headers."),
    (14, "FORCA_CARGA", "Força de laminação, tensões e cargas."),
    (15, "CAMPANHA_MANUTENCAO", "Manutenção requerida: campanha de cilindros e componentes."),
]
AREA_NOME = {b: n for b, n, _ in AREAS}
AREA_BIT = {n: b for b, n, _ in AREAS}

# ------------------------------------------------------------------ códigos de alarme (iguais em todo CLP): AAKK
TIPOS: dict[int, tuple[str, str]] = {
    1: ("alarme", "Valor analógico abaixo do limite de alarme"),
    2: ("alarme", "Valor analógico acima do limite de alarme"),
    11: ("aviso", "Valor analógico abaixo da faixa normal"),
    12: ("aviso", "Valor analógico acima da faixa normal"),
    50: ("alarme", "Entrada digital de falha ativa (trip / falha de dispositivo)"),
    60: ("alarme", "Parada por material: cobble, sucata ou falha de transferência"),
    61: ("aviso", "Parada operacional ou ajuste em andamento"),
    70: ("aviso", "Manutenção requerida: campanha acima de 90 % do limite"),
}

ESTADOS_PACKML = {
    "Execute": "produzindo",
    "Suspended": "parada por condição externa (linha parada por outro equipamento)",
    "Held": "pausada por condição interna (ajuste)",
    "Stopped": "parada controlada (manutenção programada)",
    "Aborted": "parada anormal (falha, cobble)",
}

_INSTRUMENTACAO = {"desvio_modelo_n2", "tensao_tubo_kv", "corrente_tubo_ma", "t_cabecote", "desvio_calibracao"}
_COMBUSTAO = {"queimadores_em_trip", "o2_fumos", "co_fumos", "pressao_forno", "consumo_especifico",
              "t_fumos_pos_recuperador"}
_TERMICA = {"t_desenfornamento", "t_placa_entrada", "t_esboco_saida", "t_entrada", "t_saida", "dt_cabeca_cauda",
            "fdt", "gradiente_borda_centro", "dt_skid_mark", "ct_visada", "ct_medida", "taxa_resf_laminar",
            "taxa_resf_intensivo"}
_AGUA = {"t_agua_skids_entrada", "dt_agua_skids", "t_agua", "vazao_total", "vazao_ciclo"}
_PRESSAO = {"pressao_header", "pressao_header_laminar", "pressao_header_intensivo", "nivel_acumulador", "dp_filtro"}
_HIDRAULICA = {"pressao_hidraulica_viga", "pressao_agc", "pressao_expansao_mandril"}
_ACIONAMENTO = {"corrente_motor", "corrente_bomba_1", "corrente_bomba_2", "torque", "velocidade", "tempo_corte"}
_VIBRACAO = {"vibracao", "vibracao_mancais", "freq_pico_vibracao"}
_GEOMETRIA = {"gap", "delta_forca_lados", "camber", "angulo_looper", "amplitude_oscilacao_looper", "bending",
              "shifting_cvc", "desvio_posicao_laminas", "erro_posicao_wrapper", "assimetria_gap_pinch",
              "comprimento_desponte"}
_FORCA = {"forca_laminacao", "forca_edger", "tensao_entre_cadeiras", "tensao_bobinamento", "forca_pinch_lo",
          "forca_pinch_la"}
_QUALIDADE = {"desvio_espessura", "amplitude_oscilacao_espessura", "coroa_c40", "cunha", "sobrelargura",
              "planicidade", "erro_ct", "telescopia"}
_MATERIAL = {"ritmo_desenfornamento", "tempo_residencia", "ciclos_corte", "tempo_enrol_desenrol",
             "diametro_bobina", "peso_bobina"}


def area_de(v: cat.Var) -> int:
    i = v.id
    for conj, area in ((_INSTRUMENTACAO, 8), (_COMBUSTAO, 5), (_TERMICA, 4), (_AGUA, 3), (_PRESSAO, 13),
                       (_HIDRAULICA, 1), (_ACIONAMENTO, 0), (_VIBRACAO, 6), (_GEOMETRIA, 7), (_FORCA, 14),
                       (_QUALIDADE, 9), (_MATERIAL, 12)):
        if i in conj:
            return area
    if i.startswith("t_zona_"):
        return 4
    if i.startswith("vazao_banco_"):
        return 3
    if i == "km_campanha_cilindro":
        return 15
    if i == "t_mancal_wrapper":
        return 2
    raise KeyError(f"variável sem área no CLP: {i}")


def clp_id(eq_id: str) -> str:
    return f"CLP-{eq_id}"


def tags(e: cat.Equip) -> list[dict]:
    """Mapa de E/S do CLP da máquina: entradas analógicas AInnn e digitais DInn, na ordem do catálogo."""
    out, ai, di = [], 0, 0
    for v in e.variaveis:
        if v.id == "queimadores_em_trip":
            di += 1
            tag = f"DI{di:02d}"
        else:
            ai += 1
            tag = f"AI{ai:03d}"
        out.append({"tag": tag, "var": v.id, "area": AREA_NOME[area_de(v)]})
    return out


def _tag_de(e: cat.Equip) -> dict[str, str]:
    return {t["var"]: t["tag"] for t in tags(e)}


def codigo(area: int, tipo: int) -> str:
    return f"{area:02d}{tipo:02d}"


def _inicio_anormal(p: Planta, e: cat.Equip, v: cat.Var, m: int) -> int:
    s = p.series[(e.id, v.id)]
    ini, ok = m, 0
    for mm in range(m, max(-1, m - 1440), -1):
        if s[mm] is None:
            continue
        if q.classe(p, e, v, mm)[0] in ("alarme", "fora_da_faixa"):
            ini, ok = mm, 0
        else:
            ok += 1
            if ok > 3:
                break
    return ini


def ler_clp(p: Planta, e: cat.Equip, m: int) -> dict:
    """Estado do CLP da máquina no minuto m (o que o supervisório mostraria)."""
    tg = _tag_de(e)
    alarmes = []
    for v in e.variaveis:
        cls, _ = q.classe(p, e, v, m)
        x = p.valor(e.id, v.id, m)
        area = area_de(v)
        if v.id == "queimadores_em_trip":
            if x:
                alarmes.append((area, 50, tg[v.id], _inicio_anormal(p, e, v, m)))
            continue
        if v.id == "km_campanha_cilindro":
            lim = v.faixa[1]
            if x is not None and x > 0.9 * lim:
                ini = m
                while ini > 0 and p.km(e.id, ini - 1) > 0.9 * lim:
                    ini -= 1
                alarmes.append((area, 2 if x > lim else 70, tg[v.id], ini))
            continue
        if cls not in ("alarme", "fora_da_faixa") or x is None:
            continue
        ref = v.ideal if v.ideal is not None else (sum(t for t in v.faixa if t is not None) / 2)
        baixo = x < ref
        tipo = (1 if baixo else 2) if cls == "alarme" else (11 if baixo else 12)
        alarmes.append((area, tipo, tg[v.id], _inicio_anormal(p, e, v, m)))
    estado, modo = "Execute", "Produção"
    for par in p.paradas_ativas(m):
        if par.equip == e.id:
            if par.tipo == "programada":
                estado, modo = "Stopped", "Manutenção"
            elif par.categoria in ("cobble", "mecanica"):
                estado = "Aborted"
                alarmes.append((12, 60, "DI90", int(par.inicio)))
            else:
                estado = "Held"
                alarmes.append((12, 61, "DI91", int(par.inicio)))
    if estado == "Execute" and e.id in EQUIP_LINHA and p.linha_parada(m) is not None:
        estado = "Suspended"

    falha = aviso = 0
    lista = []
    for area, tipo, tag, ini in sorted(alarmes, key=lambda a: (TIPOS[a[1]][0] != "alarme", a[0], a[2])):
        cat_ = TIPOS[tipo][0]
        if cat_ == "alarme":
            falha |= 1 << area
        else:
            aviso |= 1 << area
        lista.append({"id": codigo(area, tipo), "categoria": cat_, "area": AREA_NOME[area], "tag": tag,
                      "mensagem": TIPOS[tipo][1], "desde": p.ts(ini).strftime("%H:%M")})
    acesas = []
    if falha:
        acesas.append("vermelho")
    if aviso & ~(1 << 15):
        acesas.append("amarelo")
    if aviso & (1 << 15) or estado == "Stopped":
        acesas.append("azul")
    if estado == "Execute" and not falha:
        acesas.append("verde")
    return {"clp": clp_id(e.id), "eq": e.id, "estado": estado, "modo": modo, "lanterna": acesas,
            "palavra_falha": falha, "palavra_aviso": aviso,
            "bits_falha": f"{falha:016b}", "bits_aviso": f"{aviso:016b}",
            "areas_falha": [AREA_NOME[b] for b in range(16) if falha >> b & 1],
            "areas_aviso": [AREA_NOME[b] for b in range(16) if aviso >> b & 1],
            "alarmes": lista}


# ------------------------------------------------------------------ consultas
def status_clp(p: Planta, eq_id: str | None = None) -> dict:
    m = p.garantir()
    if eq_id:
        e = cat.equip(eq_id)
        d = ler_clp(p, e, m)
        d["hora"] = p.ts_iso(m)
        d["como_ler"] = ("bits_*: bit 0 à direita; cada bit é uma área padronizada (ver areas_falha). "
                         "Para entender um alarme: consultar_documentacao_equipamento_ltq(id, codigo ou tag).")
        return d
    acesos, verdes = [], []
    for e in cat.EQUIPAMENTOS:
        d = ler_clp(p, e, m)
        if d["lanterna"] == ["verde"]:
            verdes.append(e.id)
            continue
        acesos.append({k: d[k] for k in ("clp", "eq", "estado", "lanterna", "palavra_falha", "palavra_aviso",
                                          "areas_falha", "areas_aviso")} | {"n_alarmes": len(d["alarmes"])})
    acesos.sort(key=lambda d: ("vermelho" not in d["lanterna"], "amarelo" not in d["lanterna"], d["eq"]))
    return {"hora": p.ts_iso(m), "perfil": PERFIL, "clps_com_sinal": acesos, "clps_verde": verdes,
            "proximo_passo": "status_clp(id) para os códigos e tags; consultar_documentacao_equipamento_ltq(id, codigo/tag) para o significado"}
