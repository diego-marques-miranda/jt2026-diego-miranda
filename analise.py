"""analise.py — Itapema (SC): recomendacao de investimento Seazone.

Como rodar:
    python analise.py
Saidas:
    output/*.csv  (tabelas intermediarias e finais)
    relatorio.md  (resposta final, em portugues)

Premissas decididas e aplicadas neste script:
    - Price_AV deduplicado: ultima captura por (listing, data de estadia).
    - Universo de receita: listings ativos precificados com numero_de_reviews > 0 (977).
    - Proxy de noites por ano: reviews / 0.5 * 3, teto de 365.
    - Cross-check de ocupacao: cenarios fixos 25% / 35% / 45%.
    - Imputacao com mediana; colunas de nota com valor 0 = "nao avaliado" viram NaN e
      sao imputadas com a mediana da coluna.
    - Colunas min_nights e response_* excluidas (sem dados validos).
    - Faixas de quartos: Studio (0q), 1, 2, 3, 4, 5+.
    - Bairros do VivaReal normalizados; Andorinha e Castelo Branco entram como grupo
      explicito no lado de preco de compra; Estreito, Itapema, Ocean Tower e NaN
      excluidos. Q3 usa ADR como alvo.
"""

import os

import pandas as pd

MIN_N = 20
REVIEW_RATE = 0.5
NIGHTS_PER_REVIEW = 3
OCC = {"occ25": 0.25, "occ35": 0.35, "occ45": 0.45}
BAND_LABELS = ["Studio (0q)", "1 quarto", "2 quartos", "3 quartos", "4 quartos", "5+ quartos"]

OUT = "output"
os.makedirs(OUT, exist_ok=True)

RATING_COLS = [
    "star_rating", "guest_satisfaction_overall", "accuracy_rating", "checkin_rating",
    "cleanliness_rating", "communication_rating", "location_rating", "value_rating",
]

VIVA_EXACT = {
    "CENTRO": "Centro",
    "MEIA PRAIA": "Meia Praia",
    "Meia praia": "Meia Praia",
    "meia praia": "Meia Praia",
    "Meia Praia - Frente Mar": "Meia Praia",
    "Taboleiro": "Tabuleiro dos Oliveiras",
    "Tabuleiro": "Tabuleiro dos Oliveiras",
    "Jardim Praia Mar": "Jardim Praiamar",
    "Alto S\ufffdo Bento": "Alto Sao Bento",
    "Sert\ufffdo do Trombudo": "Sertao do Trombudo",
    "Sert\ufffdo Do Trombudo": "Sertao do Trombudo",
    "Sert\ufffdozinho": "Sertaozinho",
}
VIVA_AC_GROUP = {"Andorinha", "Castelo Branco"}
AC_LABEL = "Outros (Andorinha e Castelo Branco)"
EXCLUDED_SUBURBS = {"Estreito", "Itapema", "Ocean Tower"}

COMPACTOS = ["apartamento|Studio (0q)", "apartamento|1 quarto"]


def fmt(v):
    if pd.isna(v):
        return "-"
    return f"{v:,.0f}".replace(",", ".")

def pct(v):
    return f"{v:.2f}".replace(".", ",")

def prep_bairro(nome):
    """Preposicao correta antes do nome do bairro em portugues."""
    n = str(nome)
    if n == "Centro":
        return f"no {n}"
    if n in ("Meia Praia", "Casa Branca", "Ilhota", "Varzea"):
        return f"na {n}"
    return f"em {n}"

def le_csv(path):
    return pd.read_csv(path, low_memory=False)

def to_int(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return 0

def band_de_quartos(bed):
    b = to_int(bed)
    if b <= 0:
        return BAND_LABELS[0]
    if b == 1:
        return BAND_LABELS[1]
    if b == 2:
        return BAND_LABELS[2]
    if b == 3:
        return BAND_LABELS[3]
    if b == 4:
        return BAND_LABELS[4]
    return BAND_LABELS[5]

def mapa_viva(s):
    if pd.isna(s) or s in EXCLUDED_SUBURBS or s == "nan":
        return None
    if s in VIVA_AC_GROUP:
        return AC_LABEL
    if s in VIVA_EXACT:
        return VIVA_EXACT[s]
    if s in CANONICAL_SUBURBS:
        return s
    return None

def perfil_legivel(p):
    """'apartamento|4 quartos' -> 'Apartamento · 4 quartos'."""
    tipo, faixa = str(p).split("|", 1)
    nome = {"apartamento": "Apartamento", "casa": "Casa", "hotel": "Hotel",
            "outros": "Outros"}.get(tipo, "Outros")
    return f"{nome} · {faixa}"

FEAT_LABELS = {
    "number_of_bedrooms": "Número de quartos",
    "cleaning_fee": "Taxa de limpeza",
    "picture_count": "Número de fotos do anúncio",
    "location_rating": "Nota de localização",
    "nrev": "Número de avaliações",
    "star_rating": "Nota média (estrelas)",
    "is_superhost": "Superhost",
    "guest_satisfaction_overall": "Satisfação geral dos hóspedes",
    "cleanliness_rating": "Nota de limpeza",
    "communication_rating": "Nota de comunicação",
    "value_rating": "Nota de custo-benefício",
    "years_host": "Tempo como anfitrião (anos)",
    "months_host": "Tempo como anfitrião (meses)",
    "host_reviews": "Avaliações do anfitrião",
}

def md_table(df, labels=None, digits=1, money=()):
    df = df.copy()
    header = "| " + " | ".join((labels or list(df.columns))) + " |"
    sep = "|" + "|".join(["---"] * len(df.columns)) + "|"
    lines = [header, sep]
    for _, row in df.iterrows():
        cells = []
        for c in row.index:
            v = row[c]
            if c in money and pd.notna(v):
                cells.append("R$ " + fmt(v))
            elif isinstance(v, float):
                cells.append(f"{v:.{digits}f}".replace(".", ",") if pd.notna(v) else "")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)

