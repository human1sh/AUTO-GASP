import os
import shutil
import warnings
import matplotlib as mpl

warnings.filterwarnings("ignore")

def setup_matplotlib():
    """Configures global Matplotlib plotting defaults[cite: 1, 5]."""
    mpl.rcParams['font.size'] = 16
    mpl.rcParams["figure.figsize"] = (11, 7)
    mpl.rcParams['savefig.dpi'] = 600
    mpl.rcParams["legend.fontsize"] = 16
    mpl.rcParams["legend.title_fontsize"] = 16
    mpl.rcParams["axes.grid"] = False
    mpl.rcParams["grid.color"] = 'black'
    mpl.rcParams['grid.linestyle'] = 'dotted'
    mpl.rcParams['grid.linewidth'] = 0.2
    mpl.rcParams["xtick.minor.visible"] = True
    mpl.rcParams['xtick.minor.width'] = 1.0
    mpl.rcParams['xtick.major.width'] = 1.0
    mpl.rcParams['xtick.direction'] = 'in'
    mpl.rcParams['xtick.minor.size'] = 2
    mpl.rcParams['xtick.major.size'] = 6
    mpl.rcParams['xtick.top'] = True
    mpl.rcParams["ytick.minor.visible"] = True
    mpl.rcParams['ytick.minor.width'] = 1.0
    mpl.rcParams['ytick.major.width'] = 1.0
    mpl.rcParams['ytick.direction'] = 'in'
    mpl.rcParams['ytick.minor.size'] = 2
    mpl.rcParams['ytick.major.size'] = 6
    mpl.rcParams['ytick.right'] = True

def prepare_work_directory(target_dir, config_dir):
    """Copies required template files into the target folder[cite: 1, 2]."""
    required_files = ['default.sex', 'default.conv', 'default.nnw', 'Custom.param', 'galfit.feedme', 'gal.constraints']
    for f in required_files:
        src_path = os.path.join(config_dir, f)
        if os.path.exists(src_path):
            shutil.copy2(src_path, os.path.join(target_dir, f))
        else:
            raise FileNotFoundError(f"Missing configuration file: '{src_path}'")