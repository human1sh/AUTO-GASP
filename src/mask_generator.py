import os
import math
import subprocess
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.table import Table
from astropy.coordinates import Angle, SkyCoord
from astropy.wcs.utils import skycoord_to_pixel
from astropy.visualization import ZScaleInterval
from photutils.aperture import EllipticalAperture

def generate_sextractor_mask(ra, dec, work_dir, fold_name):
    """Runs SExtractor, masks target galaxy from segmentation map, and saves 3-panel diagnostic figures."""
    subprocess.run(['source-extractor', 'I_image.fits', 'I_image.fits', '-c', 'default.sex'], cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    cat_file = os.path.join(work_dir, 'sources.cat')
    tab = Table.read(cat_file, format='ascii.sextractor', names=['XW', 'YW', 'XI', 'YI', 'FK', 'KR', 'AI', 'BI', 'TI'])
    seg_file = os.path.join(work_dir, 'S1.SEG.fits')
    aper_file = os.path.join(work_dir, 'S3.APER.fits')
    X = SkyCoord(ra, dec, frame='icrs', unit='deg')
    with fits.open(seg_file) as hdul:
        seg_hdr = hdul[0].header
        seg_data = hdul[0].data.copy()
        cx, cy = skycoord_to_pixel(X, wcs=WCS(seg_hdr))
        dist = [(row, math.sqrt((cx - row['XI'])**2 + (cy - row['YI'])**2)) for row in tab]
        reg, _ = min(dist, key=lambda x: x[1])
        apr = EllipticalAperture((reg['XI'], reg['YI']), reg['KR'] * reg['AI'], reg['KR'] * reg['BI'], Angle(reg['TI'], 'deg'))
        idd = seg_data[int(reg['YI']), int(reg['XI'])]
        seg_data[seg_data == idd] = 0
        segm_file = os.path.join(work_dir, 'S2.SEGM.fits')
        fits.PrimaryHDU(seg_data).writeto(segm_file, overwrite=True)
        reg_tab = Table(rows=[reg], names=['XW', 'YW', 'XI', 'YI', 'FK', 'KR', 'AI', 'BI', 'TI'])
        reg_tab.write(os.path.join(work_dir, 'gal-prop.fits'), overwrite=True)

    # Plot Segmentation Diagnostics
    with fits.open(seg_file) as SEG, fits.open(aper_file) as APR, fits.open(segm_file) as SEGM:
        images = [SEG[0].data, APR[0].data, SEGM[0].data]
        titles = ['SEG Image', 'APER Image', 'SEGM Image']
        fig, ax = plt.subplots(1, 3, figsize=(17, 5))
        for i, (img, tit) in enumerate(zip(images, titles)):
            d1, d2 = ZScaleInterval().get_limits(img)
            im = ax[i].imshow(img, cmap='gray', origin='lower', vmin=d1, vmax=d2)
            if i == 0:
                apr.plot(color='green', lw=2.0, ax=ax[i])
            ax[i].set_title(tit)
            ax[i].set_xlabel('X-axis [pix]')
            ax[i].set_ylabel('Y-axis [pix]')
            fig.colorbar(im, ax=ax[i], shrink=0.8)
        fig.tight_layout()
        fig.suptitle(f'Segmentation image - {fold_name}', y=1.05)
        fig.savefig(os.path.join(work_dir, '1.SExtractor-segmentation.png'), format='png', bbox_inches='tight')
        plt.close(fig)

    print("[1/3] SExtractor Segmentation Mask : Generated")