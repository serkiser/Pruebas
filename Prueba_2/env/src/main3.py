from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
import json
import pandas as pd
from scipy.integrate import simpson
from scipy.signal import find_peaks, peak_widths
from scipy.stats import median_abs_deviation

# -------- CONFIGURACIÓN --------
fits_file = r"C:\Users\PC\Desktop\Ellie\Programación\Pruebas\Preubas\Prueba_2\env\src\med-58859-NT054013S012745S01_sp12-180.fits"

# Parámetros de procesamiento
REBIN_FACTOR = 4
SG_WINDOW = 61
SG_POLY = 2
MOVING_AVG_WINDOW = 35
DO_CONTINUUM_NORM = True

# Parámetros de análisis
SNR_WINDOW = 150
CONTINUUM_WINDOW = 701
CONTINUUM_PERCENTILE = 90
REDSHIFT_SIGMA_CLIP = 2.0  # Número de desviaciones estándar para filtrar outliers

# Líneas de interés para análisis (ampliada para mejor cálculo de redshift)
lines = {
    "Hβ": 4861.3,
    "[O III] 4959": 4958.91,    # Línea importante en nebulosas
    "[O III] 5007": 5006.84,    # Línea fuerte en regiones HII
    "[N II] 6548": 6548.05,     # Línea de nitrógeno (si el rango espectral lo permite)
    "[N II] 6583": 6583.45,     # Otra línea de nitrógeno
    "[S II] 6716": 6716.44,     # Línea de azufre
    "[S II] 6731": 6730.82      # Otra línea de azufre
}

# ---------- FUNCIONES DE UTILIDAD ----------
def valid_mask(flux, ivar):
    """Crea una máscara para valores válidos"""
    m = np.isfinite(flux) & np.isfinite(ivar) & (ivar > 0)
    return m

