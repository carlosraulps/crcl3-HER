#!/usr/bin/env python3
"""
================================================================================
 PACK CALCULATIONS FOR CLUSTER DEPLOYMENT (Pure Python stdlib)
================================================================================
 Packs the staged CrCl3 2x2 H adsorption calculation directories into
 compressed archives (.tar.gz and .zip) using Python's built-in modules.
 No external zip/tar CLI binaries required.
================================================================================
"""

import os
import sys
import tarfile
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TAR_NAME = "crcl3_2x2_h_ads_without_U.tar.gz"
ZIP_NAME = "crcl3_2x2_h_ads_without_U.zip"

INCLUDE_DIRS = ["no_vdw", "yes_vdw"]
INCLUDE_FILES = [
    "setup_h_ads.py",
    "verify_supercell.py",
    "calculate_h_adsorption_physics.py",
    "pack_calculations.py"
]

def make_tar():
    tar_path = os.path.join(SCRIPT_DIR, TAR_NAME)
    print("Creating tar.gz archive: {}...".format(TAR_NAME))
    with tarfile.open(tar_path, "w:gz") as tar:
        for d in INCLUDE_DIRS:
            dp = os.path.join(SCRIPT_DIR, d)
            if os.path.exists(dp):
                tar.add(dp, arcname=d)
        for f in INCLUDE_FILES:
            fp = os.path.join(SCRIPT_DIR, f)
            if os.path.exists(fp):
                tar.add(fp, arcname=f)
    sz = os.path.getsize(tar_path) / (1024 * 1024)
    print("  -> Done! Size: {:.2f} MB".format(sz))

def make_zip():
    zip_path = os.path.join(SCRIPT_DIR, ZIP_NAME)
    print("Creating zip archive: {}...".format(ZIP_NAME))
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for d in INCLUDE_DIRS:
            dp = os.path.join(SCRIPT_DIR, d)
            if os.path.exists(dp):
                for root, dirs, files in os.walk(dp):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, SCRIPT_DIR)
                        zf.write(full_path, arcname=rel_path)
        for f in INCLUDE_FILES:
            fp = os.path.join(SCRIPT_DIR, f)
            if os.path.exists(fp):
                zf.write(fp, arcname=f)
    sz = os.path.getsize(zip_path) / (1024 * 1024)
    print("  -> Done! Size: {:.2f} MB".format(sz))

def main():
    print("=" * 80)
    print(" PACKING CrCl3 2x2 H ADSORPTION CALCULATIONS")
    print("=" * 80)
    make_tar()
    make_zip()
    print("\n" + "=" * 80)
    print(" CLUSTER TRANSFER INSTRUCTIONS (Port 7722):")
    print("=" * 80)
    print(" Transfer command:")
    print("   scp -P 7722 {}/{} juan@gmcan.unmsm.edu.pe:~/".format(SCRIPT_DIR, TAR_NAME))
    print("\n Unpack command on cluster:")
    print("   tar -xzf {}".format(TAR_NAME))
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
