"""
Taxonomia de instrumentos: mapeo emisora BMV -> ticker Yahoo Finance,
clase de activo, sector GICS-like, industria, region y mercado.

Todos los tickers .MX cotizan en MXN (incluido el SIC), por lo que la
valuacion no requiere conversion FX. La columna `divisa_subyacente`
identifica la exposicion cambiaria economica real de cada posicion.

Los 30 tickers fueron validados contra Yahoo Finance el 2026-07-21.
"""

from __future__ import annotations

import re
import unicodedata

# --------------------------------------------------------------------------
# Normalizacion de nombres de emisora
# --------------------------------------------------------------------------
# Las hojas de posicion traen el prefijo de "tipo valor" de la BMV
# ("1", "1A", "1B", "1I", "41", "CF"), mientras que la hoja de movimientos
# y las boletas del custodio no lo traen. Se normaliza a la forma sin prefijo.

_TIPO_VALOR = re.compile(r"^(?:\d+[A-Z]?|CF)\s+")
_WS = re.compile(r"\s+")


def normalizar_emisora(raw: str) -> str:
    """'1B NAFTRAC ISHRS' -> 'NAFTRAC ISHRS'; 'AC *      ' -> 'AC *'."""
    if raw is None:
        return ""
    s = unicodedata.normalize("NFKC", str(raw)).strip().upper()
    s = _TIPO_VALOR.sub("", s)
    return _WS.sub(" ", s).strip()


def extraer_tipo_valor(raw: str) -> str:
    """Devuelve el prefijo de tipo valor de la BMV, o '' si no lo trae."""
    if raw is None:
        return ""
    s = unicodedata.normalize("NFKC", str(raw)).strip().upper()
    m = _TIPO_VALOR.match(s)
    return m.group(0).strip() if m else ""


# --------------------------------------------------------------------------
# Catalogo maestro
# --------------------------------------------------------------------------
# clase_activo | sector | industria | region | mercado | divisa_subyacente

