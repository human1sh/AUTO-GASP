# AUTO-GASP

**Automated 1-Component Sérsic GALFIT & SExtractor Processing Pipeline**

AUTO-GASP is an automated Python pipeline designed for multi-wavelength astronomical galaxy decomposition and Sérsic profile fitting. It integrates **SExtractor** for automated source detection and segmentation masking with **GALFIT** for single-component (1C) Sérsic profile parameter extraction, diagnostic plotting, and parameter logging.  

### Motivation & Background
I originally built this pipeline in mid-2024 to automate the tedious and repetitive process of manually configuring masking parameters and initial guesses when analyzing large samples of galaxies. Having worked extensively with multi-component photometric decomposition of elliptical galaxies across optical Sloan Digital Sky Survey (SDSS) and Dark Energy Camera Legacy Survey (DECaLS) datasets, I wanted a hands-off, robust tool that could handle everything from target masking to post-fit residual diagnostics without sacrificing scientific accuracy.

---

## Table of Contents
- [AUTO-GASP](#auto-gasp)
    - [Motivation \& Background](#motivation--background)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Repository Structure and input file requirements](#repository-structure-and-input-file-requirements)
  - [System \& Software Prerequisites](#system--software-prerequisites)
    - [1. Astronomical Binary Dependencies](#1-astronomical-binary-dependencies)
    - [2. Python Environment](#2-python-environment)
  - [Pipeline Architecture](#pipeline-architecture)
    - [1. Environment \& Config Preparation (`src/config.py`)](#1-environment--config-preparation-srcconfigpy)
    - [2. SExtractor Segmentation \& Masking (`src/mask_generator.py`)](#2-sextractor-segmentation--masking-srcmask_generatorpy)
    - [3. GALFIT 1-Component Execution (`src/galfit_runner.py`)](#3-galfit-1-component-execution-srcgalfit_runnerpy)
    - [4. Post-GALFIT Parameter Extraction \& Visuals (`src/post_galfit.py`)](#4-post-galfit-parameter-extraction--visuals-srcpost_galfitpy)
  - [Installation \& Setup](#installation--setup)
  - [Usage Guide](#usage-guide)
    - [Single Target Execution](#single-target-execution)
    - [Batch Execution](#batch-execution)
    - [Command-Line Options](#command-line-options)
  - [Output Files \& Outputs Explanation](#output-files--outputs-explanation)

---

## Features

- **Automated Masking**: Runs SExtractor on target images (`I_image.fits`), identifies the target via WCS coordinates (`SkyCoord`), and produces primary galaxy segmentation masks (`S1.SEG.fits`, `S2.SEGM.fits`).
- **Dynamic Parameter Injection**: Automatically updates the `galfit.feedme` configuration file with sky centroids ($X, Y$), axis ratio ($b/a$), and position angle ($PA$).
- **Double-Pass GALFIT Execution**: Invokes GALFIT both for standard parameter estimation and for output block extraction (`-o3`).
- **Diagnostic Visualizations**:
  - 3-panel SExtractor diagnostic maps (`SEG Image`, `APER Image`, `SEGM Image`).
  - 3-panel GALFIT decomposition maps (`MAIN Image`, `MODEL Image`, `RESIDUAL Image`).
- **Data Extraction**: Log parameters ($n$, $R_e$, $\mu_e$, $\chi_\nu^2$, total flux/luminosity) directly to standard ASCII outputs (`galfit_params.txt`).

---

## Repository Structure and input file requirements
For the pipeline to process target data correctly, all input subdirectories inside data/ must follow the RD={RA},{DEC} naming convention (where coordinates match the cutout center). Each folder must contain three input FITS files with these exact filenames:

```text
AUTO-GASP/
├── main.py                     # Pipeline CLI entry point & driver
├── README.md                   # Repository documentation
├── config/                     # Template configuration directory
│   ├── default.sex             # SExtractor main configuration settings
│   ├── default.conv            # SExtractor convolution filter matrix
│   ├── default.nnw             # SExtractor neural network star/galaxy weights
│   ├── Custom.param            # SExtractor output catalog column specs
│   ├── galfit.feedme           # GALFIT template feedme file
│   └── gal.constraints         # GALFIT parameter constraint limits
├── src/                        # Core Python source modules
│   ├── __init__.py
│   ├── config.py               # Plotting styles & target directory initialization
│   ├── mask_generator.py       # SExtractor execution & WCS masking logic
│   ├── galfit_runner.py        # GALFIT execution wrapper & parameter updater
│   └── post_galfit.py          # Output image block parser & parameter log generator
└── data/                       # Working target directories (Format: RD=<RA>,<DEC>)
    └── RD={RA},{DEC}/
        ├── I_image.fits        # Science frame containing the primary galaxy target 
        ├── I_weight.fits       # Inverse-variance weight (or variance/error) map
        ├── I_psf.fits          # Point Spread Function (PSF) model image
        └── gal-prop.fits       # Pre-extracted target catalog property FITS table
```
---

## System & Software Prerequisites

### 1. Astronomical Binary Dependencies
Ensure the following tools are installed and available in your shell environment:
- **GALFIT** (v3.0.7d or later)
- **SExtractor** / **Source-Extractor** (`source-extractor` or `sex`)
- **CFITSIO** shared libraries

### 2. Python Environment
Python **3.8+** is recommended. The pipeline relies on the following core scientific packages:

| Library | Minimal Recommended Version | Purpose |
| :--- | :--- | :--- |
| `numpy` | `1.21.0` | Numerical calculations & array operations |
| `matplotlib` | `3.4.0` | 2D image block & diagnostic plot generation |
| `astropy` | `5.0.0` | FITS I/O, WCS transformation, SkyCoord, Table parsing |
| `photutils` | `1.3.0` | Elliptical aperture creation & plotting |
| `scipy` | `1.7.0` | Gamma function calculations (`scipy.special.gamma`) |

Install dependencies using `pip`:

```bash
pip install numpy matplotlib astropy photutils scipy
```

---

## Pipeline Architecture

### 1. Environment & Config Preparation (`src/config.py`)
- Sets global publication-quality Matplotlib rendering properties (ticks, fonts, figure dimensions).
- Copies mandatory setup template files (`default.sex`, `default.conv`, `default.nnw`, `Custom.param`, `galfit.feedme`, `gal.constraints`) from `config/` directly into the active target directory inside `data/`.

### 2. SExtractor Segmentation & Masking (`src/mask_generator.py`)
- Executes SExtractor on `I_image.fits`.
- Parses output catalog `sources.cat`.
- Projects RA and Dec onto pixel coordinates using the image WCS (`skycoord_to_pixel`).
- Identifies the target galaxy, generates an elliptical aperture overlay, isolates the target source from the segmentation map, and writes `S2.SEGM.fits`.
- Saves a 3-panel plot: `1.SExtractor-segmentation.png`.

### 3. GALFIT 1-Component Execution (`src/galfit_runner.py`)
- Reads target physical parameters ($X, Y$ centroids, $b/a$ axis ratio, position angle $PA$) from `gal-prop.fits`.
- Modifies `galfit.feedme` in place with target values.
- Configures required `PATH` and `LD_LIBRARY_PATH` environment variables for GALFIT binaries.
- Executes `galfit galfit.feedme` followed by `galfit -o3 galfit.01` to generate image block fits.

### 4. Post-GALFIT Parameter Extraction & Visuals (`src/post_galfit.py`)
- Parses fitted Sérsic output parameters ($R_e$, $n$, $\mu_e$, $\chi_\nu^2$) from output headers.
- Converts pixel units into physical sky scale using pixel scale constant ($\text{SDSS} = 0.396^{\prime\prime}/\text{pix}$).
- Generates 3-panel image decomposition plot (`MAIN`, `MODEL`, `RESIDUAL`) saved as `2.Galfit-decomposition-1C.png`.
- Logs numeric parameter tuples into `galfit_params.txt`.

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/AUTO-GASP.git
   cd AUTO-GASP
   ```

2. **Verify executable paths:**
   Check path variables in `src/galfit_runner.py` to match your local installation directory for GALFIT and CFITSIO binaries:
   ```python
   galfit_dir = "/path/to/galfit3.0.7d"
   cfitsio_dir = "/path/to/cfitsio"
   ```

---

## Usage Guide

### Single Target Execution
To run the pipeline on a single galaxy target folder (e.g., `data/RD=189.231,12.315`):

```bash
python main.py --ra 189.231 --dec 12.315
```

### Batch Execution
To process all target directories following the `RD=<RA>,<DEC>` naming convention inside `data/`:

```bash
python main.py --batch
```

### Command-Line Options

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--ra` | `float` | `None` | Target Right Ascension in decimal degrees (e.g., `189.231`) |
| `--dec` | `float` | `None` | Target Declination in decimal degrees (e.g., `12.315`) |
| `--id` | `int` | `0` | Target index row ID |
| `--home_dir` | `str` | `os.getcwd()` | Root directory path containing `config/` and `data/` |
| `--batch` | `flag` | `False` | Batch process all `RD=*` folders inside `data/` |

---

## Output Files & Outputs Explanation

Upon successful completion, each target folder (`data/RD=<RA>,<DEC>/`) will contain:

| File Name | Description |
| :--- | :--- |
| `sources.cat` | ASCII catalog produced by SExtractor |
| `S1.SEG.fits` | Original raw SExtractor segmentation map |
| `S2.SEGM.fits` | Cleaned target-removed background segmentation mask |
| `S3.APER.fits` | SExtractor aperture overlay FITS map |
| `gal-prop.fits` | Target galaxy spatial property FITS table |
| `1.SExtractor-segmentation.png` | 3-panel plot: `SEG`, `APER`, and `SEGM` images |
| `galfit.01` | GALFIT fitted parameter log file |
| `imgblock.fits` | 3D FITS block containing Original, Model, and Residual images |
| `2.Galfit-decomposition-1C.png` | 3-panel plot: `MAIN`, `MODEL`, and `RESIDUAL` fit maps |
| `galfit_params.txt` | Extracted numerical Sérsic parameters tuple |