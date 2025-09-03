from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

# -------- CONFIG --------
fits_file = r"C:\Users\PC\Desktop\Ellie\Programación\Pruebas\Preubas\Prueba_2\env\src\med-58859-NT054013S012745S01_sp12-180.fits"
REBIN_FACTOR = 2
SG_WINDOW = 101
SG_POLY = 3
DO_CONTINUUM_NORM = False
# ------------------------

# Diccionario de líneas de interés
lines_blue = {
    "O III": 4959,
    "O III": 5007,
    "Mg I": 5175
}
lines_red = {
    "O I": 6300,
    "O I": 6363,
    "N II": 6548,
    "Hα": 6563,
    "N II": 6583,
    "S II": 6716,
    "S II": 6731
}

# -------- utilidades --------
def valid_mask(flux, ivar):
    return np.isfinite(flux) & np.isfinite(ivar) & (ivar > 0)

def rebin_spectrum(wl, flux, ivar, factor=2):
    if factor <= 1:
        return wl, flux, ivar
    n = len(wl) // factor
    wl_r = wl[:n*factor].reshape(n, factor).mean(axis=1)
    var = 1.0 / ivar
    var_r = var[:n*factor].reshape(n, factor).mean(axis=1)
    flux_r = flux[:n*factor].reshape(n, factor).mean(axis=1)
    ivar_r = 1.0 / var_r
    return wl_r, flux_r, ivar_r

def try_savgol(y, window, poly):
    try:
        from scipy.signal import savgol_filter
        window = max(3, int(window) | 1)
        return savgol_filter(y, window_length=window, polyorder=poly, mode="interp")
    except Exception:
        return y  # fallback: no suavizado
# --------------------------------

def process_extension(hdul, extname):
    data = hdul[extname].data
    wl   = np.array(data["WAVELENGTH"][0], dtype=float)
    flux = np.array(data["FLUX"][0], dtype=float)
    ivar = np.array(data["IVAR"][0], dtype=float)
    m = valid_mask(flux, ivar)
    wl, flux, ivar = wl[m], flux[m], ivar[m]
    wl_r, flux_r, ivar_r = rebin_spectrum(wl, flux, ivar, factor=REBIN_FACTOR)
    flux_smooth = try_savgol(flux_r, window=SG_WINDOW, poly=SG_POLY)
    return wl_r, flux_r, flux_smooth

# -------- leer FITS --------
with fits.open(fits_file) as hdul:
    wl_b, flux_b, flux_b_s = process_extension(hdul, "COADD_B")
    wl_r, flux_r, flux_r_s = process_extension(hdul, "COADD_R")

# -------- graficar --------
fig, axs = plt.subplots(2, 1, figsize=(12,8), sharey=False)

# --- Azul ---
axs[0].plot(wl_b, flux_b, linewidth=0.5, alpha=0.6, label="Rebin")
axs[0].plot(wl_b, flux_b_s, linewidth=1.0, label="Suavizado")
for name, wavelength in lines_blue.items():
    axs[0].axvline(wavelength, color="red", linestyle="--", alpha=0.7)
    axs[0].text(wavelength+2, np.nanmax(flux_b_s)*0.8, name,
                rotation=90, color="red", fontsize=8)
axs[0].set_title("COADD_B (Azul)")
axs[0].set_xlabel("Longitud de onda (Å)")
axs[0].set_ylabel("Flujo")
axs[0].legend()
axs[0].grid(alpha=0.3)

# --- Rojo ---
axs[1].plot(wl_r, flux_r, linewidth=0.5, alpha=0.6, label="Rebin")
axs[1].plot(wl_r, flux_r_s, linewidth=1.0, label="Suavizado")
for name, wavelength in lines_red.items():
    axs[1].axvline(wavelength, color="red", linestyle="--", alpha=0.7)
    axs[1].text(wavelength+2, np.nanmax(flux_r_s)*0.8, name,
                rotation=90, color="red", fontsize=8)
axs[1].set_title("COADD_R (Rojo)")
axs[1].set_xlabel("Longitud de onda (Å)")
axs[1].set_ylabel("Flujo")
axs[1].legend()
axs[1].grid(alpha=0.3)

plt.tight_layout()
plt.show()
