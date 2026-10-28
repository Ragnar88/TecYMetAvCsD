"""Genera la guía PDF del ARIMA a partir de las salidas guardadas del notebook.

Uso, desde la raíz del repositorio:
    python scripts/build_arima_pdf.py data/eia_precios_crudo_diarios_2024-01_a_2026-10.csv \
        output/pdf/explicacion_modelo_arima_wti_brent.pdf output/pdf/figuras_arima
Requiere además reportlab (pip install reportlab), que no está en requirements.txt.

No reentrena el modelo: los números salen de arima_periodo_2_wti_brent.ipynb
(ejecución del 26/10/2026). El CSV se usa para el historial y para ACF/PACF.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from statsmodels.tsa.stattools import acf, pacf
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

CSV, SALIDA, FIGS = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
FIGS.mkdir(parents=True, exist_ok=True)

# ---------- Paleta y tipografía (misma guía visual que el PDF de Holt) ----------
TEAL = colors.HexColor("#087f8c")
NAVY = colors.HexColor("#15384b")
PANEL = colors.HexColor("#f0f5f8")
STEP = colors.HexColor("#e4ecf1")
MUTED = colors.HexColor("#5b7381")
LINE = colors.HexColor("#d8e2e8")
C_WTI, C_BRENT, C_ARIMA = "#2864A0", "#D08023", "#A32D36"

# Arial en macOS o Windows (regular, negrita).
CANDIDATAS = [(Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
               Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")),
              (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf"))]
REGULAR, NEGRITA = next((r, b) for r, b in CANDIDATAS if r.is_file() and b.is_file())
pdfmetrics.registerFont(TTFont("Sans", str(REGULAR)))
pdfmetrics.registerFont(TTFont("Sans-Bold", str(NEGRITA)))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-Bold")

S = {
    "kicker": ParagraphStyle("kicker", fontName="Sans-Bold", fontSize=8.5, textColor=TEAL, spaceAfter=6),
    "h1": ParagraphStyle("h1", fontName="Sans-Bold", fontSize=23, leading=28, textColor=NAVY, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="Sans-Bold", fontSize=12.5, leading=16, textColor=TEAL,
                         spaceBefore=10, spaceAfter=4),
    "body": ParagraphStyle("body", fontName="Sans", fontSize=9.6, leading=14, textColor=NAVY,
                           spaceAfter=6, alignment=TA_LEFT),
    "note": ParagraphStyle("note", fontName="Sans", fontSize=7.6, leading=10.4, textColor=MUTED,
                           spaceBefore=2, spaceAfter=6),
    "cell": ParagraphStyle("cell", fontName="Sans", fontSize=8.4, leading=11, textColor=NAVY),
    "cellh": ParagraphStyle("cellh", fontName="Sans-Bold", fontSize=8.2, leading=10.5, textColor=colors.white),
    "big": ParagraphStyle("big", fontName="Sans-Bold", fontSize=22, leading=25, textColor=TEAL),
    "stat": ParagraphStyle("stat", fontName="Sans", fontSize=8.2, leading=11, textColor=MUTED),
    "callh": ParagraphStyle("callh", fontName="Sans-Bold", fontSize=11.5, leading=15, textColor=TEAL,
                            spaceAfter=3),
}
ANCHO = A4[0] - 2 * 18 * mm


def n(x, dec=2):
    """Formato con coma decimal y punto de miles."""
    return f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def P(texto, estilo="body"):
    return Paragraph(texto, S[estilo])


def tabla(filas, anchos, zebra=True, alinear_derecha=()):
    datos = [[P(c, "cellh") for c in filas[0]]] + [[P(str(c), "cell") for c in f] for f in filas[1:]]
    t = Table(datos, colWidths=[ANCHO * a for a in anchos], repeatRows=1)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE),
    ]
    if zebra:
        estilo += [("BACKGROUND", (0, i), (-1, i), PANEL) for i in range(2, len(datos), 2)]
    t.setStyle(TableStyle(estilo))
    return t


def recuadro(titulo, texto):
    cuerpo = [P(titulo, "callh"), P(texto)]
    t = Table([[cuerpo]], colWidths=[ANCHO])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("LINEBEFORE", (0, 0), (0, -1), 2.6, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return KeepTogether([Spacer(1, 4), t, Spacer(1, 8)])


def tarjetas(items):
    celdas = [[P(num, "big"), P(txt, "stat")] for num, txt in items]
    t = Table([celdas], colWidths=[ANCHO / len(items)] * len(items))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("LINEAFTER", (0, 0), (-2, -1), 3, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t


def pasos(total, evaluados):
    estilo_n = ParagraphStyle("paso", fontName="Sans-Bold", fontSize=8.5, alignment=1, textColor=NAVY)
    estilo_b = ParagraphStyle("pasob", parent=estilo_n, textColor=colors.white)
    celdas = [P(str(i), "cell") for i in range(1, total + 1)]
    celdas = [Paragraph(str(i), estilo_b if i > total - evaluados else estilo_n) for i in range(1, total + 1)]
    ancho = ANCHO / total
    t = Table([celdas], colWidths=[ancho] * total, rowHeights=[22])
    estilo = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("LINEAFTER", (0, 0), (-2, -1), 3, colors.white)]
    for i in range(total):
        estilo.append(("BACKGROUND", (i, 0), (i, 0), TEAL if i >= total - evaluados else STEP))
    t.setStyle(TableStyle(estilo))
    leyenda = Table([[P(f"Pasos 1 a {total - evaluados}: recorrido intermedio", "note"),
                      Paragraph(f"Pasos {total - evaluados + 1} a {total}: semana objetivo",
                                ParagraphStyle("r", parent=S["note"], alignment=2, textColor=TEAL))]],
                    colWidths=[ANCHO / 2] * 2)
    leyenda.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    return [t, leyenda]


def imagen(ruta, ancho_rel=1.0):
    from reportlab.lib.utils import ImageReader
    w, h = ImageReader(str(ruta)).getSize()
    ancho = ANCHO * ancho_rel
    return Image(str(ruta), width=ancho, height=ancho * h / w)


# ---------- Datos: historial del CSV y salidas guardadas del notebook ----------
crudo_csv = pd.read_csv(CSV, keep_default_na=False)
crudo_csv["period"] = pd.to_datetime(crudo_csv["period"])
crudo_csv["value"] = pd.to_numeric(crudo_csv["value"])
p2 = crudo_csv[crudo_csv["period"].between("2026-04-01", "2026-10-26")]
series = {c: p2[p2["series"] == s].set_index("period")["value"].sort_index()
          for c, s in {"WTI": "RWTC", "Brent": "RBRTE"}.items()}
# Control contra las salidas guardadas: cantidades y último precio.
assert len(series["WTI"]) == 138 and len(series["Brent"]) == 136
assert series["WTI"].index[-1] == series["Brent"].index[-1] == pd.Timestamp("2026-10-14")
assert np.isclose(series["WTI"].iloc[-1], 101.91) and np.isclose(series["Brent"].iloc[-1], 126.55)

# Parámetros finales guardados (punto 7 del notebook).
WTI_C, WTI_PHI, WTI_S2 = 93.46755, 0.93601, 14.53399
BRENT_S2 = 23.67989
Z = 1.959964
H = np.arange(1, 18)
fechas_fut = pd.bdate_range("2026-10-15", "2026-11-06")
assert len(fechas_fut) == 17
y_wti, y_brent = series["WTI"].iloc[-1], series["Brent"].iloc[-1]
wti_media = WTI_C + WTI_PHI ** H * (y_wti - WTI_C)
wti_sd = np.sqrt(WTI_S2 * (1 - WTI_PHI ** (2 * H)) / (1 - WTI_PHI ** 2))
brent_media = np.full(17, y_brent)
brent_sd = np.sqrt(BRENT_S2 * H)
trayectorias = {
    "WTI": pd.DataFrame({"m": wti_media, "lo": wti_media - Z * wti_sd, "hi": wti_media + Z * wti_sd}, index=fechas_fut),
    "Brent": pd.DataFrame({"m": brent_media, "lo": brent_media - Z * brent_sd, "hi": brent_media + Z * brent_sd},
                          index=fechas_fut),
}
SEMANA = {  # Tabla guardada: pronóstico de la semana objetivo.
    "WTI": [(97.04, 77.81, 116.27), (96.81, 77.32, 116.30), (96.60, 76.88, 116.31), (96.40, 76.49, 116.31),
            (96.21, 76.13, 116.29)],
    "Brent": [(126.55, 92.16, 160.94), (126.55, 90.86, 162.24), (126.55, 89.61, 163.49), (126.55, 88.40, 164.70),
              (126.55, 87.23, 165.87)],
}
# La trayectoria recalculada con los parámetros guardados debe coincidir con la tabla guardada.
for crudo, filas in SEMANA.items():
    recalculado = trayectorias[crudo].iloc[-5:].round(2).to_numpy()
    assert np.allclose(recalculado, np.array(filas), atol=0.011), (crudo, recalculado)

PRUEBA = {  # Punto 10: semana 05/10 al 09/10, corte 02/10.
    "WTI": {"real": [96.13, 96.24, 95.02, 98.26, 98.73], "arima": [97.89] * 5, "ultimo": 97.89,
            "lo": [90.10, 86.87, 84.39, 82.31, 80.47], "hi": [105.68, 108.91, 111.39, 113.47, 115.31]},
    "Brent": {"real": [125.51, 125.44, 126.00, 130.18, 130.03], "arima": [134.61, 133.73, 132.89, 132.07, 131.28],
              "ultimo": 135.51, "lo": [125.06, 120.46, 116.89, 113.90, 111.29],
              "hi": [144.15, 147.01, 148.88, 150.24, 151.27]},
}
fechas_prueba = pd.bdate_range("2026-10-05", "2026-10-09")

# ---------- Figuras ----------
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.edgecolor": "#33475b",
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e3e9ee", "grid.linewidth": 0.7, "axes.titleweight": "bold",
                     "axes.titlecolor": "#15384b", "axes.labelcolor": "#15384b"})
fmt = mdates.DateFormatter("%d/%m")

fig, ax = plt.subplots(figsize=(8, 3.3))
for crudo, color in [("WTI", C_WTI), ("Brent", C_BRENT)]:
    ax.plot(series[crudo].index, series[crudo], color=color, lw=1.5, label=crudo)
ax.set_ylabel("USD por barril")
ax.xaxis.set_major_formatter(fmt)
ax.legend(frameon=False, loc="upper right")
ax.set_title("Período 2: cotizaciones usadas por el ARIMA", loc="left", fontsize=10)
fig.tight_layout()
fig.savefig(FIGS / "series.png", dpi=200)
plt.close(fig)

# Valores p de KPSS en nivel (d = 0) frente al umbral de 0,05.
fig, ax = plt.subplots(figsize=(8, 1.9))
ax.axvline(0.05, color="#15384b", lw=1.2, ls="--")
ax.text(0.0503, 1.55, "umbral 0,05", ha="left", fontsize=8, color="#15384b")
ax.axvspan(0.040, 0.05, color="#f3dede", alpha=0.7)
ax.axvspan(0.05, 0.060, color="#e0eef0", alpha=0.7)
ax.text(0.0415, 0.15, "KPSS rechaza → d = 1", fontsize=7.5, color="#7a3b3b")
ax.text(0.0585, 0.15, "KPSS no rechaza → d = 0", fontsize=7.5, color="#0b5e66", ha="right")
for y, crudo, p, color in [(1.0, "WTI", 0.051228, C_WTI), (0.55, "Brent", 0.049994, C_BRENT)]:
    ax.plot(p, y, "o", color=color, ms=8)
    ax.text(p + (0.0006 if crudo == "WTI" else -0.0006), y, f"{crudo}: {n(p, 6)}", va="center",
            ha="left" if crudo == "WTI" else "right", fontsize=8.5, color=color, fontweight="bold")
ax.set(xlim=(0.040, 0.060), ylim=(0, 1.8), yticks=[])
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: n(v, 3)))
ax.grid(False)
ax.spines["left"].set_visible(False)
ax.set_title("Valor p de KPSS sobre el precio sin diferenciar, ajuste final", loc="left", fontsize=9.5)
fig.tight_layout()
fig.savefig(FIGS / "kpss.png", dpi=200)
plt.close(fig)

# ACF y PACF del precio (período 2 completo hasta el 14/10, la misma muestra del ajuste final).
REZAGOS = 20
autocorr = {}
for crudo, serie in series.items():
    for nombre, z in [("nivel", serie.to_numpy()), ("diferencia", np.diff(serie.to_numpy()))]:
        valores_acf, ic_acf = acf(z, nlags=REZAGOS, alpha=0.05)
        valores_pacf, ic_pacf = pacf(z, nlags=REZAGOS, method="ywm", alpha=0.05)
        autocorr[crudo, nombre] = {
            "acf": valores_acf[1:], "banda_acf": (ic_acf[1:, 1] - valores_acf[1:]),
            "pacf": valores_pacf[1:], "banda_pacf": (ic_pacf[1:, 1] - valores_pacf[1:]),
        }


def fuera_de_banda(crudo, nombre, tipo):
    r = autocorr[crudo, nombre]
    return [k + 1 for k in range(REZAGOS) if abs(r[tipo][k]) > r[f"banda_{tipo}"][k]]


fig, axes = plt.subplots(2, 2, figsize=(8, 5.0), sharey=True)
rezagos = np.arange(1, REZAGOS + 1)
for col, (crudo, color) in enumerate([("WTI", C_WTI), ("Brent", C_BRENT)]):
    r = autocorr[crudo, "nivel"]
    for fila, (tipo, titulo) in enumerate([("acf", "ACF · autocorrelación"),
                                           ("pacf", "PACF · autocorrelación parcial")]):
        ax = axes[fila, col]
        ax.fill_between(rezagos, -r[f"banda_{tipo}"], r[f"banda_{tipo}"], color="#b9c9d4", alpha=0.45,
                        lw=0, label="Banda aproximada del 95 %")
        ax.vlines(rezagos, 0, r[tipo], color=color, lw=1.6)
        ax.plot(rezagos, r[tipo], "o", color=color, ms=3.5)
        ax.axhline(0, color="#33475b", lw=0.8)
        ax.set_title(f"{crudo} · {titulo}", fontsize=9.5)
        ax.set(ylim=(-0.4, 1.05), xlim=(0.3, REZAGOS + 0.7), xticks=[1, 5, 10, 15, 20])
        if fila == 1:
            ax.set_xlabel("Rezago (cotizaciones hacia atrás)")
axes[0, 0].set_ylabel("Correlación")
axes[1, 0].set_ylabel("Correlación parcial")
axes[0, 1].legend(frameon=False, fontsize=7.5, loc="upper right")
fig.tight_layout()
fig.savefig(FIGS / "acf_pacf.png", dpi=200)
plt.close(fig)

fig, axes = plt.subplots(2, 1, figsize=(8, 6.2))
for ax, (crudo, color) in zip(axes, [("WTI", C_WTI), ("Brent", C_BRENT)]):
    hist = series[crudo].iloc[-40:]
    tr = trayectorias[crudo]
    ax.plot(hist.index, hist, color=color, lw=1.5, label="Precios observados")
    ax.fill_between(tr.index, tr["lo"], tr["hi"], color=C_ARIMA, alpha=0.13, lw=0,
                    label="Intervalo de predicción 95 %")
    ax.plot(tr.index, tr["m"], color=C_ARIMA, ls=":", lw=1.3, label="Recorrido hasta la semana objetivo")
    sem = tr.iloc[-5:]
    ax.plot(sem.index, sem["m"], color=C_ARIMA, marker="o", ms=4, lw=1.5, label="Pronóstico ARIMA, 02 al 06/11")
    ax.axhline(hist.iloc[-1], color="#555555", ls="--", lw=0.9, label="Último precio")
    ax.axvline(hist.index[-1], color="#777777", ls=":", lw=1)
    orden = "ARIMA(1,0,0) con constante" if crudo == "WTI" else "ARIMA(0,1,0) sin deriva"
    ax.set_title(f"{crudo} · {orden}", fontsize=10)
    ax.set_ylabel("USD/barril")
    ax.xaxis.set_major_formatter(fmt)
    if crudo == "WTI":
        ax.legend(frameon=False, fontsize=7.5, loc="lower left", ncol=2)
fig.tight_layout()
fig.savefig(FIGS / "pronostico.png", dpi=200)
plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(8, 2.9))
for ax, (crudo, color) in zip(axes, [("WTI", C_WTI), ("Brent", C_BRENT)]):
    d = PRUEBA[crudo]
    ax.fill_between(fechas_prueba, d["lo"], d["hi"], color=C_ARIMA, alpha=0.12, lw=0, label="Intervalo 95 %")
    ax.plot(fechas_prueba, d["arima"], color=C_ARIMA, marker="o", ms=3.5, label="ARIMA")
    ax.axhline(d["ultimo"], color="#555555", ls="--", lw=0.9, label="Último precio")
    ax.plot(fechas_prueba, d["real"], "o", color="#222222", ms=5, label="Precio real")
    orden = "(0,1,0)" if crudo == "WTI" else "(1,0,0)"
    ax.set_title(f"{crudo} · ARIMA{orden}", fontsize=9.5)
    ax.xaxis.set_major_formatter(fmt)
    ax.set_xticks(fechas_prueba)
axes[0].set_ylabel("USD/barril")
axes[1].legend(frameon=False, fontsize=7, loc="upper right")
fig.tight_layout()
fig.savefig(FIGS / "prueba.png", dpi=200)
plt.close(fig)


# ---------- Documento ----------
ELABORADO = "28/10/2026"


def decorar(canvas, doc):
    canvas.saveState()
    ancho, alto = A4
    canvas.setFillColor(TEAL)
    canvas.rect(0, alto - 4, ancho, 4, fill=1, stroke=0)
    canvas.setFont("Sans-Bold", 7.6)
    canvas.setFillColor(NAVY)
    canvas.drawString(18 * mm, alto - 13 * mm, "PETRÓLEO | MODELO ARIMA")
    canvas.setFont("Sans", 7.6)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(ancho - 18 * mm, alto - 13 * mm, f"Guía elaborada el {ELABORADO}")
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 15 * mm, ancho - 18 * mm, 15 * mm)
    canvas.drawString(18 * mm, 10.5 * mm, "Resultados guardados: 26/10/2026 | Precios y errores en USD por barril")
    canvas.drawRightString(ancho - 18 * mm, 10.5 * mm, str(doc.page))
    canvas.restoreState()


doc = BaseDocTemplate(
    str(SALIDA), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=20 * mm, bottomMargin=20 * mm,
    title="Cómo pronosticamos el precio del petróleo con ARIMA: WTI y Brent",
    author="Trabajo práctico - Predicción del precio del petróleo",
    subject="Explicación accesible del modelo ARIMA y sus resultados guardados",
)
doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width,
                                                         doc.height, id="f")], onPage=decorar)])
h = []

# 01 · Mirada general
h += [P("01 / UNA MIRADA GENERAL", "kicker"),
      P("Cómo pronosticamos el precio<br/>del petróleo con ARIMA", "h1"),
      P("Guía para entender el segundo modelo de series de tiempo de WTI y Brent", "h2"),
      P("El trabajo ya había usado <b>Holt con tendencia amortiguada</b>. Este documento explica el segundo "
        "enfoque: <b>ARIMA</b>. La idea es mirar cómo se relaciona cada precio con los anteriores y con los "
        "errores que el modelo cometió antes, y usar esa relación para proyectar los próximos pasos."),
      P("Se ajustó un ARIMA por separado para cada crudo. El programa elige solo la forma del modelo con "
        "reglas fijadas de antemano; por eso WTI y Brent terminaron con versiones distintas."),
      Spacer(1, 6),
      tarjetas([("2", "modelos independientes:<br/>uno para WTI y otro para Brent"),
                ("274", "cotizaciones del período 2:<br/>138 WTI y 136 Brent"),
                ("5", "precios diarios por crudo<br/>para la semana siguiente")]),
      Spacer(1, 10),
      P("Qué pregunta intenta responder", "h2"),
      P("<b>¿Qué precios podríamos esperar de lunes a viernes de la semana siguiente, usando solo la forma en "
        "que se movieron los precios pasados?</b> El modelo aprende únicamente del período 2, que el grupo "
        "asocia con el contexto de guerra. No incorpora noticias ni variables geopolíticas."),
      tabla([["Fecha del resultado", "Información disponible", "Semana pronosticada"],
             ["26/10/2026", "01/04/2026 al 14/10/2026", "2 al 6 de noviembre de 2026"]], [0.26, 0.37, 0.37],
            zebra=False),
      recuadro("La lectura principal",
               "WTI quedó cerca de <b>96,61 en promedio</b>, con una leve baja diaria; Brent quedó fijo en "
               "<b>126,55</b>, igual a su último precio. En la validación histórica ARIMA <b>empató exactamente</b> "
               "con repetir el último precio en ambos crudos, porque en todos los cortes eligió esa misma regla."),
      P("Este documento explica los datos, el funcionamiento del método, las pruebas realizadas y el sentido de "
        "los números. Reproduce las salidas guardadas de <b>arima_periodo_2_wti_brent.ipynb</b>; el notebook no "
        "se volvió a ejecutar para elaborar el PDF.", "note"),
      PageBreak()]

# 02 · Datos
h += [P("02 / LOS DATOS Y SU PREPARACIÓN", "kicker"),
      P("Los mismos precios que usó Holt", "h1"),
      P("Una serie de tiempo es una lista de valores ordenados por fecha. Aquí cada valor es una cotización "
        "diaria de petróleo publicada por EIA, expresada en dólares por barril."),
      tabla([["Crudo", "Primera cotización", "Última cotización", "Cantidad", "Demora al corte"],
             ["WTI", "01/04/2026", "14/10/2026", "138", "12 días"],
             ["Brent", "01/04/2026", "14/10/2026", "136", "12 días"]], [0.16, 0.22, 0.22, 0.16, 0.24]),
      P("La demora es la distancia entre el último precio disponible y la fecha de ejecución (26/10). El CSV "
        "local llegaba hasta el 14/10; el notebook lo informa como fuente atrasada.", "note"),
      imagen(FIGS / "series.png"),
      P("Figura elaborada a partir del CSV local del proyecto, con el mismo recorte del notebook. WTI y Brent se "
        "muestran juntos para compararlos; cada uno tiene su propio modelo.", "note"),
      tabla([["Qué se revisó", "Resultado guardado"],
             ["Nulos, precios no finitos y unidades distintas de USD/barril", "0 casos"],
             ["Duplicados completos y por fecha y crudo", "0 casos"],
             ["Series desconocidas (distintas de WTI y Brent)", "0 casos"],
             ["Filas fuera del período 2 o posteriores al corte", "1.128 filas excluidas"]], [0.65, 0.35]),
      P("No se inventaron precios para fines de semana ni fechas ausentes, y no se eliminaron los movimientos "
        "extremos: pueden reflejar hechos reales del período. Marzo de 2026 y el período 1 no participan."),
      PageBreak()]

# 03 · Método
h += [P("03 / EL MÉTODO, CON POCAS FÓRMULAS", "kicker"),
      P("Las tres letras de ARIMA(p, d, q)", "h1"),
      P("ARIMA es un nombre compuesto. Cada parte responde una pregunta distinta sobre la serie, y los tres "
        "números entre paréntesis indican cuánto se usa cada una."),
      P("d · Diferenciar: ¿mirar el precio o su cambio?", "h2"),
      P("Si el precio deambula sin volver a un valor típico, conviene modelar el <b>cambio</b> entre una "
        "cotización y la siguiente. d = 0 usa el precio tal cual; d = 1 usa la diferencia en USD por barril "
        "(no es un porcentaje)."),
      P("p · Autorregresión: ¿cuánto pesa el precio anterior?", "h2"),
      P("Con p = 1 el valor de hoy se explica en parte por el de la cotización anterior. Si ese peso es menor "
        "que 1, el precio tiende a volver poco a poco hacia un promedio."),
      P("q · Media móvil de errores: ¿se corrigen los errores pasados?", "h2"),
      P("Con q = 1 el modelo usa la sorpresa de la cotización anterior, es decir, cuánto se equivocó, para "
        "ajustar la siguiente. No es la media móvil de 20 cotizaciones que aparece en los gráficos del notebook."),
      Spacer(1, 4),
      P("Un ejemplo inventado para entenderlo", "h2"),
      P("Supongamos un promedio de largo plazo de 100, un último precio de 110 y un peso del 80 % para el dato "
        "anterior. Comparamos dos modelos sencillos:"),
      tabla([["Paso futuro", "ARIMA(1,0,0): vuelve al promedio", "ARIMA(0,1,0): repite el último precio"],
             ["1", "108,00", "110,00"], ["2", "106,40", "110,00"], ["3", "105,12", "110,00"]],
            [0.2, 0.4, 0.4]),
      P("Ejemplo didáctico: el promedio 100, el precio 110 y el 80 % no son resultados del TP. En el primer caso "
        "se calcula 100 + 0,8 × (precio anterior − 100). El segundo se conoce como <b>paseo aleatorio</b>: su "
        "mejor estimación es el último precio.", "note"),
      recuadro("Los dos modelos de este trabajo son justamente esos casos",
               "Para WTI se eligió <b>ARIMA(1,0,0) con constante</b>: el precio tiende a volver hacia un promedio. "
               "Para Brent se eligió <b>ARIMA(0,1,0) sin deriva</b>: el pronóstico repite el último precio. "
               "Las páginas siguientes explican por qué el programa llegó a resultados distintos."),
      PageBreak()]

# 04 · ACF y PACF
r_wti, r_brent = autocorr["WTI", "nivel"], autocorr["Brent", "nivel"]
pacf_dif_brent = fuera_de_banda("Brent", "diferencia", "pacf")
texto_dif_brent = ("ningún rezago" if not pacf_dif_brent else
                   "solo el rezago " + ", ".join(map(str, pacf_dif_brent)) + ", de forma aislada")
h += [P("04 / CÓMO SE PARECE CADA PRECIO A LOS ANTERIORES", "kicker"),
      P("Autocorrelación y autocorrelación parcial", "h1"),
      P("Antes de elegir el modelo conviene mirar cuánto se parece cada cotización a las anteriores. Un "
        "<b>rezago</b> cuenta cotizaciones hacia atrás: el rezago 1 es la anterior, el rezago 5 la de cinco "
        "publicaciones antes. Una correlación cercana a 1 indica que los precios se mueven muy juntos; cercana "
        "a 0, que no hay relación."),
      imagen(FIGS / "acf_pacf.png"),
      P("Figura elaborada con las 138 cotizaciones de WTI y 136 de Brent del período 2, hasta el 14/10, sobre "
        "el precio sin diferenciar. Las barras que salen de la zona gris se apartan de cero más de lo esperable "
        "por azar; alguna barra aislada puede salir por casualidad.", "note"),
      P("ACF: la memoria total", "h2"),
      P(f"Mide la correlación entre el precio y su valor k cotizaciones antes, sin separar caminos directos e "
        f"indirectos. En ambos crudos <b>baja muy despacio</b>: en WTI pasa de {n(r_wti['acf'][0])} en el rezago 1 "
        f"a {n(r_wti['acf'][9])} en el 10; en Brent, de {n(r_brent['acf'][0])} a {n(r_brent['acf'][9])}. Es la "
        "huella típica de una serie que deambula sin volver rápido a un nivel fijo."),
      P("PACF: la memoria directa", "h2"),
      P(f"Mide la relación con el rezago k <b>descontando</b> lo que ya explican los rezagos intermedios. Aquí "
        f"aparece <b>un solo pico grande en el rezago 1</b> ({n(r_wti['pacf'][0])} en WTI y "
        f"{n(r_brent['pacf'][0])} en Brent) y el resto queda casi en cero. Es decir: el precio de hoy depende "
        "sobre todo del de la cotización anterior; los más viejos influyen a través de él."),
      recuadro("Qué anticipan estos gráficos para el modelo",
               "Un pico único en la PACF apunta a un término autorregresivo de orden 1. Como ese valor está muy "
               "cerca de 1, no es claro si el precio vuelve a un promedio (p = 1 con d = 0) o se comporta como un "
               "paseo aleatorio (d = 1). Al tomar la variación diaria, la PACF ya no muestra estructura: "
               f"en WTI ningún rezago sale de la banda y en Brent sale {texto_dif_brent}. Los gráficos describen la "
               "dependencia; el orden lo deciden las pruebas de la página siguiente."),
      PageBreak()]

# 04 · Selección
h += [P("05 / CÓMO SE ELIGIÓ CADA MODELO", "kicker"),
      P("Primero d, después p y q", "h1"),
      P("El programa no prueba combinaciones al azar. Sigue dos etapas, siempre con los datos de entrenamiento "
        "y nunca con los precios que después se usan para evaluar."),
      P("Etapa 1: decidir si hay que diferenciar", "h2"),
      P("Se usan dos pruebas de estacionariedad, es decir, de si la serie oscila alrededor de un nivel estable. "
        "<b>KPSS</b> parte de suponer que sí lo hace; <b>ADF</b>, de suponer lo contrario. La regla fijada fue "
        "elegir el <b>menor d para el que KPSS no rechaza</b>, con significancia del 5 %. ADF se informa como "
        "control complementario."),
      imagen(FIGS / "kpss.png", 0.82),
      P("Figura elaborada con los valores p guardados del ajuste final (138 cotizaciones de WTI y 136 de "
        "Brent).", "note"),
      P("Los dos crudos quedaron prácticamente sobre el umbral. WTI obtuvo 0,051228 y KPSS no rechazó: se "
        "eligió <b>d = 0</b>. Brent obtuvo 0,049994 y KPSS rechazó por muy poco: se pasó a <b>d = 1</b>. Para "
        "WTI, además, ADF no rechazó la raíz unitaria (p = 0,245), así que el notebook marca la lectura como "
        "<b>no concluyente</b>."),
      P("Etapa 2: elegir p, q y el término fijo con AICc", "h2"),
      P("Con d ya decidido, se probaron 16 combinaciones por crudo (p y q de 0 a 2, con p + q ≤ 3, con y sin "
        "término fijo). Se eligió la de <b>menor AICc</b>. El AICc no agrega complejidad al modelo: sirve para "
        "<b>frenarla</b>. Un modelo con más parámetros casi siempre se ajusta mejor a los precios ya conocidos, "
        "aunque solo esté copiando ruido, y después pronostica peor. Por eso el AICc suma dos partes: una que "
        "<b>baja</b> cuanto mejor se ajusta el modelo y otra que <b>sube</b> por cada parámetro agregado. Un "
        "parámetro extra solo conviene si mejora el ajuste más de lo que cuesta."),
      P("Fórmula: AIC = −2·ln(L) + 2k, donde L es la verosimilitud y k la cantidad de parámetros; "
        "AICc = AIC + 2k(k+1)/(n−k−1) agrega un costo extra cuando hay pocos datos. El valor no está en dólares "
        "ni tiene sentido por sí solo: importa la diferencia entre candidatos del mismo crudo y el mismo d.",
        "note"),
      tabla([["Crudo", "Modelo elegido", "AICc", "Segundo mejor", "AICc"],
             ["WTI", "(1,0,0) con constante", "769,25", "(2,0,0) con constante", "770,56"],
             ["Brent", "(0,1,0) sin deriva", "812,37", "(1,1,1) sin deriva", "812,71"]],
            [0.12, 0.27, 0.12, 0.33, 0.16]),
      P("En Brent, ARIMA(1,1,1) tiene dos parámetros más que ARIMA(0,1,0) pero mejoró tan poco el ajuste que "
        "su AICc quedó apenas peor: ganó el más simple. En ambos crudos la distancia con el segundo es menor a "
        "2 puntos (1,31 en WTI y 0,34 en Brent), lo que suele leerse como una diferencia poco concluyente."),
      recuadro("Por qué importa ese límite tan fino",
               "La diferencia entre WTI y Brent no indica que sus mercados funcionen de manera opuesta. Indica que "
               "con pocos datos y alta volatilidad la prueba quedó en el borde. Si se suman cotizaciones, el orden "
               "elegido puede cambiar. Se respetó la regla fijada antes de ver los resultados."),
      PageBreak()]

# 05 · Validación
h += [P("06 / CÓMO SE PUSO A PRUEBA", "kicker"),
      P("Ensayar en el pasado antes de pronosticar", "h1"),
      P("Para evaluar un modelo, se hace de cuenta que aún no se conocen algunos precios históricos. Se entrena "
        "con lo anterior y después se compara lo pronosticado con lo que realmente ocurrió."),
      recuadro("La regla que evita una prueba engañosa",
               "En cada corte se vuelven a elegir d, p, q y el término fijo usando solo los precios anteriores. "
               "Los precios con los que se evalúa siempre están <b>después</b> del último dato de entrenamiento."),
      P("Por qué hubo que pronosticar 17 pasos", "h2"),
      P("La ejecución fue el 26 de octubre, pero el último precio disponible era del 14. Para llegar al viernes 6 "
        "de noviembre hubo que recorrer 17 fechas de lunes a viernes desde ese dato. La semana del 2 al 6 "
        "corresponde a los pasos 13 a 17; los doce anteriores son el camino intermedio."),
      Spacer(1, 6), *pasos(17, 5), Spacer(1, 4),
      P("Se repitió la prueba en tres cortes", "h2"),
      tabla([["Corte", "Último dato usado", "Cinco precios evaluados", "n WTI", "n Brent", "Modelo elegido"],
             ["1", "07/09", "24/09 al 30/09", "111", "109", "(0,1,0) en ambos"],
             ["2", "14/09", "01/10 al 07/10", "116", "114", "(0,1,0) en ambos"],
             ["3", "21/09", "08/10 al 14/10", "121", "119", "(0,1,0) en ambos"]],
            [0.1, 0.18, 0.25, 0.11, 0.11, 0.25]),
      P("Todas las fechas son de 2026. n es la cantidad de cotizaciones de entrenamiento. Cada corte pronostica "
        "17 pasos y evalúa los últimos cinco; las tres ventanas evaluadas no se superponen.", "note"),
      P("La referencia sencilla", "h2"),
      P("Se compara ARIMA con repetir el último precio conocido en todos los pasos futuros. Así se sabe si la "
        "complejidad adicional aporta algo. En total se evaluaron <b>15 cotizaciones por método y por crudo</b>."),
      PageBreak()]

# 06 · Resultados validación
h += [P("07 / RESULTADOS DE LA VALIDACIÓN", "kicker"),
      P("Un empate exacto, y por qué ocurrió", "h1"),
      P("<b>MAE</b> es el error absoluto promedio: un MAE de 4,40 significa que las predicciones se alejaron del "
        "precio real unos 4,40 dólares por barril en promedio. <b>RMSE</b> también resume el error, pero da más "
        "peso a los errores grandes. En ambos, un valor menor es mejor."),
      tabla([["Crudo", "Método", "MAE", "RMSE", "Precios evaluados"],
             ["WTI", "ARIMA", "4,40", "4,83", "15"], ["WTI", "Último precio", "4,40", "4,83", "15"],
             ["Brent", "ARIMA", "10,67", "11,40", "15"], ["Brent", "Último precio", "10,67", "11,40", "15"]],
            [0.16, 0.28, 0.16, 0.16, 0.24]),
      P("MAE y RMSE en USD por barril. Fuente: validación guardada del notebook.", "note"),
      P("Error por corte", "h2"),
      tabla([["Corte", "WTI · MAE", "WTI · RMSE", "Brent · MAE", "Brent · RMSE"],
             ["1", "5,06", "5,34", "12,88", "13,15"], ["2", "5,41", "5,66", "6,78", "7,78"],
             ["3", "2,73", "3,08", "12,35", "12,50"]], [0.16, 0.21, 0.21, 0.21, 0.21]),
      P("Los valores son iguales para ARIMA y para el último precio en cada corte.", "note"),
      P("Cómo leer este resultado", "h2"),
      P("En los seis ajustes de validación el programa eligió <b>ARIMA(0,1,0) sin deriva</b>. Ese modelo pronostica "
        "exactamente el último precio, de modo que el empate no es una casualidad: los dos métodos dieron los "
        "mismos números. Con 109 a 121 cotizaciones, ninguna estructura adicional mejoró el AICc lo suficiente."),
      P("Brent tuvo errores más grandes porque se movió con más fuerza en esas semanas, por ejemplo con el salto "
        "de fines de septiembre y comienzos de octubre."),
      recuadro("Qué se puede afirmar",
               "En estas 15 comparaciones por crudo, ARIMA no aportó una mejora frente a la referencia sencilla, "
               "porque eligió esa misma regla. Tres cortes no alcanzan para asegurar qué método ganará en otras "
               "semanas."),
      PageBreak()]

# 07 · Pronósticos
filas = [["Crudo", "Fecha", "Paso", "Pronóstico", "Límite inferior*", "Límite superior*"]]
for crudo in ("WTI", "Brent"):
    for fecha, (m, lo, hi), paso in zip(pd.bdate_range("2026-11-02", "2026-11-06"), SEMANA[crudo], range(13, 18)):
        filas.append([crudo, f"{fecha:%d/%m}", str(paso), n(m), n(lo), n(hi)])
h += [P("08 / LOS PRONÓSTICOS GUARDADOS", "kicker"),
      P("La semana del 2 al 6 de noviembre", "h1"),
      P("Terminada la validación, se eligió y ajustó otra vez el ARIMA con <b>todas</b> las cotizaciones del "
        "período 2. Con más datos, WTI pasó a d = 0 y quedó un modelo distinto al de la validación."),
      tabla(filas, [0.13, 0.13, 0.1, 0.18, 0.23, 0.23]),
      P("Todos los importes están en USD por barril. * Intervalo de predicción del 95 % calculado por "
        "statsmodels; su alcance se explica en la página siguiente.", "note"),
      tabla([["Crudo", "Último precio (14/10)", "Promedio de los cinco pronósticos", "Parámetros estimados"],
             ["WTI", "101,91", "96,61", "constante 93,47 · peso AR 0,936"],
             ["Brent", "126,55", "126,55", "sin coeficientes de rezago"]], [0.13, 0.22, 0.3, 0.35]),
      P("Por qué WTI baja y Brent no", "h2"),
      P("En WTI el modelo estima un promedio de <b>93,47</b> y un peso de <b>0,936</b> para el precio anterior. "
        "Como el último precio, 101,91, está por encima de ese promedio, cada paso recorre una parte de la "
        "distancia hacia él. Después de 13 pasos queda en 97,04 y llega a 96,21 el viernes."),
      P("En Brent el paseo aleatorio no tiene a qué valor volver: su mejor estimación es 126,55 en todos los pasos."),
      recuadro("Qué significa esta diferencia",
               "La baja de WTI es una consecuencia del modelo elegido, no una señal de mercado detectada. Si la "
               "prueba KPSS hubiera caído del otro lado del umbral, WTI también habría repetido su último precio. "
               "Ninguno de los dos pronósticos anticipa nuevos acontecimientos."),
      PageBreak()]

# 08 · Incertidumbre
h += [P("09 / LA INCERTIDUMBRE", "kicker"),
      P("El precio estimado y el margen de duda", "h1"),
      P("La línea punteada recorre los 17 pasos desde el último dato; los puntos marcan la semana objetivo. La "
        "zona sombreada es el intervalo de predicción del 95 % bajo los supuestos del modelo."),
      imagen(FIGS / "pronostico.png"),
      P("Figura elaborada con las cotizaciones del CSV y los parámetros guardados. El recorrido intermedio se "
        "recalculó con esos parámetros y coincide con la tabla guardada de la semana objetivo. La línea vertical "
        "marca el último dato observado.", "note"),
      P("Por qué las bandas se abren distinto", "h2"),
      P("Las bandas salen directamente de las fórmulas del ARIMA, sin simulación. En <b>Brent</b>, el paseo "
        "aleatorio acumula incertidumbre en cada paso y la banda se sigue abriendo: el viernes 6 va de "
        "<b>87,23 a 165,87</b>. En <b>WTI</b>, la vuelta al promedio frena ese crecimiento y la banda casi se "
        "estabiliza: el viernes va de <b>76,13 a 116,29</b>."),
      P("Los intervalos suponen errores normales e independientes, y no incluyen la incertidumbre de haber elegido "
        "el orden ni de estimar los parámetros. Su cobertura del 95 % no fue comprobada en el TP, y la banda de "
        "cada día no garantiza cubrir toda la semana en conjunto.", "note"),
      PageBreak()]

# 09 · Residuos
h += [P("10 / LO QUE QUEDA SIN EXPLICAR", "kicker"),
      P("Residuos: revisar lo que el modelo no capturó", "h1"),
      P("Los residuos son los errores de un paso dentro del entrenamiento. Se revisan <b>estandarizados</b>: "
        "divididos por su desvío esperado, de modo que un modelo adecuado debería dejar valores centrados en cero "
        "y con desvío cercano a 1. Son distintos de los errores de validación, que se calcularon sobre precios "
        "posteriores al corte."),
      tabla([["Crudo", "Residuos", "Media", "Desvío", "Mayores a 3 desvíos"],
             ["WTI", "138", "−0,025", "1,003", "3"], ["Brent", "135", "0,011", "1,004", "3"]],
            [0.16, 0.16, 0.2, 0.2, 0.28]),
      P("Valores sin unidad. En Brent se excluye la primera observación, que la diferenciación no permite usar.",
        "note"),
      P("Ljung–Box: ¿queda dependencia entre errores?", "h2"),
      P("La prueba revisa si los residuos siguen correlacionados hasta cierto rezago. Un valor p menor a 0,05 "
        "indicaría que queda estructura sin modelar."),
      tabla([["Crudo", "Rezago 5", "Rezago 10", "Rezago 20", "Lectura"],
             ["WTI", "0,776", "0,941", "0,886", "No se rechaza ausencia de autocorrelación"],
             ["Brent", "0,357", "0,323", "0,195", "No se rechaza ausencia de autocorrelación"]],
            [0.12, 0.13, 0.13, 0.13, 0.49]),
      P("Valores p de Ljung–Box guardados en el notebook.", "note"),
      P("Qué dicen las colas", "h2"),
      P("Cada crudo tiene <b>3 residuos</b> que superan los tres desvíos; bajo una distribución normal, en una "
        "muestra de este tamaño se esperaría menos de uno. El gráfico Q–Q del notebook confirma que los extremos "
        "son más grandes de lo que supone la normal. Es otra razón para leer las bandas con cautela."),
      recuadro("Qué se puede concluir",
               "No aparece dependencia que el modelo haya dejado sin usar, pero eso no demuestra que se cumplan "
               "todos los supuestos. Los saltos bruscos y los cambios de volatilidad, típicos del período, no "
               "forman parte de un ARIMA."),
      PageBreak()]

# 10 · Prueba histórica
filas_p = [["Crudo", "Fecha", "Real", "ARIMA", "Error ARIMA", "Error último precio"]]
for crudo in ("WTI", "Brent"):
    d = PRUEBA[crudo]
    for fecha, real, pred in zip(fechas_prueba, d["real"], d["arima"]):
        filas_p.append([crudo, f"{fecha:%d/%m}", n(real), n(pred), n(real - pred).replace("-", "−"),
                        n(abs(real - d["ultimo"]))])
h += [P("11 / UNA SEMANA YA CONOCIDA", "kicker"),
      P("Prueba histórica: 5 al 9 de octubre", "h1"),
      P("Se simuló lo que se habría pronosticado al cierre del viernes 2 de octubre y se comparó con los precios "
        "reales publicados después. El modelo se eligió y ajustó con las cotizaciones hasta ese viernes; los "
        "precios de la semana solo se usaron para evaluar."),
      imagen(FIGS / "prueba.png"),
      P("Figura elaborada con la tabla guardada del punto 10 del notebook.", "note"),
      tabla(filas_p, [0.12, 0.12, 0.15, 0.15, 0.2, 0.26]),
      P("Error ARIMA = real − pronóstico; negativo significa que ARIMA quedó por encima. La última columna es "
        "el error absoluto de repetir el último precio (97,89 en WTI y 135,51 en Brent).", "note"),
      tabla([["Crudo", "Modelo elegido al 02/10", "MAE ARIMA", "MAE último precio"],
             ["WTI", "(0,1,0) sin deriva", "1,50", "1,50"], ["Brent", "(1,0,0) con constante", "5,49", "8,08"]],
            [0.15, 0.37, 0.24, 0.24]),
      P("En esta semana el ARIMA de Brent, que con los datos hasta el 2/10 había elegido d = 0, previó una "
        "vuelta hacia el promedio y redujo el error en <b>2,59 USD por barril</b>. WTI repitió el último precio y "
        "empató. Es una sola semana: no basta para concluir que un método sea mejor en general."),
      PageBreak()]

# 11 · Repaso
h += [P("12 / REPASO Y FUENTES", "kicker"),
      P("Cómo contarlo y qué falta comparar", "h1"),
      P("Frente a Holt", "h2"),
      P("Holt y ARIMA se ejecutaron con fechas de referencia distintas (20/10 y 26/10). Por eso pronostican semanas "
        "distintas y validaron con cortes y horizontes distintos: 12 pasos para Holt y 17 para ARIMA. "
        "Sus MAE <b>no se pueden comparar directamente</b>. Lo que sí coincide es la conclusión: ninguno de los dos "
        "superó con claridad a repetir el último precio. Para una comparación justa, ambos notebooks deberían "
        "ejecutarse con la misma <b>FECHA_REFERENCIA</b> y el mismo CSV."),
      P("Palabras útiles para explicar el trabajo", "h2"),
      tabla([["Palabra", "En lenguaje sencillo"],
             ["Estacionaria", "Serie que oscila alrededor de un nivel estable, sin desplazarse indefinidamente."],
             ["Diferenciar (d)", "Modelar el cambio entre cotizaciones en lugar del precio."],
             ["Autorregresión (p)", "Usar los precios anteriores para explicar el actual."],
             ["Media móvil de errores (q)", "Usar las sorpresas anteriores para ajustar la siguiente estimación."],
             ["Paseo aleatorio", "ARIMA(0,1,0): la mejor estimación es el último precio."],
             ["AICc", "Puntaje para elegir entre candidatos: baja con el buen ajuste y sube con cada parámetro; gana el menor."],
             ["Validación temporal", "Probar el método con precios posteriores a cada entrenamiento."]],
            [0.3, 0.7]),
      P("Una forma de contarlo oralmente", "h2"),
      recuadro("Resumen en cinco frases",
               "Tomamos los precios de WTI y Brent del período 2 y revisamos que estuvieran limpios. Ajustamos un "
               "ARIMA por crudo: primero decidimos si modelar el precio o su cambio, y después elegimos la forma más "
               "simple con mejor puntaje. En tres cortes del pasado el modelo eligió repetir el último precio, así "
               "que empató con la referencia. Con todos los datos, WTI pasó a un modelo que vuelve hacia 93,47 y "
               "Brent siguió repitiendo 126,55. Las bandas son amplias y el modelo no anticipa acontecimientos."),
      P("De dónde salen los números", "h2"),
      P("Fuente principal: salidas guardadas de notebooks/arima_periodo_2_wti_brent.ipynb, fecha de referencia "
        "26/10/2026, CSV eia_precios_crudo_diarios_2024-01_a_2026-10.csv. Las tablas reproducen sus valores "
        "redondeados. Los gráficos se elaboraron para este informe sin volver a entrenar el modelo; se verificaron "
        "cantidades, últimos precios y pronósticos contra las salidas guardadas.", "note"),
      P("1. EIA: precios spot diarios de petróleo · 2. statsmodels: ARIMA y get_forecast · 3. statsmodels: ADF, "
        "KPSS y Ljung–Box · 4. Hyndman y Athanasopoulos, Forecasting: Principles and Practice: ARIMA y "
        "validación temporal.", "note"),
      P(f"Ejecución de origen: Python 3.11.9, pandas 2.3.3, NumPy 2.4.6 y statsmodels 0.15.0. Elaboración del "
        f"PDF: {ELABORADO}. La fecha de elaboración no implica una nueva consulta de precios.", "note")]

doc.build(h)
print(f"OK: {SALIDA}")
