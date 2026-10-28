import os
import subprocess
import numpy as np
from astropy.table import Table

def run_galfit_single_sersic(work_dir):
    """Executes single 1-Component Sersic GALFIT fit."""
    
    # Remove old galfit logs and output image blocks
    for f in os.listdir(work_dir):
        if f.endswith(".log") or f.endswith("block.fits"):
            os.remove(os.path.join(work_dir, f))
    i_file = 'galfit.feedme'
    o_file = 'galfit.01'   
    prop_file = os.path.join(work_dir, 'gal-prop.fits')
    t = Table.read(prop_file)
    input_path  = os.path.join(work_dir, i_file)
    output_path = os.path.join(work_dir, o_file)
    with open(input_path, 'r+') as file:
        lines = file.readlines()
        # Set 1-Component Sersic centroid, axis ratio (b/a), and position angle (PA)
        lines[33:34] = [f' 1) {t["XI"][0]}  {t["YI"][0]} 1 1  # position x, y\n']
        lines[40:41] = [f' 9) {np.round(t["BI"][0] / t["AI"][0], 4)}      1          # axis ratio (b/a)\n']
        lines[41:42] = [f' 10) {t["TI"][0]}       1          # position angle (PA) [deg: Up=0, Left=90]\n']
        file.seek(0)
        file.writelines(lines)
        file.truncate()

    # Build environment dict with PATH and LD_LIBRARY_PATH
    env         = os.environ.copy()
    galfit_dir  = "/home/maverick/galfit3.0.7d"
    cfitsio_dir = "/home/maverick/galfit3.0.7d/cfitsio"    
    env["PATH"]            = f"{galfit_dir}:{env.get('PATH', '')}"
    env["LD_LIBRARY_PATH"] = f"{cfitsio_dir}:{env.get('LD_LIBRARY_PATH', '')}"
    subprocess.run(['galfit',        i_file], cwd=work_dir, env=env, capture_output=True, text=True, check=True)
    subprocess.run(['galfit', '-o3', o_file], cwd=work_dir, env=env, capture_output=True, text=True, check=True)
    if os.path.isfile(output_path):
        print("[2/3] GALFIT 1C Fit : Successful")
        return 'DONE'
    else:
        print("[2/3] GALFIT 1C Fit : Unsccessful")
        return 'NOT DONE'