def rebin_spectrum(wl, flux, ivar, factor=2):
    """Rebinea el espectro para mejorar la relación señal/ruido"""
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
    """Intenta aplicar filtro Savitzky-Golay, falla a media móvil"""
    try:
        from scipy.signal import savgol_filter
        window = max(3, int(window) | 1)
        window = min(window, len(y) - (1 - (len(y)%2)))
        if window < poly + 2:
            window = poly + 3
        return savgol_filter(y, window_length=window, polyorder=poly, mode="interp")
    except Exception:
        w = max(3, int(MOVING_AVG_WINDOW))
        if w % 2 == 0:
            w += 1
        k = np.ones(w) / w
        y_pad = np.pad(y, (w//2, w//2), mode="edge")
        return np.convolve(y_pad, k, mode="valid")

def running_percentile(y, win=301, q=90):
    """Calcula un percentil móvil para estimar el continuo"""
    win = max(51, int(win) | 1)
    if win >= len(y):
        return np.full_like(y, np.nanmedian(y))
    half = win // 2
    cont = np.empty_like(y)
    for i in range(len(y)):
        a = max(0, i - half)
        b = min(len(y), i + half + 1)
        cont[i] = np.nanpercentile(y[a:b], q)
    return cont

def enhance_line_detection(flux, enhancement_factor=1.5):
    """
    Realza las líneas espectrales en espectros ruidosos
    aplicando una transformación no lineal al flujo.
    """
    # Normalizar el flujo
    norm_flux = (flux - np.min(flux)) / (np.max(flux) - np.min(flux))
    
    # Aplicar transformación no lineal para realzar características
    enhanced_flux = np.power(norm_flux, enhancement_factor)
    
    # Reescalar al rango original
    return enhanced_flux * (np.max(flux) - np.min(flux)) + np.min(flux)

def calculate_snr(flux, window=100):
    """Calcula la relación señal/ruido (SNR) del espectro"""
    n_segments = len(flux) // window
    snr_values = []
    
    for i in range(n_segments):
        segment = flux[i*window:(i+1)*window]
        signal = np.median(segment)
        noise = np.std(segment)
        if noise > 0:
            snr_values.append(signal / noise)
    
    return np.median(snr_values) if snr_values else 0

def measure_line_parameters(wavelengths, flux, line_center, window=10):
    """Mide parámetros importantes de una línea espectral"""
    mask = (wavelengths >= line_center - window) & (wavelengths <= line_center + window)
    wl_window = wavelengths[mask]
    flux_window = flux[mask]
    
    if len(flux_window) == 0:
        return None
    
    # Encontrar mínimo de flujo (máxima absorción)
    min_flux_idx = np.argmin(flux_window)
    observed_center = wl_window[min_flux_idx]
    min_flux = flux_window[min_flux_idx]
    
    # Calcular continuo local
    continuum_left = np.median(flux_window[:5])
    continuum_right = np.median(flux_window[-5:])
    continuum = (continuum_left + continuum_right) / 2
    
    # Calcular ancho equivalente
    equivalent_width = simpson(1 - flux_window/continuum, wl_window)
    
    # Calcular FWHM
    half_max = (continuum + min_flux) / 2
    left_idx = np.where(flux_window[:min_flux_idx] <= half_max)[0]
    right_idx = np.where(flux_window[min_flux_idx:] <= half_max)[0]
    
    if len(left_idx) > 0 and len(right_idx) > 0:
        left_wl = wl_window[left_idx[-1]]
        right_wl = wl_window[min_flux_idx + right_idx[0]]
        fwhm = right_wl - left_wl
    else:
        fwhm = np.nan
    
    # Calcular profundidad de la línea
    depth = 1 - (min_flux / continuum)
    
    return {
        'observed_center': observed_center,
        'equivalent_width': equivalent_width,
        'fwhm': fwhm,
        'depth': depth,
        'continuum_level': continuum
    }

def calculate_redshift(observed_wavelength, rest_wavelength):
    """Calcula el redshift a partir de una línea espectral"""
    return (observed_wavelength - rest_wavelength) / rest_wavelength

def robust_redshift_calculation(redshifts, sigma_clip=3.0):
    """Calcula un redshift robusto eliminando outliers"""
    if len(redshifts) == 0:
        return None, None, 0
    
    # Primera estimación usando mediana y MAD
    median_z = np.median(redshifts)
    mad_z = median_abs_deviation(redshifts)
    
    # Filtrar outliers
    filtered_redshifts = [z for z in redshifts if abs(z - median_z) < sigma_clip * mad_z]
    
    if len(filtered_redshifts) == 0:
        # Si todos son outliers, usar la mediana original
        return median_z, mad_z, len(redshifts)
    
    # Calcular media y desviación estándar de los valores filtrados
    mean_z = np.mean(filtered_redshifts)
    std_z = np.std(filtered_redshifts)
    
    return mean_z, std_z, len(filtered_redshifts)

def calculate_mg_fe_index(wavelengths, flux, mg_line=5175, fe_line=5270, window=20):
    """Calcula el índice Mg/Fe para estimar metalicidad"""
    mg_mask = (wavelengths >= mg_line - window) & (wavelengths <= mg_line + window)
    fe_mask = (wavelengths >= fe_line - window) & (wavelengths <= fe_line + window)
    
    mg_flux = np.mean(flux[mg_mask])
    fe_flux = np.mean(flux[fe_mask])
    
    return mg_flux / fe_flux

def estimate_temperature(hbeta_ew):
    """Estimación simple de temperatura a partir del ancho equivalente de Hβ"""
    if hbeta_ew < 2:
        return "Muy caliente (>10000 K)", 11000
    elif hbeta_ew < 4:
        return "Caliente (8000-10000 K)", 9000
    elif hbeta_ew < 6:
        return "Intermedia (6000-8000 K)", 7000
    else:
        return "Fría (<6000 K)", 5500

def find_emission_lines(wavelengths, flux, height_threshold=0.05, distance=5):  # Umbral más bajo
    """Encuentra líneas de emisión en el espectro"""
    # Normalizar el flujo para el detector de picos
    norm_flux = (flux - np.min(flux)) / (np.max(flux) - np.min(flux))
    
    # Encontrar picos (líneas de emisión)
    peaks, properties = find_peaks(norm_flux, height=height_threshold, distance=distance)
    
    # Calcular anchuras de los picos
    widths, width_heights, left_ips, right_ips = peak_widths(norm_flux, peaks, rel_height=0.5)
    
    # Convertir índices a longitudes de onda
    peak_wavelengths = wavelengths[peaks]
    fwhms = widths * (wavelengths[1] - wavelengths[0])  # Convertir a Å
    
    # Preparar resultados
    emission_lines = []
    for i, wl in enumerate(peak_wavelengths):
        emission_lines.append({
            'wavelength': wl,
            'strength': properties['peak_heights'][i],
            'fwhm': fwhms[i]
        })
    
    return emission_lines

def generate_spectral_report(wavelengths, flux, ivar, lines_dict):
    """Genera un reporte con los parámetros espectrales más importantes"""
    report = {}
    
    # Información básica del espectro
    report['wavelength_range'] = {
        'min': float(np.min(wavelengths)),
        'max': float(np.max(wavelengths)),
        'delta': float(np.max(wavelengths) - np.min(wavelengths))
    }
    
    # Calcular SNR
    report['snr'] = float(calculate_snr(flux))
    
    # Medir parámetros para cada línea de absorción
    report['absorption_lines'] = {}
    redshifts = []  # Lista para almacenar todos los redshifts calculados
    
    for name, rest_wl in lines_dict.items():
        measurement = measure_line_parameters(wavelengths, flux, rest_wl)
        if measurement:
            report['absorption_lines'][name] = measurement
            
            # Calcular redshift para esta línea
            z = calculate_redshift(measurement['observed_center'], rest_wl)
            measurement['redshift'] = z
            redshifts.append(z)
    
    # Calcular redshift robusto usando múltiples líneas
    if redshifts:
        mean_z, std_z, n_lines = robust_redshift_calculation(redshifts, sigma_clip=REDSHIFT_SIGMA_CLIP)
        
        report['redshift'] = {
            'value': float(mean_z),
            'error': float(std_z),
            'n_lines_used': n_lines,
            'n_lines_total': len(redshifts)
        }
        
        # Calcular velocidad radial
        report['radial_velocity'] = {
            'value': float(mean_z * 299792.458),  # km/s
            'error': float(std_z * 299792.458)
        }
    
    # Buscar líneas de emisión
    report['emission_lines'] = find_emission_lines(wavelengths, flux)
    
    # Calcular metalicidad aproximada
    report['mg_fe_ratio'] = float(calculate_mg_fe_index(wavelengths, flux))
    
    # Estimación de metalicidad basada en ratio Mg/Fe
    if report['mg_fe_ratio'] < 0.9:
        report['metallicity_estimate'] = "Baja metalicidad"
    elif report['mg_fe_ratio'] < 1.1:
        report['metallicity_estimate'] = "Metalicidad solar"
    else:
        report['metallicity_estimate'] = "Alta metalicidad"
    
    # Estimación de temperatura si se midió Hβ
    if 'Hβ' in report['absorption_lines']:
        hbeta_ew = report['absorption_lines']['Hβ']['equivalent_width']
        temp_est, temp_val = estimate_temperature(hbeta_ew)
        report['temperature_estimate'] = temp_est
        report['temperature_value'] = temp_val
    
    return report

def plot_spectrum_with_analysis(wavelengths, flux_original, flux_processed, lines_dict, report):
    """Crea una visualización completa del espectro con análisis"""
    fig = plt.figure(figsize=(15, 10))
    
    # Espectro principal
    plt.subplot(2, 1, 1)
    plt.plot(wavelengths, flux_original, linewidth=0.5, alpha=0.6, label="Original", color='lightgray')
    plt.plot(wavelengths, flux_processed, linewidth=1.0, label="Procesado", color='blue')
    
    # Añadir líneas y anotaciones
    y_max = np.nanmax(flux_processed) * 1.1
    for name, wavelength in lines_dict.items():
        if wavelengths.min() <= wavelength <= wavelengths.max():
            plt.axvline(wavelength, color="red", linestyle="--", alpha=0.7)
            measurement = report['absorption_lines'].get(name)
            if measurement:
                plt.text(wavelength+2, y_max*0.9, 
                        f"{name}\nEW={measurement['equivalent_width']:.2f}Å", 
                        rotation=90, color="red", fontsize=7)
    
    plt.xlabel("Longitud de onda (Å)")
    plt.ylabel("Flujo")
    
    # Título con información de redshift si está disponible
    title = f"Espectro LAMOST - SNR: {report['snr']:.1f}"
    if 'redshift' in report:
        title += f" - z: {report['redshift']['value']:.6f} ± {report['redshift']['error']:.6f}"
    plt.title(title)
    
    plt.legend()
    plt.grid(alpha=0.3)
    
    # Segundo subplot para zoom en regiones interesantes
    plt.subplot(2, 1, 2)
    zoom_region = (5100, 5200)  # Ajusta según tu espectro
    zoom_mask = (wavelengths >= zoom_region[0]) & (wavelengths <= zoom_region[1])
    plt.plot(wavelengths[zoom_mask], flux_processed[zoom_mask], linewidth=1.5, color='blue')
    
    # Resaltar líneas en la región de zoom
    for name, wavelength in lines_dict.items():
        if zoom_region[0] <= wavelength <= zoom_region[1]:
            plt.axvline(wavelength, color="red", linestyle="--", alpha=0.7)
            plt.text(wavelength+1, np.max(flux_processed[zoom_mask])*0.9, 
                    name, rotation=90, color="red", fontsize=8)
    
    plt.xlabel("Longitud de onda (Å)")
    plt.ylabel("Flujo")
    plt.title(f"Zoom región {zoom_region[0]}-{zoom_region[1]} Å")
    plt.grid(alpha=0.3)
    
    plt.tight_layout()
    return fig

# ---------- PROCESAMIENTO PRINCIPAL ----------
def main():
    # 1) Leer FITS
    try:
        with fits.open(fits_file) as hdul:
            # Intentar diferentes posibles nombres de extensión
            for ext_name in ["COADD_B", "COADD_R", "FLUX", 1]:
                if ext_name in hdul:
                    data = hdul[ext_name].data
                    break
            else:
                raise ValueError("No se encuentra extensión válida en el archivo FITS")
            
            # Intentar diferentes nombres de columnas
            if "WAVELENGTH" in data.columns.names:
                wl = np.array(data["WAVELENGTH"][0], dtype=float)
                flux = np.array(data["FLUX"][0], dtype=float)
                ivar = np.array(data["IVAR"][0], dtype=float)
            elif "lambda" in data.columns.names:
                wl = np.array(data["lambda"][0], dtype=float)
                flux = np.array(data["flux"][0], dtype=float)
                ivar = np.array(data["ivar"][0], dtype=float)
            else:
                # Si no encuentra las columnas esperadas, usar la primera fila
                wl = np.array(data[0][0], dtype=float)
                flux = np.array(data[0][1], dtype=float)
                ivar = np.array(data[0][2], dtype=float)
    except Exception as e:
        print(f"Error leyendo archivo FITS: {e}")
        return

    # 2) Máscara básica usando IVAR
    m = valid_mask(flux, ivar)
    wl, flux, ivar = wl[m], flux[m], ivar[m]

    # 3) Rebin para mejorar SNR
    wl_r, flux_r, ivar_r = rebin_spectrum(wl, flux, ivar, factor=REBIN_FACTOR)

    # 4) Suavizado
    flux_smooth = try_savgol(flux_r, window=SG_WINDOW, poly=SG_POLY)

    # 4.5) Realce de líneas para espectros con SNR bajo
    flux_enhanced = enhance_line_detection(flux_smooth, enhancement_factor=1.3)

    # 5) (opcional) normalización de continuo
    if DO_CONTINUUM_NORM:
        cont = running_percentile(flux_enhanced, win=CONTINUUM_WINDOW, q=CONTINUUM_PERCENTILE)
        cont = np.where(cont <= 0, np.nanmedian(cont[cont>0]), cont)
        flux_plot = flux_enhanced / cont
        ylab = "Flujo (normalizado)"
    else:
        flux_plot = flux_enhanced
        ylab = "Flujo"

    # 6) Generar reporte de análisis
    report = generate_spectral_report(wl_r, flux_plot, ivar_r, lines)
    
    # 7) Mostrar resultados importantes
    print("=== REPORTE DE ANÁLISIS ESPECTRAL ===")
    print(f"Rango de longitud de onda: {report['wavelength_range']['min']:.1f} - {report['wavelength_range']['max']:.1f} Å")
    print(f"SNR estimado: {report['snr']:.1f}")
    
    if 'redshift' in report:
        z_info = report['redshift']
        rv_info = report['radial_velocity']
        print(f"Redshift: {z_info['value']:.6f} ± {z_info['error']:.6f}")
        print(f"Velocidad radial: {rv_info['value']:.1f} ± {rv_info['error']:.1f} km/s")
        print(f"Líneas utilizadas: {z_info['n_lines_used']}/{z_info['n_lines_total']}")
    
    if 'temperature_estimate' in report:
        print(f"Temperatura estimada: {report['temperature_estimate']}")
    
    print(f"Ratio Mg/Fe: {report['mg_fe_ratio']:.3f}")
    print(f"Metalicidad estimada: {report['metallicity_estimate']}")
    
    print("\n=== LÍNEAS DE ABSORCIÓN DETECTADAS ===")
    for name, params in report['absorption_lines'].items():
        print(f"{name}: EW={params['equivalent_width']:.3f}Å, FWHM={params['fwhm']:.3f}Å, z={params.get('redshift', 'N/A'):.6f}")
    
    print("\n=== LÍNEAS DE EMISIÓN DETECTADAS ===")
    for i, line in enumerate(report['emission_lines']):
        print(f"Línea {i+1}: {line['wavelength']:.2f}Å, Fuerza: {line['strength']:.3f}")

    # 8) Guardar resultados
    with open('spectral_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    
    spectrum_df = pd.DataFrame({
        'wavelength': wl_r,
        'flux_original': flux_r,
        'flux_processed': flux_plot,
        'ivar': ivar_r
    })
    spectrum_df.to_csv('processed_spectrum.csv', index=False)
    
    # 9) Crear y guardar gráficos
    fig = plot_spectrum_with_analysis(wl_r, flux_r, flux_plot, lines, report)
    plt.savefig('detailed_spectral_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\nAnálisis completado. Resultados guardados en:")
    print("- spectral_analysis_report.json")
    print("- processed_spectrum.csv")
    print("- detailed_spectral_analysis.png")

if __name__ == "__main__":
    main()