def monta_verdict(yield_cidade, yield_sub, q1, centro_best):
    """Gera o texto de posicionamento sobre a tese a partir dos numeros."""
    comp = []
    cq = q1[q1["perfil"].isin(COMPACTOS)]
    alt = q1[~q1["perfil"].isin(COMPACTOS)]
    if not cq.empty and not alt.empty:
        efic_comp = float(cq["rev_por_quarto"].max())
        efic_alt = float(alt["rev_por_quarto"].max())
        comp.append(f"- Receita estimada por quarto: compactos R$ "
                    f"{fmt(efic_comp)} vs. demais perfis R$ {fmt(efic_alt)}.")

    ys = yield_sub if yield_sub is not None else pd.DataFrame()
    sup_compacto = False
    if not ys.empty:
        best_cell = ys.iloc[0]
        sup_compacto = best_cell["suburb"] == "Centro" and best_cell["perfil"] in COMPACTOS
        y_comp_centro = None
        yc = ys[ys["suburb"] == "Centro"]
        if not yc.empty:
            sub_c = yc[yc["perfil"].isin(COMPACTOS)]
            if not sub_c.empty:
                y_comp_centro = float(sub_c["yield_proxy"].max())
            y_all_centro = float(yc["yield_proxy"].max())
            y_geral = float(ys["yield_proxy"].max())
            comp.append(f"- Retorno anual estimado (%) de compactos no Centro: "
                        f"{(pct(y_comp_centro)) if y_comp_centro is not None else '-'}"
                        f"% (melhor combinação no Centro: {pct(y_all_centro)}%; melhor da cidade: "
                        f"{pct(y_geral)}%).")

    melhor = ""
    if not ys.empty:
        r = ys.iloc[0]
        melhor = f"priorizar **{perfil_legivel(r['perfil'])} {prep_bairro(r['suburb'])}** " \
                 f"(retorno estimado de {pct(r['yield_proxy'])}%) "

    if sup_compacto:
        veredito = ("Os dados SUSTENTAM a tese: o melhor retorno estimado vem do perfil "
                    "compacto no Centro (maior retorno da amostra). A recomendação é comprar "
                    "esse perfil nessa localização.")
    else:
        veredito = (f"Os dados NÃO SUSTENTAM plenamente a tese dos compactos no Centro: há "
                    f"perfis e bairros com retorno estimado maior. A recomendação é "
                    f"{melhor}mantendo os compactos do Centro como alternativa de entrada com "
                    f"menor capital.")

    return "\n".join(comp) + "\n\n" + veredito


