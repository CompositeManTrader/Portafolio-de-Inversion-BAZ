"""
Capa de graficos: plantilla Plotly y constructores de figuras.

Reglas de construccion aplicadas de forma consistente:
  - Paleta categorica de orden fijo, nunca ciclada ni generada.
  - Un solo eje de valor por figura; dos magnitudes distintas se indizan
    a una base comun o se separan en dos graficos.
  - Marcas delgadas, extremos redondeados de 4 px, separacion de 2 px
    entre rellenos contiguos.
  - Rejilla y ejes recesivos; etiquetas directas cuando hay 4 series o menos.
  - Capa de hover siempre presente.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# --- Superficies y tintas (verificadas por contraste) ---------------------
PLANO = "#0a0a0f"
SUPERFICIE = "#14141b"
BORDE = "#2a2a38"
TINTA = "#f4f3f7"
TINTA_2 = "#a8a5b8"
TINTA_3 = "#7d7a90"

MARCA = "#522D6D"
MARCA_CLARA = "#9085e9"

POSITIVO = "#0ca30c"
NEGATIVO = "#d03b3b"
POSITIVO_TXT = "#22c55e"
NEGATIVO_TXT = "#ef4444"
NEUTRO = "#4a4a5c"

# Paleta categorica de orden fijo. Validada sobre la superficie #14141b:
# banda de luminosidad, piso de croma, separacion CVD adyacente 8.4,
# piso de vision normal 19.3 y contraste >= 3:1 en las ocho ranuras.
CATEGORICA = [
    "#3987e5",  # 1 azul
    "#008300",  # 2 verde
    "#d55181",  # 3 magenta
    "#c98500",  # 4 amarillo
    "#199e70",  # 5 aqua
    "#d95926",  # 6 naranja
    "#9085e9",  # 7 violeta
    "#e66767",  # 8 rojo
]

MONO = "JetBrains Mono, IBM Plex Mono, SF Mono, Consolas, monospace"
SANS = "Inter, -apple-system, Segoe UI, Roboto, sans-serif"


def registrar_plantilla() -> None:
    """Registra y activa la plantilla 'punto' en Plotly."""
    pio.templates["punto"] = go.layout.Template(
        layout=dict(
            paper_bgcolor=SUPERFICIE,
            plot_bgcolor=SUPERFICIE,
            font=dict(family=SANS, size=11.5, color=TINTA_2),
            title=dict(font=dict(family=SANS, size=13, color=TINTA), x=0, xanchor="left"),
            colorway=CATEGORICA,
            xaxis=dict(gridcolor=BORDE, zerolinecolor=BORDE, linecolor=BORDE,
                       tickfont=dict(family=MONO, size=10, color=TINTA_3),
                       showgrid=False, automargin=True),
            yaxis=dict(gridcolor=BORDE, zerolinecolor=BORDE, linecolor=BORDE,
                       tickfont=dict(family=MONO, size=10, color=TINTA_3),
                       gridwidth=1, automargin=True),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10.5, color=TINTA_2),
                        orientation="h", yanchor="bottom", y=1.02,
                        xanchor="left", x=0),
            hoverlabel=dict(bgcolor="#1c1c26", bordercolor=BORDE,
                            font=dict(family=MONO, size=11, color=TINTA)),
            margin=dict(l=10, r=14, t=34, b=10),
            separators=".,",
        )
    )
    pio.templates.default = "punto"


def _color_direccional(valores) -> list[str]:
    """Verde/rojo segun signo. Se acompana siempre de etiqueta o eje con signo."""
    return [POSITIVO if v >= 0 else NEGATIVO for v in valores]


def _vacio(mensaje: str = "Sin datos suficientes") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=mensaje, showarrow=False,
                       font=dict(family=SANS, size=12, color=TINTA_3))
    fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False),
                      height=240)
    return fig


# --------------------------------------------------------------------------
# Composicion
# --------------------------------------------------------------------------

def treemap_composicion(valuada: pd.DataFrame, dimension: str = "sector",
                        altura: int = 430) -> go.Figure:
    """
    Mapa de arbol: tamano = valor de mercado, color = dimension (identidad).
    Las etiquetas directas son el codificado secundario que exige la
    validacion de la paleta en formas de todos-contra-todos.
    """
    if not len(valuada):
        return _vacio()

    df = valuada.copy()
    niveles = df[dimension].astype(str)
    orden = list(dict.fromkeys(niveles))
    mapa = {n: CATEGORICA[i % len(CATEGORICA)] for i, n in enumerate(orden)}

    # Plotly exige que cada valor de `parents` exista tambien como `labels`.
    # Sin los nodos padre explicitos el arbol queda huerfano y no dibuja nada.
    etiquetas = orden + df["emisora"].astype(str).tolist()
    padres = [""] * len(orden) + niveles.tolist()
    valores = [0.0] * len(orden) + df["valor_mercado"].tolist()
    pesos = [df.loc[niveles == n, "peso_pct"].sum() for n in orden] + \
            df["peso_pct"].tolist()
    colores = [mapa[n] for n in orden] + [mapa[n] for n in niveles]

    fig = go.Figure(go.Treemap(
        labels=etiquetas, parents=padres, values=valores,
        branchvalues="remainder",   # el padre suma lo de sus hijos
        marker=dict(colors=colores,
                    line=dict(color=SUPERFICIE, width=2)),  # separacion de 2 px
        customdata=[f"{p:.1f} %" for p in pesos],
        texttemplate="<b>%{label}</b><br>%{customdata}",
        textfont=dict(family=MONO, size=10.5, color="#ffffff"),
        hovertemplate=("<b>%{label}</b><br>Valor  %{value:,.0f} MXN"
                       "<br>Peso   %{customdata}<extra></extra>"),
        tiling=dict(pad=2),
        pathbar=dict(visible=False),
    ))
    fig.update_layout(height=altura, margin=dict(l=0, r=0, t=8, b=0))
    return fig


def barras_dimension(agrupado: pd.DataFrame, dimension: str,
                     altura: int = 340) -> go.Figure:
    """
    Peso por dimension. Categoria nominal sin orden intrinseco: una sola
    serie, por lo tanto un solo tono y sin caja de leyenda.
    """
    if not len(agrupado):
        return _vacio()

    df = agrupado.sort_values("valor_mercado")
    fig = go.Figure(go.Bar(
        x=df["peso_pct"], y=df[dimension].astype(str), orientation="h",
        marker=dict(color=CATEGORICA[0],
                    line=dict(color=SUPERFICIE, width=2)),
        text=[f"{p:.1f}%" for p in df["peso_pct"]],
        textposition="outside",
        textfont=dict(family=MONO, size=10, color=TINTA_2),
        customdata=np.stack([df["valor_mercado"], df["no_realizado"],
                             df["rend_pct"]], axis=-1),
        hovertemplate=("<b>%{y}</b><br>Peso    %{x:.2f} %"
                       "<br>Valor   %{customdata[0]:,.0f} MXN"
                       "<br>P&L     %{customdata[1]:,.0f} MXN"
                       "<br>Rend.   %{customdata[2]:+.2f} %<extra></extra>"),
        cliponaxis=False,
    ))
    fig.update_layout(
        height=altura, bargap=0.34,
        xaxis=dict(title="Peso del portafolio (%)", showgrid=True, ticksuffix=" %"),
        yaxis=dict(title=None),
        margin=dict(l=6, r=54, t=12, b=8),
    )
    return fig


# --------------------------------------------------------------------------
# Resultado y atribucion
# --------------------------------------------------------------------------

def barras_contribucion(df: pd.DataFrame, etiqueta: str, valor: str,
                        titulo_eje: str = "P&L no realizado (MXN)",
                        altura: int = 430, n: int = 18) -> go.Figure:
    """
    Aporte al resultado, ordenado. Polaridad -> escala divergente con
    gris neutro implicito en el cero; el eje con signo es el codificado
    secundario que evita depender solo del color.
    """
    if not len(df):
        return _vacio()

    d = df.reindex(df[valor].abs().sort_values(ascending=False).index).head(n)
    d = d.sort_values(valor)

    fig = go.Figure(go.Bar(
        x=d[valor], y=d[etiqueta].astype(str), orientation="h",
        marker=dict(color=_color_direccional(d[valor]),
                    line=dict(color=SUPERFICIE, width=2)),
        text=[f"{v/1e6:+,.2f} M" for v in d[valor]],
        textposition="outside",
        textfont=dict(family=MONO, size=10, color=TINTA_2),
        hovertemplate="<b>%{y}</b><br>" + titulo_eje + "  %{x:,.0f}<extra></extra>",
        cliponaxis=False,
    ))
    fig.add_vline(x=0, line=dict(color=TINTA_3, width=1))
    fig.update_layout(
        height=altura, bargap=0.32,
        xaxis=dict(title=titulo_eje, showgrid=True),
        yaxis=dict(title=None),
        margin=dict(l=6, r=76, t=12, b=8),
    )
    return fig


def linea_desempeno(serie_port: pd.Series, serie_bench: pd.Series | None = None,
                    nombre_bench: str = "IPC", altura: int = 380) -> go.Figure:
    """
    Portafolio contra referencia, ambos indizados a 100 en el origen.
    La indizacion es lo que permite una sola escala: nunca dos ejes.
    Dos series -> leyenda presente y ademas etiqueta directa al final.
    """
    if serie_port is None or len(serie_port) < 2:
        return _vacio("Sin historico suficiente")

    base_p = serie_port.iloc[0]
    idx_p = serie_port / base_p * 100.0

    fig = go.Figure()
    # Sin relleno al eje: un indice no es una magnitud medida desde cero, y
    # anclar el area en cero obligaria al eje a abarcar 0-120, aplastando la
    # variacion real contra el borde superior.
    fig.add_trace(go.Scatter(
        x=idx_p.index, y=idx_p.values, name="Portafolio",
        mode="lines", line=dict(color=MARCA_CLARA, width=2),
        hovertemplate="<b>Portafolio</b><br>%{x|%d %b %Y}<br>Base 100  %{y:.2f}<extra></extra>",
    ))
    fig.add_annotation(x=idx_p.index[-1], y=idx_p.iloc[-1], text="Portafolio",
                       showarrow=False, xanchor="left", xshift=7,
                       font=dict(family=SANS, size=10.5, color=MARCA_CLARA))

    if serie_bench is not None and len(serie_bench) >= 2:
        b = serie_bench.reindex(serie_port.index).ffill().dropna()
        if len(b) >= 2:
            idx_b = b / b.iloc[0] * 100.0
            fig.add_trace(go.Scatter(
                x=idx_b.index, y=idx_b.values, name=nombre_bench,
                mode="lines", line=dict(color=TINTA_3, width=2, dash="dot"),
                hovertemplate="<b>" + nombre_bench +
                              "</b><br>%{x|%d %b %Y}<br>Base 100  %{y:.2f}<extra></extra>",
            ))
            fig.add_annotation(x=idx_b.index[-1], y=idx_b.iloc[-1], text=nombre_bench,
                               showarrow=False, xanchor="left", xshift=7,
                               font=dict(family=SANS, size=10.5, color=TINTA_3))

    fig.add_hline(y=100, line=dict(color=BORDE, width=1, dash="dash"))
    fig.update_layout(
        height=altura, hovermode="x unified",
        yaxis=dict(title="Indice (base 100)", showgrid=True, autorange=True,
                   rangemode="normal"),
        xaxis=dict(showgrid=False),
        margin=dict(l=6, r=76, t=30, b=8),
    )
    return fig


def area_drawdown(serie_port: pd.Series, altura: int = 250) -> go.Figure:
    """Caida acumulada desde el maximo previo."""
    if serie_port is None or len(serie_port) < 2:
        return _vacio("Sin historico suficiente")
    dd = (serie_port / serie_port.cummax() - 1.0) * 100.0
    fig = go.Figure(go.Scatter(
        x=dd.index, y=dd.values, mode="lines",
        line=dict(color=NEGATIVO, width=2),
        fill="tozeroy", fillcolor="rgba(208,59,59,0.18)",
        hovertemplate="%{x|%d %b %Y}<br>Caida  %{y:.2f} %<extra></extra>",
    ))
    fig.update_layout(
        height=altura, hovermode="x unified",
        yaxis=dict(title="Caida desde maximo (%)", ticksuffix=" %", showgrid=True),
        xaxis=dict(showgrid=False), margin=dict(l=6, r=14, t=12, b=8),
    )
    return fig


# --------------------------------------------------------------------------
# Efectivo
# --------------------------------------------------------------------------

def escalones_efectivo(serie: pd.DataFrame, altura: int = 300) -> go.Figure:
    """Saldo de efectivo en escalones, con los flujos del dia en el hover."""
    if not len(serie):
        return _vacio("Aun no hay movimientos registrados")

    fig = go.Figure(go.Scatter(
        x=serie["fecha"], y=serie["efectivo"], mode="lines+markers",
        line=dict(color=CATEGORICA[4], width=2, shape="hv"),
        marker=dict(size=8, color=CATEGORICA[4],
                    line=dict(color=SUPERFICIE, width=2)),  # anillo de 2 px
        customdata=serie["flujo"],
        hovertemplate=("%{x|%d %b %Y}<br>Saldo   %{y:,.0f} MXN"
                       "<br>Flujo   %{customdata:+,.0f} MXN<extra></extra>"),
    ))
    fig.add_hline(y=0, line=dict(color=TINTA_3, width=1, dash="dash"))
    fig.update_layout(
        height=altura, hovermode="x unified",
        yaxis=dict(title="Saldo de efectivo (MXN)", showgrid=True),
        xaxis=dict(showgrid=False), margin=dict(l=6, r=14, t=12, b=8),
    )
    return fig


def barras_flujo(bitacora: pd.DataFrame, altura: int = 280) -> go.Figure:
    """Entradas y salidas de efectivo por dia."""
    if not len(bitacora) or bitacora["fecha"].isna().all():
        return _vacio("Aun no hay movimientos registrados")

    b = bitacora.dropna(subset=["fecha"])
    g = b.groupby("fecha", as_index=False)["efecto_caja"].sum()

    fig = go.Figure(go.Bar(
        x=g["fecha"], y=g["efecto_caja"],
        marker=dict(color=_color_direccional(g["efecto_caja"]),
                    line=dict(color=SUPERFICIE, width=2)),
        hovertemplate="%{x|%d %b %Y}<br>Flujo neto  %{y:,.0f} MXN<extra></extra>",
    ))
    fig.add_hline(y=0, line=dict(color=TINTA_3, width=1))
    fig.update_layout(
        height=altura, bargap=0.5,
        yaxis=dict(title="Flujo neto de efectivo (MXN)", showgrid=True),
        xaxis=dict(showgrid=False), margin=dict(l=6, r=14, t=12, b=8),
    )
    return fig


# --------------------------------------------------------------------------
# Riesgo
# --------------------------------------------------------------------------

def barras_riesgo_vs_peso(riesgo_pos: pd.DataFrame, altura: int = 430,
                          n: int = 15) -> go.Figure:
    """
    Peso contra contribucion al riesgo. Ambas magnitudes son porcentajes
    del total, por lo que comparten escala legitimamente: dos series
    agrupadas, con leyenda.
    """
    if not len(riesgo_pos):
        return _vacio("Se requiere historico de al menos 30 sesiones")

    d = riesgo_pos.head(n).sort_values("contrib_riesgo_pct")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=d["peso_pct"], y=d["emisora"].astype(str), orientation="h",
        name="Peso en cartera", marker=dict(color=NEUTRO,
                                            line=dict(color=SUPERFICIE, width=2)),
        hovertemplate="<b>%{y}</b><br>Peso  %{x:.2f} %<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=d["contrib_riesgo_pct"], y=d["emisora"].astype(str), orientation="h",
        name="Contribucion al riesgo",
        marker=dict(color=CATEGORICA[5], line=dict(color=SUPERFICIE, width=2)),
        hovertemplate="<b>%{y}</b><br>Riesgo  %{x:.2f} %<extra></extra>",
    ))
    fig.update_layout(
        height=altura, barmode="group", bargap=0.28, bargroupgap=0.12,
        xaxis=dict(title="Porcentaje del total (%)", ticksuffix=" %", showgrid=True),
        yaxis=dict(title=None), margin=dict(l=6, r=14, t=30, b=8),
    )
    return fig


def mapa_correlacion(corr: pd.DataFrame, altura: int = 500) -> go.Figure:
    """
    Correlaciones. Polaridad en torno a cero -> escala divergente de dos
    tonos con gris neutro en el punto medio, nunca un arcoiris.
    """
    if not len(corr):
        return _vacio("Se requiere historico de al menos 30 sesiones")

    escala = [
        [0.00, "#1b4f8f"], [0.25, "#3987e5"], [0.47, "#5a5a68"],
        [0.50, "#6b6b78"], [0.53, "#5a5a68"], [0.75, "#d95926"],
        [1.00, "#8f2f10"],
    ]
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.index,
        colorscale=escala, zmid=0, zmin=-1, zmax=1,
        xgap=2, ygap=2,  # separacion de 2 px entre celdas
        colorbar=dict(title=dict(text="Corr.", font=dict(size=10)),
                      tickfont=dict(family=MONO, size=9.5), thickness=11,
                      outlinewidth=0, len=0.85),
        hovertemplate="<b>%{y}</b> vs <b>%{x}</b><br>Correlacion  %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(
        height=altura,
        xaxis=dict(tickangle=-45, tickfont=dict(family=MONO, size=9.5), showgrid=False),
        yaxis=dict(tickfont=dict(family=MONO, size=9.5), showgrid=False,
                   autorange="reversed"),
        margin=dict(l=6, r=6, t=12, b=8),
    )
    return fig


def dispersion_riesgo_rendimiento(valuada: pd.DataFrame, tecnicos: pd.DataFrame,
                                  riesgo_pos: pd.DataFrame,
                                  altura: int = 440) -> go.Figure:
    """
    Volatilidad individual contra rendimiento acumulado; el tamano codifica
    el peso en cartera. Al ser una forma de todos-contra-todos, la identidad
    se resuelve con etiqueta directa y no con color.
    """
    if not len(valuada) or not len(riesgo_pos):
        return _vacio("Se requiere historico de al menos 30 sesiones")

    d = valuada.merge(riesgo_pos[["ticker", "vol_individual_pct"]],
                      on="ticker", how="inner")
    if not len(d):
        return _vacio()

    tam = 9 + (d["peso_pct"] / d["peso_pct"].max()) * 34

    fig = go.Figure(go.Scatter(
        x=d["vol_individual_pct"], y=d["rend_pct"], mode="markers+text",
        text=d["emisora"], textposition="top center",
        textfont=dict(family=MONO, size=8.6, color=TINTA_3),
        marker=dict(size=tam, color=_color_direccional(d["rend_pct"]),
                    opacity=0.82,
                    line=dict(color=SUPERFICIE, width=2)),  # anillo de 2 px
        customdata=np.stack([d["peso_pct"], d["valor_mercado"],
                             d["no_realizado"]], axis=-1),
        hovertemplate=("<b>%{text}</b><br>Volatilidad  %{x:.1f} %"
                       "<br>Rendimiento  %{y:+.1f} %"
                       "<br>Peso         %{customdata[0]:.2f} %"
                       "<br>P&L          %{customdata[2]:,.0f} MXN<extra></extra>"),
    ))
    fig.add_hline(y=0, line=dict(color=TINTA_3, width=1, dash="dash"))
    fig.update_layout(
        height=altura,
        xaxis=dict(title="Volatilidad anualizada (%)", ticksuffix=" %", showgrid=True),
        yaxis=dict(title="Rendimiento acumulado (%)", ticksuffix=" %", showgrid=True),
        margin=dict(l=6, r=14, t=12, b=8),
    )
    return fig
