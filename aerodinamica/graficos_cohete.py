"""Figuras del CP con el dibujo del cohete al lado (los cálculos están en cp_barrowman.py).

Uso:  python3 graficos_cohete.py      (genera figuras/cohete/)
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import ConnectionPatch, Polygon, Rectangle
from matplotlib.ticker import FuncFormatter

import cp_barrowman as cp

AZUL, NARANJA, VERDE, AMARILLO = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
TINTA, TINTA_2, REJILLA, ZONA, CASCO = "#1f1f1e", "#6b6a64", "#e9e8e3", "#efeee9", "#d9d8d2"
COLORES = {"Ojiva": AZUL, "Aletas": NARANJA, "Cuerpo (sustentación)": VERDE,
           "Transición de cola": AMARILLO}
ZOOM = (1.12, 2.12)  # tramo del cohete que se amplía a la derecha (m desde la punta)
COMA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))

plt.rcParams.update({"font.family": "Helvetica", "font.size": 11, "axes.titlesize": 13,
                     "axes.labelcolor": TINTA, "text.color": TINTA,
                     "pdf.fonttype": 42})  # fuente TrueType incrustada: el PDF se ve igual en LaTeX


def coma(v, d=1):
    return f"{v:.{d}f}".replace(".", ",")


def estilo(ax):
    ax.grid(color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(TINTA_2)
    ax.tick_params(colors=TINTA_2)
    ax.xaxis.set_major_formatter(COMA)
    ax.yaxis.set_major_formatter(COMA)


def dibujar_cohete(ax, marcas):
    """Silueta de Camões en vertical (punta arriba). marcas: [(x, texto, color, símbolo[, desplazamiento])]."""
    x = np.linspace(0, cp.X_TRANSICION + cp.L_TRANSICION, 600)
    r = cp.radio(x)
    ax.fill_betweenx(x, -r, r, color=CASCO, edgecolor=TINTA_2, linewidth=1)
    raiz = cp.X_ALETAS
    for lado in (1, -1):
        aleta = [(lado * cp.R, raiz), (lado * (cp.R + cp.S), raiz + cp.X_T),
                 (lado * (cp.R + cp.S), raiz + cp.X_T + cp.CT), (lado * cp.R, raiz + cp.CR)]
        ax.add_patch(Polygon(aleta, closed=True, facecolor=CASCO, edgecolor=TINTA_2, linewidth=1))
    for pos, texto, color, simbolo, *desplazamiento in marcas:
        y_texto = pos + (desplazamiento[0] if desplazamiento else 0)
        ax.plot(0, pos, simbolo, color=color, markersize=9, markeredgewidth=2,
                markerfacecolor="white" if simbolo == "o" else color, zorder=5)
        ax.annotate(texto, (0, pos), xytext=(0.36, y_texto), color=color, fontsize=9.5, va="center",
                    arrowprops=dict(arrowstyle="-", color=color, linewidth=0.8))
    ax.add_patch(Rectangle((-0.3, ZOOM[0]), 0.6, ZOOM[1] - ZOOM[0], fill=False,
                           edgecolor=TINTA_2, linestyle=(0, (3, 3)), linewidth=1))
    ax.set_xlim(-0.3, 1.25)
    ax.set_ylim(2.62, -0.08)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(0, -0.06, "punta", ha="center", va="bottom", color=TINTA_2, fontsize=9)


def conectar(fig, ax_cohete, ax_curva):
    """Líneas del recuadro del cohete al panel ampliado."""
    for y in ZOOM:
        fig.add_artist(ConnectionPatch(xyA=(0.3, y), coordsA=ax_cohete.transData,
                                       xyB=(0, y), coordsB=ax_curva.get_yaxis_transform(),
                                       color=TINTA_2, linewidth=0.8, linestyle=(0, (3, 3))))


def lineas_cg(ax, x_max):
    for cg, texto, trazo in ((cp.CG_DESPEGUE, "CG al despegue", "--"),
                             (cp.CG_FIN_COMBUSTION, "CG tras la combustión", ":")):
        ax.axhline(cg, color=TINTA_2, linestyle=trazo, linewidth=1.5)
        ax.text(x_max, cg - 0.012, texto, color=TINTA_2, ha="right", va="bottom", fontsize=9.5)


def flecha_margen(ax, x, x_cp, izquierda=False):
    ax.annotate("", xy=(x, x_cp), xytext=(x, cp.CG_DESPEGUE),
                arrowprops=dict(arrowstyle="<->", color=TINTA_2, linewidth=1))
    margen = (x_cp - cp.CG_DESPEGUE) / cp.D
    ax.text(x, (x_cp + cp.CG_DESPEGUE) / 2, f" margen estático \n {coma(margen)} calibres ",
            color=TINTA_2, va="center", ha="right" if izquierda else "left", fontsize=9.5)


def lienzo(titulo, subtitulo):
    fig = plt.figure(figsize=(11, 7.6))
    rejilla = fig.add_gridspec(2, 2, width_ratios=[1.05, 2.6], height_ratios=[3, 2],
                               wspace=0.08, hspace=0.12, left=0.02, right=0.98, top=0.86,
                               bottom=0.08)
    ax_cohete = fig.add_subplot(rejilla[:, 0])
    ax_cp = fig.add_subplot(rejilla[0, 1])
    ax_cn = fig.add_subplot(rejilla[1, 1], sharex=ax_cp)
    fig.text(0.02, 0.95, titulo, fontsize=16, fontweight="bold")
    fig.text(0.02, 0.915, subtitulo, fontsize=11, color=TINTA_2)
    for ax in (ax_cp, ax_cn):
        estilo(ax)
    ax_cp.set_ylim(ZOOM[1], ZOOM[0])  # mismo sentido que el cohete: punta arriba
    ax_cp.set_ylabel("Posición desde la punta (m)")
    plt.setp(ax_cp.get_xticklabels(), visible=False)
    return fig, ax_cohete, ax_cp, ax_cn


def figura_mach(carpeta):
    machs = np.linspace(0.05, 2.5, 500)
    cps = np.array([cp.x_cp(m) for m in machs])
    fig, ax_cohete, ax_cp, ax_cn = lienzo(
        "Centro de presiones frente al número de Mach",
        "Cohete Camões (EuRoC'23), α ≈ 0, método de Barrowman")

    dibujar_cohete(ax_cohete, [
        (cp.X_NARIZ, "fuerza de la ojiva", AZUL, "s"),
        (cp.CG_FIN_COMBUSTION, "CG tras la combustión", TINTA_2, "o"),
        (cp.CG_DESPEGUE, "CG al despegue", TINTA, "o"),
        (cps.min(), f"CP a Mach {machs[cps.argmin()]:.3g}".replace(".", ","), AZUL, "x"),
        (cp.x_cp(0.3), "CP a Mach 0,3", AZUL, "x"),
        (cps.max(), f"CP a Mach {machs[cps.argmax()]:.3g}".replace(".", ","), AZUL, "x"),
        (cp.x_cp_aletas(0.3), "fuerza de las aletas", NARANJA, "s"),
    ])
    conectar(fig, ax_cohete, ax_cp)

    for ax in (ax_cp, ax_cn):
        ax.axvspan(cp.M_SUB, cp.M_SUP, color=ZONA, linewidth=0, zorder=0)
    for xm, texto in ((0.45, "subsónico"), (1.075, "transónico"), (1.9, "supersónico")):
        ax_cp.text(xm, ZOOM[1] - 0.015, texto, ha="center", va="bottom", color=TINTA_2,
                   fontsize=9.5)
    ax_cp.plot(machs, cps, color=AZUL, linewidth=2.5)
    ax_cp.text(2.5, cps[-1] + 0.03, "CP", color=AZUL, fontweight="bold", ha="right", va="top")
    lineas_cg(ax_cp, 2.5)
    flecha_margen(ax_cp, 0.3, cp.x_cp(0.3))
    flecha_margen(ax_cp, 2.35, cp.x_cp(2.35), izquierda=True)

    ax_cn.plot(machs, [cp.cna_aletas(m) for m in machs], color=NARANJA, linewidth=2.5)
    ax_cn.plot(machs, np.full_like(machs, cp.CNA_NARIZ), color=AZUL, linewidth=2.5)
    ax_cn.text(0.1, 11.2, "Aletas", color=NARANJA, fontweight="bold")
    ax_cn.text(0.1, 2.6, "Ojiva", color=AZUL, fontweight="bold")
    ax_cn.set_ylim(0, 16)
    ax_cn.set_ylabel("$C_{N\\alpha}$ (1/rad)")
    ax_cn.set_xlabel("Número de Mach")
    guardar(fig, carpeta, "cp_frente_mach")


def figura_alfa(carpeta, mach=0.3):
    alfas = np.linspace(0.1, 15, 300)
    cps = np.array([cp.x_cp(mach, np.radians(a)) for a in alfas])
    fig, ax_cohete, ax_cp, ax_cn = lienzo(
        "Centro de presiones frente al ángulo de ataque",
        f"Cohete Camões (EuRoC'23), Mach {coma(mach)}, Barrowman extendido (Galejs)")

    dibujar_cohete(ax_cohete, [
        (cp.X_NARIZ, "fuerza de la ojiva", AZUL, "s"),
        (cp.CG_FIN_COMBUSTION, "CG tras la combustión", TINTA_2, "o"),
        (cp.X_PLANTA, "fuerza del cuerpo", VERDE, "s", -0.035),
        (cp.CG_DESPEGUE, "CG al despegue", TINTA, "o", 0.035),
        (cps[-1], "CP a α = 15°", AZUL, "x"),
        (cps[0], "CP a α ≈ 0°", AZUL, "x"),
        (cp.x_cp_aletas(mach), "fuerza de las aletas", NARANJA, "s"),
    ])
    conectar(fig, ax_cohete, ax_cp)

    ax_cp.plot(alfas, cps, color=AZUL, linewidth=2.5)
    ax_cp.text(15, cps[-1] + 0.03, "CP", color=AZUL, fontweight="bold", ha="right", va="top")
    lineas_cg(ax_cp, 15)
    flecha_margen(ax_cp, 1, cp.x_cp(mach, np.radians(1)))
    flecha_margen(ax_cp, 13.5, cp.x_cp(mach, np.radians(13.5)), izquierda=True)

    for nombre, color in COLORES.items():
        cn = [cp.contribuciones(mach, np.radians(a))[nombre][0] for a in alfas]
        ax_cn.plot(alfas, cn, color=color, linewidth=2.5)
        ax_cn.text(14.8, cn[-1] + (-0.08 if cn[-1] < 0 else 0.08), nombre, color=color,
                   fontweight="bold", ha="right", va="top" if cn[-1] < 0 else "bottom", fontsize=9.5)
    ax_cn.axhline(0, color=TINTA_2, linewidth=0.8)
    ax_cn.set_xlim(0, 15.3)
    ax_cn.set_ylim(-0.75, 3.1)
    ax_cn.set_ylabel("Fuerza normal $C_N$")
    ax_cn.set_xlabel("Ángulo de ataque α (°)")
    guardar(fig, carpeta, "cp_frente_alfa")


def guardar(fig, carpeta, nombre):
    fig.savefig(carpeta / f"{nombre}.pdf")
    fig.savefig(carpeta / f"{nombre}.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    cp.comprobar()
    carpeta = Path(__file__).parent / "figuras" / "cohete"
    carpeta.mkdir(parents=True, exist_ok=True)
    figura_mach(carpeta)
    figura_alfa(carpeta)
    print("figuras en", carpeta)