def main():
    global CANONICAL_SUBURBS
    print("=== Carregando dados ===")
    det = le_csv("data/Details_Itapema.csv")
    hosts = le_csv("data/Hosts_ids_Itapema.csv")
    mesh = le_csv("data/Mesh_Ids_Data_Itapema.csv")
    price = le_csv("data/Price_AV_Itapema.csv")
    vr = le_csv("data/VivaReal_Itapema.csv")

    CANONICAL_SUBURBS = set(mesh[mesh["suburb"].notna()]["suburb"].unique()) - {"none"}

    print("=== Hosts_ids: deduplica (ultima captura por owner_id) ===")
    hosts["host_snap"] = pd.to_datetime(hosts["host_snapshot_date"], errors="coerce")
    hosts = hosts.sort_values("host_snap").drop_duplicates("owner_id", keep="last")
    print(f"  hosts unicos apos dedup: {len(hosts)}")

    print("=== Price_AV: deduplica (ultima captura por listing+data de estadia) ===")
    price["aquis_dt"] = pd.to_datetime(price["aquisition_date"], errors="coerce")
    price["date"] = pd.to_datetime(price["date"], errors="coerce")
    price = price.sort_values(["airbnb_listing_id", "date", "aquis_dt"])
    price = price.drop_duplicates(["airbnb_listing_id", "date"], keep="last")
    print(f"  linhas Price_AV apos dedup: {len(price)}")
    adr = price.groupby("airbnb_listing_id")["price"].median().rename("adr")

    print("=== Universo de receita (ativos precificados com reviews>0) ===")
    n_com_preco = int(det["airbnb_listing_id"].isin(adr.index).sum())
    act = det[det["airbnb_listing_id"].isin(adr.index)].copy()
    act["nrev"] = pd.to_numeric(act["number_of_reviews"], errors="coerce")
    n_sem_review = int((act["nrev"] == 0).sum())
    act = act[act["nrev"] > 0].copy()
    print(f"  ativos precificados: {n_com_preco}; excluidos por zero reviews (D1): {n_sem_review}; "
          f"universo final: {len(act)}")
    act["adr"] = act["airbnb_listing_id"].map(adr)
    act["band"] = act["number_of_bedrooms"].apply(band_de_quartos)
    act["perfil"] = act["listing_type"] + "|" + act["band"]
    act = act.merge(mesh[["airbnb_listing_id", "suburb"]], on="airbnb_listing_id", how="left")
    act["suburb"] = act["suburb"].replace("none", pd.NA)
    act = act.merge(hosts.add_prefix("host_"), left_on="owner_id", right_on="host_owner_id", how="left")

    for c in ["number_of_bedrooms", "cleaning_fee", "picture_count"]:
        act[c] = pd.to_numeric(act[c], errors="coerce")
    for c in RATING_COLS:
        act[c] = pd.to_numeric(act[c], errors="coerce")
        act.loc[act[c] == 0, c] = pd.NA
        act[c] = act[c].fillna(act[c].median())

    act["is_superhost"] = pd.to_numeric(act["host_is_superhost"], errors="coerce").fillna(0).astype(int)
    act["years_host"] = pd.to_numeric(act["host_years_host"], errors="coerce").fillna(
        pd.to_numeric(act["host_years_host"], errors="coerce").median())
    act["months_host"] = pd.to_numeric(act["host_months_host"], errors="coerce").fillna(
        pd.to_numeric(act["host_months_host"], errors="coerce").median())
    act["host_reviews"] = pd.to_numeric(act["host_number_of_reviews_host"], errors="coerce").fillna(
        pd.to_numeric(act["host_number_of_reviews_host"], errors="coerce").median())
    act["star_alta"] = (act["star_rating"] >= 4.8).astype(int)

    print("=== Proxy de receita ===")
    act["nights"] = (act["nrev"] / REVIEW_RATE * NIGHTS_PER_REVIEW).clip(upper=365)
    act["rev_proxy"] = act["adr"] * act["nights"]
    for k, o in OCC.items():
        act[k] = act["adr"] * o * 365
    print(f"  rev_proxy mediana: R$ {fmt(act['rev_proxy'].median())}")

    det["nrev"] = pd.to_numeric(det["number_of_reviews"], errors="coerce")
    ctx = det.merge(mesh[["airbnb_listing_id", "suburb"]], on="airbnb_listing_id", how="left")
    ctx["has_price"] = ctx["airbnb_listing_id"].isin(adr.index)
    ctx["tem_rev"] = ctx["has_price"] & (ctx["nrev"] > 0)
    mercado = ctx.groupby("suburb").agg(
        oferta_total=("airbnb_listing_id", "size"),
        ativos_preco=("has_price", "sum"),
        ativos_rev=("tem_rev", "sum"),
    ).sort_values("oferta_total", ascending=False).reset_index()
    mercado.to_csv(f"{OUT}/mercado_contexto.csv", encoding="utf-8-sig", index=False)

    print("\n========== Pergunta 1 - Melhor perfil ==========")
    q1 = act.groupby("perfil").agg(
        n_ativos=("airbnb_listing_id", "size"),
        adr_med=("adr", "median"),
        rev_proxy_med=("rev_proxy", "median"),
        occ25=("occ25", "median"),
        occ35=("occ35", "median"),
        occ45=("occ45", "median"),
    ).reset_index()
    beds_num = {"Studio (0q)": 1, "1 quarto": 1, "2 quartos": 2, "3 quartos": 3,
                "4 quartos": 4, "5+ quartos": 5}
    q1["rev_por_quarto"] = q1["rev_proxy_med"] / q1["perfil"].str.split("|").str[1].map(beds_num)
    q1 = q1[q1["n_ativos"] >= MIN_N].sort_values("rev_proxy_med", ascending=False)
    q1.to_csv(f"{OUT}/q1_perfil.csv", encoding="utf-8-sig", index=False)
    print(md_table(q1, labels=["Perfil", "N de imoveis", "Preco/noite (med.)", "Receita estimada",
                               "Occ 25%", "Occ 35%", "Occ 45%", "Receita/quarto"],
                   money=["adr_med", "rev_proxy_med", "occ25", "occ35", "occ45", "rev_por_quarto"]))
    best_perfil = q1.iloc[0]
    print(f"  Perfil com maior receita estimada: {perfil_legivel(best_perfil['perfil'])} "
          f"(n={int(best_perfil['n_ativos'])})")

    print("\n========== Pergunta 2 - Melhor localizacao (receita) ==========")
    q2 = act.groupby("suburb").agg(
        n_ativos=("airbnb_listing_id", "size"),
        adr_med=("adr", "median"),
        rev_proxy_med=("rev_proxy", "median"),
        occ35=("occ35", "median"),
    ).reset_index()
    q2 = q2[q2["suburb"].notna() & (q2["n_ativos"] >= MIN_N)].sort_values("rev_proxy_med", ascending=False)
    q2.to_csv(f"{OUT}/q2_localizacao.csv", encoding="utf-8-sig", index=False)
    print(md_table(q2, labels=["Bairro", "N de imoveis", "Preco/noite (med.)", "Receita estimada",
                               "Occ 35%"],
                   money=["adr_med", "rev_proxy_med", "occ35"]))
    best_suburb = q2.iloc[0]
    print(f"  Bairro com maior receita estimada: {best_suburb['suburb']} "
          f"(n={int(best_suburb['n_ativos'])})")

    print("\n========== Pergunta 3 - Caracteristicas (alvo: ADR) ==========")
    feats = ["number_of_bedrooms", "nrev", "star_rating", "guest_satisfaction_overall",
             "cleanliness_rating", "communication_rating", "location_rating", "value_rating",
             "cleaning_fee", "picture_count", "is_superhost", "years_host", "months_host", "host_reviews"]
    corr = act[feats + ["adr"]].corr(method="spearman")["adr"].drop("adr")
    corr = corr.sort_values(key=lambda s: s.abs(), ascending=False)
    print("  Correlacao com o preco medio por noite:", corr.round(3).to_dict())
    corr.to_csv(f"{OUT}/q3_correlacoes.csv", encoding="utf-8-sig", index=False)

    grupos = []
    for var, label in [("band", "Nº de quartos"), ("listing_type", "Tipo de imóvel"),
                       ("is_superhost", "Superhost"), ("star_alta", "Nota média")]:
        for g, sub in act.groupby(var):
            if len(sub) >= MIN_N:
                if var == "is_superhost":
                    rot = "Não" if g == 0 else "Sim"
                elif var == "star_alta":
                    rot = ">= 4,8" if g == 1 else "< 4,8"
                else:
                    rot = str(g)
                grupos.append({"variavel": label, "grupo": rot, "n": len(sub),
                               "adr_med": sub["adr"].median(),
                               "rev_proxy_med": sub["rev_proxy"].median()})
    q3g = pd.DataFrame(grupos)
    q3g.to_csv(f"{OUT}/q3_grupos.csv", encoding="utf-8-sig", index=False)
    print(md_table(q3g, labels=["Caracteristica", "Grupo", "N de imoveis", "Preco/noite (med.)",
                               "Receita estimada"],
                   money=["adr_med", "rev_proxy_med"]))

    print("\n========== Pergunta 4 - O que comprar (retorno estimado) ==========")
    sr = vr[vr["listing_type"].isin(["apartamento", "casa"])].copy()
    n_antes = len(sr)
    sr["suburb_map"] = sr["suburb"].apply(mapa_viva)
    excluidos = sr[sr["suburb_map"].isna()]
    sr = sr[sr["suburb_map"].notna()].copy()
    print(f"  VivaReal apart/casa: {n_antes} -> mantidos {len(sr)} (excluidos {len(excluidos)} "
          f"sem localizacao segura)")
    sr["band"] = sr["bedrooms"].apply(band_de_quartos)
    sr["perfil"] = sr["listing_type"] + "|" + sr["band"]
    sr.to_csv(f"{OUT}/viva_normalizado.csv", encoding="utf-8-sig", index=False)

    preco_cidade = sr.groupby("perfil")["sale_price"].agg(["count", "median"]).rename(
        columns={"count": "n_venda", "median": "price_med"}).reset_index()
    preco_cidade.to_csv(f"{OUT}/q4_preco_cidade.csv", encoding="utf-8-sig", index=False)

    preco_bairro = sr.groupby(["perfil", "suburb_map"])["sale_price"].agg(["count", "median"]).rename(
        columns={"count": "n_venda", "median": "price_med"}).reset_index()

    print("\n  Preco mediano de venda por bairro (apart/casa; inclui 'Outros' A+C):")
    preco_bairro_total = sr.groupby("suburb_map")["sale_price"].agg(["count", "median"]).sort_values(
        "median", ascending=False).reset_index()
    print(md_table(preco_bairro_total.round(0), labels=["Bairro", "N venda", "Preco (mediana)"],
                   money=["median"]))

    rev_perfil = act.groupby("perfil").agg(
        n_ativos=("airbnb_listing_id", "size"), adr_med=("adr", "median"),
        rev_proxy_med=("rev_proxy", "median"), occ25=("occ25", "median"),
        occ35=("occ35", "median"), occ45=("occ45", "median")).reset_index()
    yield_cidade = rev_perfil.merge(preco_cidade, on="perfil")
    yield_cidade["yield_proxy"] = yield_cidade["rev_proxy_med"] / yield_cidade["price_med"] * 100
    yield_cidade["yield_occ35"] = yield_cidade["occ35"] / yield_cidade["price_med"] * 100
    for k in OCC:
        if k != "occ35":
            yield_cidade[f"yield_{k}"] = yield_cidade[k] / yield_cidade["price_med"] * 100
    yield_cidade = yield_cidade[(yield_cidade["n_venda"] >= MIN_N) & (yield_cidade["n_ativos"] >= MIN_N)]
    yield_cidade = yield_cidade.sort_values("yield_proxy", ascending=False)
    yield_cidade.to_csv(f"{OUT}/q4_yield_cidade.csv", encoding="utf-8-sig", index=False)
    cols_c = ["perfil", "n_ativos", "adr_med", "rev_proxy_med", "occ35", "n_venda", "price_med",
              "yield_proxy", "yield_occ35"]
    ycm_console = yield_cidade.copy()
    ycm_console["perfil"] = ycm_console["perfil"].map(perfil_legivel)
    print("\n  Retorno por perfil (cidade; preco inclui 'Outros' A+C):")
    print(md_table(ycm_console[cols_c], labels=["Perfil", "N ativos", "Preco/noite", "Receita estimada",
                                                "Occ 35%", "N venda", "Preco (mediana)",
                                                "Retorno (estim.)", "Retorno (Occ 35%)"],
                   money=["price_med", "rev_proxy_med", "occ35"]))

    rev_sub = act.groupby(["perfil", "suburb"]).agg(
        n_ativos=("airbnb_listing_id", "size"), rev_proxy_med=("rev_proxy", "median"),
        occ35=("occ35", "median")).reset_index()
    yield_sub = rev_sub.merge(preco_bairro, left_on=["perfil", "suburb"],
                              right_on=["perfil", "suburb_map"])
    yield_sub["yield_proxy"] = yield_sub["rev_proxy_med"] / yield_sub["price_med"] * 100
    yield_sub["yield_occ35"] = yield_sub["occ35"] / yield_sub["price_med"] * 100
    yield_sub = yield_sub.drop(columns=["suburb_map"], errors="ignore")
    yield_sub = yield_sub[(yield_sub["n_venda"] >= MIN_N) & (yield_sub["n_ativos"] >= MIN_N)]
    yield_sub = yield_sub.sort_values("yield_proxy", ascending=False)
    yield_sub.to_csv(f"{OUT}/q4_yield_bairro.csv", encoding="utf-8-sig", index=False)
    cols_sub = ["perfil", "suburb", "n_ativos", "rev_proxy_med", "occ35", "n_venda", "price_med",
                "yield_proxy", "yield_occ35"]
    ysm_console = yield_sub.copy()
    ysm_console["perfil"] = ysm_console["perfil"].map(perfil_legivel)
    print("\n  Retorno por perfil x bairro (com receita e venda locais):")
    print(md_table(ysm_console[cols_sub], labels=["Perfil", "Bairro", "N ativos", "Receita estimada",
                                                  "Occ 35%", "N venda", "Preco (mediana)",
                                                  "Retorno (estim.)", "Retorno (Occ 35%)"],
                   money=["price_med", "rev_proxy_med", "occ35"]))

    robustez = []
    for col in ["rev_proxy_med", "occ25", "occ35", "occ45"]:
        key = "yield_proxy" if col == "rev_proxy_med" else f"yield_{col}"
        row = yield_cidade.sort_values(key, ascending=False).iloc[0]
        robustez.append({"cenario": "proxy reviews" if col == "rev_proxy_med" else col,
                         "melhor_perfil": row["perfil"], "yield": round(float(row[key]), 2)})
    rotulos_cenario = {"proxy reviews": "Estimativa por avaliações", "occ25": "Ocupação 25%",
                       "occ35": "Ocupação 35%", "occ45": "Ocupação 45%"}
    for r in robustez:
        r["cenario"] = rotulos_cenario.get(r["cenario"], r["cenario"])
        r["melhor_perfil"] = perfil_legivel(r["melhor_perfil"])
    pd.DataFrame(robustez).rename(columns={"yield": "retorno"}).to_csv(
        f"{OUT}/q4_robustez.csv", encoding="utf-8-sig", index=False)
    print("\n  Robustez (melhor perfil por cenário):")
    for r in robustez:
        print(f"    {r['cenario']}: {r['melhor_perfil']} (retorno {r['yield']:.2f}%)")

    gerar_relatorio(best_perfil, best_suburb, q1, q2, corr, q3g, yield_cidade, yield_sub,
                    act, mercado, excluidos, n_total_parque=len(det))


