#!/usr/bin/env python3
"""
PACK CALCULATIONS FOR CLUSTER DEPLOYMENT (3x3 Supercell)
"""
import os, tarfile, zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TAR_NAME = "crcl3_3x3_h_ads_without_U.tar.gz"
ZIP_NAME = "crcl3_3x3_h_ads_without_U.zip"
INCLUDE_DIRS = ["no_vdw", "yes_vdw"]
INCLUDE_FILES = ["setup_h_ads.py", "verify_supercell.py", "pack_calculations.py"]

def make_tar():
    tar_path = os.path.join(SCRIPT_DIR, TAR_NAME)
    print("Creating tar.gz: {}...".format(TAR_NAME))
    with tarfile.open(tar_path, "w:gz") as tar:
        for d in INCLUDE_DIRS:
            dp = os.path.join(SCRIPT_DIR, d)
            if os.path.exists(dp):
                tar.add(dp, arcname=d)
        for f in INCLUDE_FILES:
            fp = os.path.join(SCRIPT_DIR, f)
            if os.path.exists(fp):
                tar.add(fp, arcname=f)
    print("  -> Size: {:.2f} MB".format(os.path.getsize(tar_path) / (1024*1024)))

def make_zip():
    zip_path = os.path.join(SCRIPT_DIR, ZIP_NAME)
    print("Creating zip: {}...".format(ZIP_NAME))
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for d in INCLUDE_DIRS:
            dp = os.path.join(SCRIPT_DIR, d)
            if os.path.exists(dp):
                for root, dirs, files in os.walk(dp):
                    for file in files:
                        full_path = os.path.join(root, file)
                        zf.write(full_path, arcname=os.path.relpath(full_path, SCRIPT_DIR))
        for f in INCLUDE_FILES:
            fp = os.path.join(SCRIPT_DIR, f)
            if os.path.exists(fp):
                zf.write(fp, arcname=f)
    print("  -> Size: {:.2f} MB".format(os.path.getsize(zip_path) / (1024*1024)))

if __name__ == "__main__":
    make_tar()
    make_zip()
