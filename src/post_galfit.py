import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from scipy.special import gamma
from astropy.visualization import ZScaleInterval

def get_lum(n, re, mue, ar):
    """Calculates total integrated luminosity from Sersic profile parameters."""
    kapp = 2 * n - 1 / 3
    norm = (2 * np.pi * re**2 * mue * ar)
    gamm = np.exp(kapp) * n * kapp**(-2 * n) * gamma(2 * n)
    Ftot = norm * gamm
    mag = -2.50 * np.log10(Ftot) + 22.5
    lum = 10**(-0.4 * mag)
    return lum

def get_param(header, key):
    """Parses numeric floating-point values from GALFIT header parameters."""
    return float(header[key].split('+/-')[0].replace('*', '').replace('[', '').replace(']', '').strip())

def process_galfit_1c_output(work_dir, fold_name, pixel_scale=0.396):
    """Plots 2D 1C image block residuals and logs fitted parameters into galfit_params.txt."""
    param_txt_path = os.path.join(work_dir, "galfit_params.txt")
    imgb_path      = os.path.join(work_dir, "imgblock.fits")
    gal_prop_file  = os.path.join(work_dir, 'gal-prop.fits')
    gal            = Table.read(gal_prop_file)
    with fits.open(imgb_path) as IMGB:
        hed = IMGB[2].header
        
        # Parse comparison parameters (e.g. Meert)
        m_re    = float(f"{gal['r_bulge_MR'][0]:.4g}") if 'r_bulge_MR' in gal.colnames else 1.0
        m_n     = float(f"{gal['n_bulge_MR'][0]:.4g}") if 'n_bulge_MR' in gal.colnames else 1.0

        # Extract 1C GALFIT parameters
        s_me1   = get_param(hed, "1_MU_E")
        s_re1   = get_param(hed, "1_RE")
        s_n1    = get_param(hed, "1_N")
        s_ar1   = get_param(hed, "1_AR")
        s_cn1   = hed['CHI2NU']
        lum1    = get_lum(s_n1, s_re1, s_me1, s_ar1)
        lumf1   = 1.0
        co1_str = f"Self 1C : Reff_pix = {s_re1:.4g}, Reff_arc = {s_re1*pixel_scale:.4g}, n = {s_n1:.4g}, f = {lumf1:.4g}"
        images  = [IMGB[1].data, IMGB[2].data, IMGB[3].data]
        titles  = ['MAIN Image', 'MODEL Image', 'RESIDUAL Image']
        fig, ax = plt.subplots(1, 3, figsize=(17, 5))
        for i, (img, tit) in enumerate(zip(images, titles)):
            d1, d2 = ZScaleInterval().get_limits(img)
            ax[i].set_title(tit)
            ax[i].imshow(img, cmap='gray', origin='lower', vmin=d1, vmax=d2)
            ax[i].set_xlabel('X-axis [pix]')
            ax[i].set_ylabel('Y-axis [pix]')
        fig.tight_layout()
        fig.suptitle(f'GALFIT 1C results for galfit.01 - {fold_name} with CHI2NU = {s_cn1}', y=1.19)
        fig.text(0.5, 1.00, f'{co1_str}', ha='center', fontsize=16, color='black')
        fig.savefig(os.path.join(work_dir, '2.Galfit-decomposition-1C.png'), format='png', bbox_inches='tight')
        print("[3/3] Post-GALFIT 1C Figure and Parameter Logs : Generated")
        plt.close()
        param = ('1C', float(m_re), float(m_n), float(s_cn1), float(lumf1), float(s_me1), float(s_re1)*pixel_scale, float(s_n1))
        with open(param_txt_path, "w") as f:
            f.write("{}\n".format(param))