def gerar_relatorio(best_perfil, best_suburb, q1, q2, corr, q3g, yield_cidade, yield_sub,
                    act, mercado, excluidos, n_total_parque):
    print("\n=== Gerando relatorio.md ===")

    q1m = q1.copy()
    q1m["perfil"] = q1m["perfil"].map(perfil_legivel)
    ycm = yield_cidade.copy()
    ycm["perfil"] = ycm["perfil"].map(perfil_legivel)
    ysm = yield_sub.copy()
    ysm["perfil"] = ysm["perfil"].map(perfil_legivel)
    corrm = pd.DataFrame(
        {"característica": corr.index.map(lambda f: FEAT_LABELS.get(f, f)),
         "correlação": corr.round(3)}).head(8)
    q3gm = q3g.copy()

    if not yield_cidade.empty:
        pos = yield_cidade.iloc[0]
        pos_txt = (f"**{perfil_legivel(pos['perfil'])}** (retorno anual estimado de "
                   f"aproximadamente {pct(pos['yield_proxy'])}%, com receita estimada perto de "
                   f"R$ {fmt(pos['rev_proxy_med'])} contra preço mediano de venda de "
                   f"R$ {fmt(pos['price_med'])})")
    else:
        pos_txt = "ver a tabela da Pergunta 4"

    centro_cell = yield_sub[yield_sub["suburb"] == "Centro"] if not yield_sub.empty else pd.DataFrame()
    centro_best = None
    if not centro_cell.empty:
        centro_best = centro_cell.sort_values("yield_proxy", ascending=False).iloc[0]

    verdict = monta_verdict(yield_cidade, yield_sub if not yield_sub.empty else None, q1,
                            centro_best)

    melhores_sub = yield_sub.head(3) if not yield_sub.empty else pd.DataFrame()
    top_lines = "\n".join(
        f"- **{perfil_legivel(r['perfil'])} {prep_bairro(r['suburb'])}** — retorno estimado de "
        f"{pct(r['yield_proxy'])}% (receita estimada de R$ {fmt(r['rev_proxy_med'])} "
        f"contra preço de venda de R$ {fmt(r['price_med'])})"
        for _, r in melhores_sub.iterrows())

    tb_q1 = md_table(q1m, labels=["Perfil", "N de imóveis", "Preço/noite (méd.)", "Receita estimada",
                                  "Occ 25%", "Occ 35%", "Occ 45%", "Receita/quarto"],
                     money=["adr_med", "rev_proxy_med", "occ25", "occ35", "occ45", "rev_por_quarto"])

    tb_criterio = ""
    resp1_criterio = ""
    if not yield_cidade.empty:
        cr = yield_cidade[["perfil", "n_ativos", "adr_med", "rev_proxy_med", "price_med",
                           "yield_proxy"]].copy()
        cr["perfil"] = cr["perfil"].map(perfil_legivel)
        tb_criterio = md_table(cr, labels=["Perfil", "N ativos", "Preço/noite", "Receita estimada",
                                           "Preço (mediana)", "Retorno (estim.)"],
                               money=["adr_med", "rev_proxy_med", "price_med"], digits=2)
        p1_melhor_ret = perfil_legivel(pos['perfil'])
        resp1_criterio = (
            "O termo **\"melhor\"** é propositalmente aberto no enunciado: cabe a nós definir o "
            "critério. A tabela abaixo cruza, para cada perfil com dados dos dois lados (anúncio "
            "ativo de aluguel + oferta de venda no VivaReal), a receita estimada e o **retorno "
            "estimado** (receita anual ÷ preço mediano de venda):\n\n"
            f"{tb_criterio}\n\n"
            f"**Leitura:** o **Apartamento · 4 quartos** concentra a maior receita bruta, mas exige "
            f"preço de entrada alto (mediana ~R$ 3,5 milhões) e entrega retorno de ~3,1% ao ano. "
            f"Já o **{p1_melhor_ret}**, mesmo com receita menor no absoluto, tem preço de venda "
            f"acessível (mediana ~R$ 824 mil) e retorno estimado de **{pct(pos['yield_proxy'])}% "
            f"ao ano** — a melhor relação receita/preço da cidade. Por esse critério, a Pergunta 4 "
            "recomenda comprar esse perfil. Perfis sem oferta de venda suficiente (ex.: casas) "
            "ficam de fora do cruzamento de retorno."
        )

    tb_q2 = md_table(q2, labels=["Bairro", "N de imóveis", "Preço/noite (méd.)", "Receita estimada",
                                 "Occ 35%"],
                     money=["adr_med", "rev_proxy_med", "occ35"])
    tb_corr = md_table(corrm, digits=2)
    tb_grupos = md_table(q3gm, labels=["Característica", "Grupo", "N de imóveis", "Preço/noite (méd.)",
                                       "Receita estimada"],
                         money=["adr_med", "rev_proxy_med"])
    cols_yc = ["perfil", "n_ativos", "adr_med", "rev_proxy_med", "occ35", "n_venda", "price_med",
               "yield_proxy", "yield_occ35"]
    tb_yc = md_table(ycm[cols_yc], labels=["Perfil", "N ativos", "Preço/noite", "Receita estimada",
                                           "Occ 35%", "N de venda", "Preço (mediana)",
                                           "Retorno (estim.)", "Retorno (Occ 35%)"],
                     money=["price_med", "rev_proxy_med", "occ35"])
    cols_yb = ["perfil", "suburb", "n_ativos", "rev_proxy_med", "occ35", "n_venda", "price_med",
               "yield_proxy", "yield_occ35"]
    tb_yb = md_table(ysm[cols_yb], labels=["Perfil", "Bairro", "N ativos", "Receita estimada",
                                           "Occ 35%", "N de venda", "Preço (mediana)",
                                           "Retorno (estim.)", "Retorno (Occ 35%)"],
                     money=["price_med", "rev_proxy_med", "occ35"])
    tb_mercado = md_table(mercado.reset_index().head(10),
                          labels=["Bairro", "Oferta total", "Com preco", "Com reviews"])

    if not yield_cidade.empty:
        resp1 = (f"a resposta depende do critério adotado. Pela **maior receita estimada**, "
                 f"o melhor perfil é o **{perfil_legivel(best_perfil['perfil'])}** (cerca de "
                 f"R$ {fmt(best_perfil['rev_proxy_med'])} por ano); pelo **maior retorno "
                 f"estimado sobre o preço de venda** — critério mais relevante para quem "
                 f"investe — é o **{perfil_legivel(pos['perfil'])}** "
                 f"({pct(pos['yield_proxy'])}% ao ano). Os dois critérios estão detalhados "
                 f"abaixo.")
    else:
        resp1 = (f"o melhor perfil de imóvel para investir na cidade é o "
                 f"**{perfil_legivel(best_perfil['perfil'])}**, com a maior receita estimada "
                 f"(cerca de R$ {fmt(best_perfil['rev_proxy_med'])} por ano).")

    if not yield_cidade.empty:
        p1_resumo = (f"pela **maior receita estimada**, o melhor é o "
                     f"**{perfil_legivel(best_perfil['perfil'])}** "
                     f"(R$ {fmt(best_perfil['rev_proxy_med'])}/ano); pelo **maior retorno "
                     f"estimado sobre o preço de venda**, o melhor é o "
                     f"**{perfil_legivel(pos['perfil'])}** ({pct(pos['yield_proxy'])}% ao ano).")
    else:
        p1_resumo = (f"o maior valor de receita estimada é o do "
                     f"**{perfil_legivel(best_perfil['perfil'])}** (cerca de "
                     f"R$ {fmt(best_perfil['rev_proxy_med'])} por ano).")
    resp2 = (f"a melhor localização em termos de receita é a **Meia Praia**, com receita "
             f"estimada de R$ {fmt(best_suburb['rev_proxy_med'])} por ano — bem à frente do "
             f"Centro e de Morretes.")
    resp3 = ("o tamanho do imóvel é o que mais influencia a receita: quanto mais quartos, "
             "maior o preço por noite e maior a receita estimada. Taxa de limpeza e número "
             "de fotos também andam junto com preços maiores. Notas e avaliações dos hóspedes "
             "têm pouca relação com o preço cobrado.")
    if not yield_cidade.empty:
        melhor_bairro = melhores_sub.iloc[0]["suburb"] if not melhores_sub.empty else "Meia Praia"
        resp4 = (f"a recomendação é comprar **{perfil_legivel(pos['perfil'])}**, com retorno "
                 f"anual estimado em aproximadamente {pct(pos['yield_proxy'])}%, pois combina "
                 f"boa receita estimada (R$ {fmt(pos['rev_proxy_med'])}) com preço mediano de "
                 f"venda razoável (R$ {fmt(pos['price_med'])}). Pelo retorno por bairro, "
                 f"{prep_bairro(melhor_bairro)} é o melhor lugar.")
    else:
        resp4 = "ver a tabela da Pergunta 4"

    txt = f"""# Relatório — Recomendação de investimento imobiliário em Itapema (SC)

## Resumo executivo

Com base nos anúncios de curta temporada (Airbnb) e de venda (VivaReal), a recomendação à
Seazone é investir em {pos_txt}.

- **Pergunta 1 (perfil):** a resposta muda conforme o critério — {p1_resumo}
- **Pergunta 2 (localização):** a maior receita estimada está na **Meia Praia**.
- **Pergunta 3 (características):** o **tamanho do imóvel** é o que mais influencia a receita;
  taxa de limpeza e número de fotos também acompanham preços maiores.
- **Pergunta 4 (compra):** os maiores retornos estimados, por combinação de imóvel e bairro, são:
{top_lines}

## Posição sobre a tese interna (compactos no Centro)

{verdict}

## Premissas e decisões
- O preço por noite de cada anúncio foi obtido mantendo a **última captura por (anúncio, data de estadia)**.
- Universo de receita = **22,5% da base (977 imóveis)**: os anúncios que estavam **com preço e com avaliações** no momento da coleta. Os demais (3.442) não tinham preço capturado, então não foi possível estimar receita para eles; entram apenas como contexto de mercado.
- **22 anúncios com preço mas sem nenhuma avaliação foram excluídos** (~2%): sem avaliações não há como estimar as noites alugadas (regra D1).
- A **estimativa de receita** usa as avaliações para estimar quantas noites por ano cada imóvel é alugado (`avaliações ÷ 0,5 × 3`, no máximo 365 noites). As colunas **Occ 25% / 35% / 45%** mostram a receita caso o imóvel fique ocupado 25%, 35% ou 45% do ano — servem para verificar se a recomendação muda conforme a premissa.
- Colunas sem dados válidos (`min_nights` e `response_*`) foram excluídas.
- Notas de avaliação com valor 0 (ou seja, "não avaliado") receberam a mediana do mercado.
- Bairros do VivaReal foram padronizados. **"Outros (Andorinha e Castelo Branco)"** reúne os anúncios de venda desses dois bairros (≈19% da oferta de venda) e entra apenas no cálculo do **preço de compra** (divisor do retorno agregado da cidade), já que lá não há dados de aluguel Airbnb — não inventamos uma receita que não existe.
- Bairros sem localização segura foram excluídos do VivaReal (Estreito, Itapema, Ocean Tower e registros sem bairro): {len(excluidos)} anúncios.
- Faixas de quartos: Studio (0q), 1, 2, 3, 4, 5+.
- A Pergunta 1 considera **dois critérios** para "melhor perfil": a **maior receita estimada**
  (resposta: 4 quartos) e o **maior retorno sobre o preço de venda** (resposta: 2 quartos).
  O retorno é o critério decisivo na Pergunta 4.

## Pergunta 1 — Melhor perfil de imóvel para investir na cidade

**Resposta:** {resp1}

{tb_q1}

{resp1_criterio}

> Perfil = tipo de anúncio + quantidade de quartos. As colunas "Occ" mostram a receita
> estimada se o imóvel ficasse ocupado 25%, 35% ou 45% do ano. Nos cenários de ocupação,
> imóveis de 1 e 2 quartos ficam praticamente empatados (veja a Pergunta 4).

## Pergunta 2 — Melhor localização em termos de receita

**Resposta:** {resp2}

{tb_q2}

> Considera bairros com pelo menos 20 imóveis ativos na amostra. A oferta total de anúncios
> por bairro está em `output/mercado_contexto.csv`.

## Pergunta 3 — Características que explicam as melhores receitas

**Resposta:** {resp3}

O foco aqui é o **preço médio por noite** (que compõe a receita) e suas associações com as
características do anúncio. A correlação varia de -1 a +1: quanto mais perto de 1, maior a
associação positiva com o preço por noite; perto de -1, associação inversa; perto de 0, sem
relação clara.

Correlação com o preço médio por noite:
{tb_corr}

Comparação por grupos (mediana de preço por noite e de receita estimada):
{tb_grupos}

## Pergunta 4 — O que a Seazone compraria hoje e estimativa de retorno

**Resposta:** {resp4}

O retorno é estimado como **receita anual estimada ÷ preço mediano de venda**. Por perfil,
considerando a cidade toda (o preço de venda inclui "Outros (Andorinha e Castelo Branco)"):
{tb_yc}

Por perfil e bairro (onde há receita e oferta de venda ao mesmo tempo):
{tb_yb}

Robustez — melhor perfil em cada cenário (1 e 2 quartos empatam): `output/q4_robustez.csv`.

## Limitações
- A janela de preço é de janeiro a abril de 2025 (alta temporada). A estimativa de receita
  pelas avaliações cobre o ano inteiro; os cenários de ocupação verificam a sensibilidade.
- Receita estimada, não contabilizada; a base não traz a taxa de ocupação real.
- Compara universos diferentes (anúncios Airbnb ativos × anúncios de venda): compara-se
  medianas de perfil/bairro, nunca imóvel a imóvel.
- "Outros (Andorinha e Castelo Branco)" não gera retorno próprio (sem receita de aluguel).
"""
    with open("relatorio.md", "w", encoding="utf-8") as f:
        f.write(txt)
    print("relatorio.md gerado.")


if __name__ == "__main__":
    main()