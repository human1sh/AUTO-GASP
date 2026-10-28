import os
import re
import argparse
from src.config import setup_matplotlib, prepare_work_directory
from src.mask_generator import generate_sextractor_mask
from src.galfit_runner import run_galfit_single_sersic
from src.post_galfit import process_galfit_1c_output

# Fixed pixel scale constant (SDSS = 0.396 "/pix)
PIXEL_SCALE = 0.396

def process_target(ra, dec, home_dir):
    """Processes a single target galaxy folder given its RA and Dec."""
    ra_str     = "{:.3f}".format(ra)
    dec_str    = "{:.3f}".format(dec)
    fold_name  = f"RD={ra_str},{dec_str}"
    config_dir = os.path.join(home_dir, "config")
    work_dir   = os.path.join(home_dir, 'data', fold_name)
    if not os.path.exists(work_dir):
        print(f"[-] Directory does not exist: {work_dir}. Skipping.")
        return
    prepare_work_directory(work_dir, config_dir)
    print(f"\n==================== {fold_name} : Processing ====================")
    # 1. Pre-GALFIT SExtractor Masking
    print("[1/3] SExtractor Segmentation Mask : Generating")
    generate_sextractor_mask(ra, dec, work_dir, fold_name)
    # 2. GALFIT 1-Component Execution (Uncomment when ready)
    print("[2/3] GALFIT 1C Fit : Initialising")
    run_galfit_single_sersic(work_dir)
    # 3. Post-GALFIT Parameter Extraction & Figure Generation (Uncomment when ready)
    print("[3/3] Post-GALFIT 1C Figure and Parameter Logs : Generating")
    process_galfit_1c_output(work_dir, fold_name, pixel_scale=PIXEL_SCALE)
    print(f"==================== {fold_name} : Processed ====================")

def main():
    parser = argparse.ArgumentParser(description="Automated 1-Component Sersic GALFIT & SExtractor Pipeline.")
    parser.add_argument("--ra", type=float, help="Right Ascension (deg)")
    parser.add_argument("--dec", type=float, help="Declination (deg)")
    parser.add_argument("--id", type=int, default=0, help="Row index in catalog file")
    parser.add_argument("--home_dir", type=str, default=os.getcwd(), help="Root directory containing configuration and sample data")
    parser.add_argument("--batch", action="store_true", help="Process all RD=RA,Dec directories inside /data/")
    args = parser.parse_args()
    setup_matplotlib()
    analysis_dir = os.path.join(args.home_dir, "data")
    if args.batch:
        if not os.path.exists(analysis_dir):
            raise FileNotFoundError(f"[-] Directory '{analysis_dir}' does not exist.")

        # Scan for all folders matching RD=<RA>,<DEC>
        rd_folders = [f for f in os.listdir(analysis_dir) if f.startswith("RD=")]
        print(f"[+] Found {len(rd_folders)} target directories in {analysis_dir}")
        for i, fold in enumerate(sorted(rd_folders)):
            match = re.search(r"RD=([0-9.]+),([0-9.-]+)", fold)
            if match:
                ra_val = float(match.group(1))
                dec_val = float(match.group(2))
                process_target(ra_val, dec_val, args.home_dir)
            else:
                print(f"[-] Skipping unrecognized folder format: {fold}")
    elif args.ra is not None and args.dec is not None:
        process_target(args.ra, args.dec, args.home_dir)
    else:
        print("[-] Please specify target coordinates (--ra and --dec) or pass --batch to process all folders.")

if __name__ == "__main__":
    main()