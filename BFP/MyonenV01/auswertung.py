# Header
import numpy as np
import matplotlib.pyplot as plt
import uncertainties.unumpy as unp
from uncertainties import ufloat
from scipy.optimize import curve_fit
# from scipy.stats import stats
# import scipy.constants as const
# import scipy.integrate as integrate
plt.rcParams['figure.figsize'] = (10, 8)
plt.rcParams['font.size'] = 18

# Daten einlesen
dt, N = np.genfromtxt('verz.txt', unpack=True)
daten = np.genfromtxt('Daten/Daten.Spe', unpack=True)
kal1 = np.genfromtxt("Daten/Kal_1_micro_second.Spe", unpack=True)
kal01 = np.genfromtxt("Daten/Kal_01_micro_second.Spe", unpack=True)
dt = dt - 20    # Zentrieren
N *= 10
N -= 130
hoehe = np.mean(N[4:16])
print()
print()
print("Halbwertsbreite: ", 29)


plt.figure(1)
plt.ylabel(r"$N(t) \, / \, (10\mathrm{s})^{-1}$")
plt.xlabel(r"$\mathrm{d}t \, / \, \mathrm{ns}$")
plt.errorbar(dt, N, yerr=np.sqrt(N), fmt='kx', label="Messwerte")
# plt.plot(dt, N, 'r.', label="Messwerte")
plt.axhline(y=hoehe, xmin=0.15, xmax=0.75, label="Plateau")
plt.axhline(y=hoehe/2, xmin=0.07, xmax=0.85, color="red",
            label="Halbwertsbreite")
plt.ylim(0, 130)
plt.grid()
plt.legend(loc="best")
plt.tight_layout()
plt.savefig("Plateau.pdf")
plt.clf()

#  Kanalauswertung
kal_t, kanal = np.genfromtxt("Daten/Kalibrierung_1.txt", unpack=True)


def linear(x, m, b):
    return m*x + b


params_kal, cov_kal = curve_fit(linear, kanal, kal_t)
errors_kal = np.sqrt(np.diag(cov_kal))
m = ufloat(params_kal[0], errors_kal[0])
b = ufloat(params_kal[1], errors_kal[1])
print("Steigung: ", m)
print("y-Achsenabschnitt: ", b)


# Plot dazu
x = np.linspace(0, 200)
plt.plot(kanal, kal_t, 'rx', label="Daten")
plt.plot(x, linear(x, *params_kal), 'b--', label="Regression")
plt.xlabel("Kanal")
plt.ylabel(r"$T_{VZ} \, / \, \mathrm{\mu s}$")
plt.xlim(0, 200)
plt.tight_layout()
plt.legend(loc="best")
plt.savefig("kal.pdf")
plt.clf()
print("Alles ohne Probleme ausgeführt!")

# Bestimmung Untergrundrate
messdauer = 147182  # Sekunden
Startimpulse = 3061879
Startimpulse = ufloat(Startimpulse, np.sqrt(Startimpulse))
n = Startimpulse/messdauer
Ts = 20*10**(-6)    # Sekunden
Nf = Startimpulse*n*Ts*unp.exp(-n*Ts)
Nf_kanal = Nf/len(daten)
print("-------------------")
print(Startimpulse)
print("Fehlmessungen: ", Nf)
print("Untergrundrate: ", Nf_kanal)

# Umrechnung Kanäle in Zeit
kanaele = np.arange(0, 512, 1)
zeiten1 = linear(kanaele, *params_kal)
# Rausnehmen von komischen Werten
zeiten = zeiten1[3:6]
zeiten = np.append(zeiten, zeiten1[7:14])
zeiten = np.append(zeiten, zeiten1[15:])
daten_ang = daten[3:6]
daten_ang = np.append(daten_ang, daten[7:14])
daten_ang = np.append(daten_ang, daten[15:])

# Entfernte Daten und Zeiten
zeiten_ent = zeiten1[:3]
zeiten_ent = np.append(zeiten_ent, zeiten1[6])
zeiten_ent = np.append(zeiten_ent, zeiten1[14])
daten_ent = daten[:3]
daten_ent = np.append(daten_ent, daten[6])
daten_ent = np.append(daten_ent, daten[14])
# Definition der exp-Funktion


def e(x, N_0, l, U):
    return N_0*np.exp(-l*x) + U


params_fit, cov_fit = curve_fit(e, zeiten, daten_ang)
errors_fit = np.sqrt(np.diag(cov_fit))
N_0 = ufloat(params_fit[0], errors_fit[0])
l = ufloat(params_fit[1], errors_fit[1])
U = ufloat(params_fit[2], errors_fit[2])

print("-------------------")
print("N_0: ", N_0)
print("Lambda: ", l)
print("Lebensdauer: ", 1/l)
print("Untergrundrate: ", U)
tau = 2.2
ta_fit = 1/l
print("Verhältnis: ", (1-ta_fit/tau)*100)
print("Verhältnis Untergrund: ", (1-U/Nf_kanal)*100)

plt.plot(zeiten, daten_ang, 'r.', label="Daten")
plt.plot(zeiten_ent, daten_ent, 'gx', label="Nicht-betrachtete Daten")
plt.plot(zeiten, e(zeiten, *params_fit), 'b--', label="Fit")
plt.xlabel(r"$\tau \,  / \, \mathrm{\mu s}$")
plt.ylabel(r"$N(t)$")
plt.grid()
plt.legend(loc="best")
plt.tight_layout()
plt.savefig('fit.pdf')
plt.clf()

# Tabellen
np.savetxt('Tabellen/tvz.txt', np.column_stack([dt, N]),
           delimiter=' & ', newline=r' \\'+'\n', fmt="%.0f")
np.savetxt('Tabellen/kal.txt', np.column_stack([kal_t, kanal]),
           delimiter=' & ', newline=r' \\'+'\n', fmt="%.0f")
np.savetxt('Tabellen/fit.txt', np.column_stack([kanaele, zeiten1, daten]),
           delimiter=' & ', newline=r' \\'+'\n', fmt="%.0f")
