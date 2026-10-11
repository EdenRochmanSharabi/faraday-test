"""Centro de presiones del cohete Camões (EuRoC'23) en función del Mach y del ángulo de ataque.

Método de Barrowman, con:
  - compresibilidad de las aletas: Diederich/Prandtl-Glauert en subsónico y teoría lineal
    supersónica (Ackeret) con corrección de punta en supersónico;
  - desplazamiento del CP de las aletas hacia la mitad de la cuerda en supersónico;
  - sustentación del cuerpo a ángulos de ataque altos (Barrowman extendido, Galejs).

x se mide en metros desde la punta de la ojiva, positivo hacia la cola.
Uso:  python3 cp_barrowman.py      (genera las figuras en figuras/)
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

# Geometría de Camões (Rocket Experiment Division, EuRoC'23), tomada del ejemplo de RocketPy:
# https://github.com/RocketPy-Team/RocketPy/blob/master/docs/examples/camoes_flight_sim.ipynb
R = 0.0715                 # radio del cuerpo (m)
D = 2 * R
A_REF = np.pi * R**2       # área de referencia: sección del cuerpo
L_NARIZ = 0.455            # ojiva Von Kármán
X_TRANSICION = 2.475       # inicio de la transición de cola (boattail)
L_TRANSICION = 0.048
R_COLA = 0.037             # radio al final de la transición
N_ALETAS = 4
CR, CT, S = 0.185, 0.15, 0.155   # cuerda en la raíz, cuerda en la punta, envergadura
X_T = CR - CT              # flecha del borde de ataque (RocketPy: borde de salida perpendicular)
X_ALETAS = 2.275           # borde de ataque de la raíz

# Centro de gravedad (de los datos de masa del mismo ejemplo): cohete sin propulsante 22,8 kg con
# el CG en x = 1,188 m; propulsante 8,33 kg con el CG en x = 1,945 m.
CG_DESPEGUE = (22.8 * 1.1884 + 8.33 * 1.945) / (22.8 + 8.33)
CG_FIN_COMBUSTION = 1.1884

K_GALEJS = 1.1             # coeficiente de sustentación del cuerpo (Galejs)
M_SUB, M_SUP = 0.9, 1.25   # zona transónica: se interpola entre estos dos Mach


def radio_von_karman(x):
    theta = np.arccos(1 - 2 * x / L_NARIZ)
    return R / np.sqrt(np.pi) * np.sqrt(theta - np.sin(2 * theta) / 2)


def radio(x):
    """Perfil del cuerpo: ojiva, tubo y transición de cola."""
    x = np.asarray(x, dtype=float)
    r = np.where(x < L_NARIZ, radio_von_karman(np.clip(x, 0, L_NARIZ)), R)
    en_cola = x > X_TRANSICION
    return np.where(en_cola, R + (R_COLA - R) * (x - X_TRANSICION) / L_TRANSICION, r)


def cp_cuerpo_de_revolucion(perfil, longitud):
    """CP de una ojiva por teoría de cuerpo esbelto: X = L - V / A_base."""
    x = np.linspace(0, longitud, 4001)
    volumen = np.trapezoid(np.pi * perfil(x) ** 2, x)
    return longitud - volumen / (np.pi * perfil(longitud) ** 2)


# --- Contribuciones que no dependen del Mach (teoría de cuerpo esbelto) ---
CNA_NARIZ = 2.0
X_NARIZ = cp_cuerpo_de_revolucion(radio_von_karman, L_NARIZ)

d_rel = R_COLA / R
CNA_COLA = 2 * (d_rel**2 - 1)            # negativa: la transición empuja hacia el lado contrario
X_COLA = X_TRANSICION + L_TRANSICION / 3 * (1 + (1 - 1 / d_rel) / (1 - (1 / d_rel) ** 2))

# --- Aletas: geometría ---
A_ALETA = (CR + CT) / 2 * S
ALARGAMIENTO = 2 * S**2 / A_ALETA        # de la pareja de aletas enfrentadas
TAN_FLECHA_MEDIA = (X_T + CT / 2 - CR / 2) / S
CUERDA_MEDIA = 2 / 3 * (CR + CT - CR * CT / (CR + CT))        # cuerda media aerodinámica (MAC)
X_CUERDA_MEDIA = X_ALETAS + X_T / 3 * (CR + 2 * CT) / (CR + CT)  # borde de ataque de la MAC
INTERFERENCIA = 1 + R / (S + R)          # el cuerpo aumenta la fuerza de las aletas


def cna_una_aleta_por_area(mach):
    """dCN/dα de una aleta, por unidad de área de la aleta (1/rad)."""
    def subsonico(m):  # Diederich, con Prandtl-Glauert en β
        beta = np.sqrt(1 - m**2)
        cos_flecha = 1 / np.sqrt(1 + TAN_FLECHA_MEDIA**2)
        sa = S**2 / A_ALETA
        return 2 * np.pi * sa / (1 + np.sqrt(1 + (beta * sa / cos_flecha) ** 2))

    def supersonico(m):  # Ackeret con la pérdida de punta de un ala de poco alargamiento
        beta = np.sqrt(m**2 - 1)
        return 4 / beta * (1 - 1 / (2 * ALARGAMIENTO * beta))

    if mach <= M_SUB:
        return subsonico(mach)
    if mach >= M_SUP:
        return supersonico(mach)
    # Simplificación: interpolación lineal en la zona transónica, donde ninguna de las dos teorías vale
    f = (mach - M_SUB) / (M_SUP - M_SUB)
    return (1 - f) * subsonico(M_SUB) + f * supersonico(M_SUP)


def cna_aletas(mach):
    """dCN/dα de todo el conjunto de aletas, referido a A_REF (1/rad)."""
    return N_ALETAS / 2 * cna_una_aleta_por_area(mach) * A_ALETA / A_REF * INTERFERENCIA


def x_cp_aletas(mach):
    """En subsónico el CP de la aleta está al 25 % de la MAC; en supersónico se va hacia la mitad."""
    if mach <= 0.5:
        fraccion = 0.25
    else:
        beta = np.sqrt(max(mach**2 - 1, 1e-9))
        sup = (ALARGAMIENTO * beta - 0.67) / (2 * ALARGAMIENTO * beta - 1)  # válida para M ≥ 2
        sup_2 = (ALARGAMIENTO * np.sqrt(3) - 0.67) / (2 * ALARGAMIENTO * np.sqrt(3) - 1)
        # Simplificación: entre M 0,5 y 2 se interpola linealmente, como aproximación a OpenRocket
        fraccion = 0.25 + (sup_2 - 0.25) * min((mach - 0.5) / 1.5, 1) if mach < 2 else sup
    return X_CUERDA_MEDIA + fraccion * CUERDA_MEDIA


# --- Sustentación del cuerpo (solo importa a ángulos de ataque altos) ---
_x = np.linspace(0, X_TRANSICION + L_TRANSICION, 6001)
_ancho = 2 * radio(_x)
A_PLANTA = np.trapezoid(_ancho, _x)
X_PLANTA = np.trapezoid(_ancho * _x, _x) / A_PLANTA


def contribuciones(mach, alfa_rad):
    """Fuerza normal (CN) y punto de aplicación de cada pieza."""
    s = np.sin(alfa_rad)
    return {
        "Ojiva": (CNA_NARIZ * s, X_NARIZ),
        "Aletas": (cna_aletas(mach) * s, x_cp_aletas(mach)),
        "Cuerpo (sustentación)": (K_GALEJS * A_PLANTA / A_REF * s**2, X_PLANTA),
        "Transición de cola": (CNA_COLA * s, X_COLA),
    }


def x_cp(mach, alfa_rad=np.radians(0.5)):
    piezas = contribuciones(mach, alfa_rad).values()
    return sum(cn * x for cn, x in piezas) / sum(cn for cn, _ in piezas)


def comprobar():
    """Comprobaciones con resultados conocidos, para que los números no salgan de la nada."""
    cono = cp_cuerpo_de_revolucion(lambda x: R * np.asarray(x) / L_NARIZ, L_NARIZ)
    assert abs(cono - 2 / 3 * L_NARIZ) < 1e-4, "cono: el CP debe estar a 2/3 de su longitud"
    assert abs(X_NARIZ / L_NARIZ - 0.5) < 0.01, "Von Kármán: CP en torno a la mitad de la ojiva"
    # Fórmula clásica de Barrowman para el CP de las aletas = 25 % de la MAC
    barrowman = X_ALETAS + X_T / 3 * (CR + 2 * CT) / (CR + CT) + (CR + CT - CR * CT / (CR + CT)) / 6
    assert abs(barrowman - x_cp_aletas(0.1)) < 1e-9
    # Fórmula clásica de Barrowman para la fuerza de las aletas (incompresible)
    l_f = np.hypot(S, X_T + CT / 2 - CR / 2)
    cna_barrowman = 4 * N_ALETAS * (S / D) ** 2 / (1 + np.sqrt(1 + (2 * l_f / (CR + CT)) ** 2))
    assert abs(cna_aletas(0.01) / (cna_barrowman * INTERFERENCIA) - 1) < 0.01
    assert x_cp(0.3, np.radians(10)) < x_cp(0.3, np.radians(1)), "con α el CP debe adelantarse"
    assert CG_FIN_COMBUSTION < CG_DESPEGUE < x_cp(0.3), "cohete estable: CP detrás del CG"


COLORES = {"Ojiva": "#2a78d6", "Aletas": "#eb6834", "Cuerpo (sustentación)": "#1baf7a",
           "Transición de cola": "#eda100"}
TINTA, TINTA_2, REJILLA = "#1f1f1e", "#6b6a64", "#e4e3dd"


def estilo(ax):
    ax.grid(color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(TINTA_2)
    ax.tick_params(colors=TINTA_2)
    coma = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))  # decimales con coma
    ax.xaxis.set_major_formatter(coma)
    ax.yaxis.set_major_formatter(coma)
    ax.xaxis.label.set_color(TINTA)
    ax.yaxis.label.set_color(TINTA)


def lineas_cg(ax, x_max):
    for cg, texto, trazo in ((CG_DESPEGUE, "CG al despegue", "--"),
                             (CG_FIN_COMBUSTION, "CG tras la combustión", ":")):
        ax.axhline(cg, color=TINTA_2, linestyle=trazo, linewidth=1.5)
        ax.text(x_max, cg - 0.01, texto, color=TINTA_2, ha="right", va="bottom", fontsize=9)


def flecha_margen(ax, x, cp):
    """Marca el margen estático al despegue en el punto x."""
    ax.annotate("", xy=(x, cp), xytext=(x, CG_DESPEGUE),
                arrowprops=dict(arrowstyle="<->", color=TINTA_2, linewidth=1))
    ax.text(x, (cp + CG_DESPEGUE) / 2, f"  margen estático\n  {(cp - CG_DESPEGUE) / D:.1f} calibres".replace(".", ","),
            color=TINTA_2, va="center", fontsize=9)


def figura_mach(carpeta):
    machs = np.linspace(0.05, 2.5, 400)
    cp = np.array([x_cp(m) for m in machs])
    fig, (arriba, abajo) = plt.subplots(2, 1, figsize=(7.5, 7), sharex=True,
                                        gridspec_kw={"height_ratios": [3, 2]})
    for ax in (arriba, abajo):
        estilo(ax)
        ax.axvspan(M_SUB, M_SUP, color=REJILLA, alpha=0.6, linewidth=0)
    arriba.plot(machs, cp, color=COLORES["Ojiva"], linewidth=2)
    lineas_cg(arriba, 2.5)
    flecha_margen(arriba, 0.3, x_cp(0.3))
    arriba.invert_yaxis()  # la punta del cohete arriba, la cola abajo
    arriba.set_ylabel("Posición del CP desde la punta (m)")
    arriba.set_title("Camões: centro de presiones frente al Mach (α ≈ 0)", color=TINTA, loc="left")
    arriba.text(1.075, arriba.get_ylim()[0] - 0.01, "transónico", ha="center", va="bottom",
                color=TINTA_2, fontsize=9)

    abajo.plot(machs, [cna_aletas(m) for m in machs], color=COLORES["Aletas"], linewidth=2,
               label="Aletas")
    abajo.plot(machs, np.full_like(machs, CNA_NARIZ), color=COLORES["Ojiva"], linewidth=2,
               label="Ojiva")
    abajo.set_ylabel("$C_{N\\alpha}$ (1/rad)")
    abajo.set_xlabel("Número de Mach")
    abajo.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(carpeta / "cp_frente_mach.png", dpi=200)


def figura_alfa(carpeta, mach=0.3):
    alfas = np.linspace(0.1, 15, 300)
    cp = np.array([x_cp(mach, np.radians(a)) for a in alfas])
    fig, (arriba, abajo) = plt.subplots(2, 1, figsize=(7.5, 7), sharex=True,
                                        gridspec_kw={"height_ratios": [3, 2]})
    for ax in (arriba, abajo):
        estilo(ax)
    arriba.plot(alfas, cp, color=COLORES["Ojiva"], linewidth=2)
    lineas_cg(arriba, 15)
    flecha_margen(arriba, 1, x_cp(mach, np.radians(1)))
    flecha_margen(arriba, 14, x_cp(mach, np.radians(14)))
    arriba.invert_yaxis()
    arriba.set_ylabel("Posición del CP desde la punta (m)")
    arriba.set_title(f"Camões: centro de presiones frente al ángulo de ataque (Mach {mach:g})".replace(".", ","),
                     color=TINTA, loc="left")

    for nombre in COLORES:
        cn = [contribuciones(mach, np.radians(a))[nombre][0] for a in alfas]
        abajo.plot(alfas, cn, color=COLORES[nombre], linewidth=2, label=nombre)
    abajo.axhline(0, color=TINTA_2, linewidth=0.8)
    abajo.set_ylabel("Fuerza normal $C_N$")
    abajo.set_xlabel("Ángulo de ataque α (°)")
    abajo.legend(frameon=False, loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(carpeta / "cp_frente_alfa.png", dpi=200)


if __name__ == "__main__":
    comprobar()
    carpeta = Path(__file__).parent / "figuras"
    carpeta.mkdir(exist_ok=True)
    figura_mach(carpeta)
    figura_alfa(carpeta)
    for m in (0.3, 1.0, 1.25, 2.5):
        print(f"Mach {m:4}: CP = {x_cp(m):.3f} m, margen al despegue = "
              f"{(x_cp(m) - CG_DESPEGUE) / D:.2f} calibres")
    for a in (1, 5, 10, 15):
        print(f"α = {a:2}°: CP = {x_cp(0.3, np.radians(a)):.3f} m")