CATALOGO: dict[str, dict[str, str]] = {
    # ---- ETFs indizados (SIC) -------------------------------------------
    "NAFTRAC ISHRS": dict(ticker="NAFTRACISHRS.MX", clase_activo="ETF",
                          sector="Indice Amplio", industria="Renta Variable Mexico",
                          region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "QQQ *": dict(ticker="QQQ.MX", clase_activo="ETF",
                  sector="Tecnologia", industria="Nasdaq 100",
                  region="EE.UU.", mercado="SIC", divisa_subyacente="USD"),
    "IVV *": dict(ticker="IVV.MX", clase_activo="ETF",
                  sector="Indice Amplio", industria="S&P 500",
                  region="EE.UU.", mercado="SIC", divisa_subyacente="USD"),
    "SHV *": dict(ticker="SHV.MX", clase_activo="Renta Fija",
                  sector="Liquidez", industria="Tesoro EE.UU. 0-1a",
                  region="EE.UU.", mercado="SIC", divisa_subyacente="USD"),
    "EWJ *": dict(ticker="EWJ.MX", clase_activo="ETF",
                  sector="Indice Amplio", industria="Renta Variable Japon",
                  region="Japon", mercado="SIC", divisa_subyacente="USD"),
    "EEM *": dict(ticker="EEM.MX", clase_activo="ETF",
                  sector="Indice Amplio", industria="Mercados Emergentes",
                  region="Emergentes", mercado="SIC", divisa_subyacente="USD"),
    "IEFA *": dict(ticker="IEFA.MX", clase_activo="ETF",
                   sector="Indice Amplio", industria="Desarrollados ex-EE.UU.",
                   region="Desarrollados ex-EE.UU.", mercado="SIC", divisa_subyacente="USD"),
    "ACWI *": dict(ticker="ACWI.MX", clase_activo="ETF",
                   sector="Indice Amplio", industria="Global All-Cap",
                   region="Global", mercado="SIC", divisa_subyacente="USD"),

    # ---- Acciones internacionales (SIC) ---------------------------------
    "MSFT *": dict(ticker="MSFT.MX", clase_activo="Accion",
                   sector="Tecnologia", industria="Software",
                   region="EE.UU.", mercado="SIC", divisa_subyacente="USD"),
    "AAPL *": dict(ticker="AAPL.MX", clase_activo="Accion",
                   sector="Tecnologia", industria="Hardware",
                   region="EE.UU.", mercado="SIC", divisa_subyacente="USD"),
    "MELI N": dict(ticker="MELI.MX", clase_activo="Accion",
                   sector="Consumo Discrecional", industria="E-commerce",
                   region="LatAm", mercado="SIC", divisa_subyacente="USD"),

    # ---- Consumo Basico (BMV) -------------------------------------------
    "WALMEX *": dict(ticker="WALMEX.MX", clase_activo="Accion",
                     sector="Consumo Basico", industria="Autoservicios",
                     region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "LACOMER UBC": dict(ticker="LACOMERUBC.MX", clase_activo="Accion",
                        sector="Consumo Basico", industria="Autoservicios",
                        region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "CHDRAUI B": dict(ticker="CHDRAUIB.MX", clase_activo="Accion",
                      sector="Consumo Basico", industria="Autoservicios",
                      region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "BIMBO A": dict(ticker="BIMBOA.MX", clase_activo="Accion",
                    sector="Consumo Basico", industria="Alimentos",
                    region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "GRUMA B": dict(ticker="GRUMAB.MX", clase_activo="Accion",
                    sector="Consumo Basico", industria="Alimentos",
                    region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "AC *": dict(ticker="AC.MX", clase_activo="Accion",
                 sector="Consumo Basico", industria="Bebidas",
                 region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "FEMSA UBD": dict(ticker="FEMSAUBD.MX", clase_activo="Accion",
                      sector="Consumo Basico", industria="Bebidas",
                      region="Mexico", mercado="BMV", divisa_subyacente="MXN"),

    # ---- Consumo Discrecional (BMV) -------------------------------------
    "ALSEA *": dict(ticker="ALSEA.MX", clase_activo="Accion",
                    sector="Consumo Discrecional", industria="Restaurantes",
                    region="Mexico", mercado="BMV", divisa_subyacente="MXN"),

    # ---- Financiero (BMV) -----------------------------------------------
    "GFNORTE O": dict(ticker="GFNORTEO.MX", clase_activo="Accion",
                      sector="Financiero", industria="Bancos",
                      region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "BBAJIO O": dict(ticker="BBAJIOO.MX", clase_activo="Accion",
                     sector="Financiero", industria="Bancos",
                     region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "GENTERA *": dict(ticker="GENTERA.MX", clase_activo="Accion",
                      sector="Financiero", industria="Microfinanzas",
                      region="Mexico", mercado="BMV", divisa_subyacente="MXN"),

    # ---- Industriales (BMV) ---------------------------------------------
    "ASUR B": dict(ticker="ASURB.MX", clase_activo="Accion",
                   sector="Industriales", industria="Aeropuertos",
                   region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "GAP B": dict(ticker="GAPB.MX", clase_activo="Accion",
                  sector="Industriales", industria="Aeropuertos",
                  region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "OMA B": dict(ticker="OMAB.MX", clase_activo="Accion",
                  sector="Industriales", industria="Aeropuertos",
                  region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "VOLAR A": dict(ticker="VOLARA.MX", clase_activo="Accion",
                    sector="Industriales", industria="Aerolineas",
                    region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "TRAXION A": dict(ticker="TRAXIONA.MX", clase_activo="Accion",
                      sector="Industriales", industria="Logistica y Transporte",
                      region="Mexico", mercado="BMV", divisa_subyacente="MXN"),

    # ---- Materiales / Salud / Inmobiliario (BMV) ------------------------
    "GMEXICO B": dict(ticker="GMEXICOB.MX", clase_activo="Accion",
                      sector="Materiales", industria="Mineria",
                      region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "LAB B": dict(ticker="LABB.MX", clase_activo="Accion",
                  sector="Salud", industria="Farmaceutica",
                  region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
    "FUNO 11": dict(ticker="FUNO11.MX", clase_activo="FIBRA",
                    sector="Inmobiliario", industria="FIBRA Diversificada",
                    region="Mexico", mercado="BMV", divisa_subyacente="MXN"),
}

CAMPOS = ("ticker", "clase_activo", "sector", "industria",
          "region", "mercado", "divisa_subyacente")

DESCONOCIDO = dict(ticker="", clase_activo="Sin clasificar", sector="Sin clasificar",
                   industria="Sin clasificar", region="Sin clasificar",
                   mercado="Sin clasificar", divisa_subyacente="MXN")


def clasificar(emisora: str) -> dict[str, str]:
    """Devuelve la ficha taxonomica de una emisora ya normalizada."""
    return CATALOGO.get(normalizar_emisora(emisora), DESCONOCIDO)


def ticker_de(emisora: str) -> str:
    return clasificar(emisora)["ticker"]


# Indice inverso ticker -> emisora, util al mapear descargas de yfinance.
TICKER_A_EMISORA = {v["ticker"]: k for k, v in CATALOGO.items()}

# Benchmark por defecto: IPC de la BMV.
BENCHMARK_TICKER = "^MXX"
BENCHMARK_NOMBRE = "IPC (S&P/BMV IPC)"
FX_TICKER = "USDMXN=X"
