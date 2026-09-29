#!/usr/bin/env python3
"""
PACK CLEAN Co, Fe, Ni ADSORPTION SUITE FOR SLURM CLUSTER (NO SYMLINKS)
"""
import os
import tarfile
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TAR_NAME = "crcl3_2x2_CoFeNi_ads_without_U.tar.gz"
ZIP_NAME = "crcl3_2x2_CoFeNi_ads_without_U.zip"

DIRS_TO_PACK = [
    "crcl3-2x2-co_ads-without-U",
    "crcl3-2x2-fe_ads-without-U",
    "crcl3-2x2-ni_ads-without-U"
]
ROOT_FILES = ["README.md", "verify_all.py", "submit_slurm_jobs.sh", "pack_cofeni_suite.py"]

def make_tar():
    tar_path = os.path.join(SCRIPT_DIR, TAR_NAME)
    if os.path.exists(tar_path):
        os.remove(tar_path)
    print("Creating tar.gz archive: {}...".format(TAR_NAME))
    with tarfile.open(tar_path, "w:gz", dereference=False) as tar:
        for d in DIRS_TO_PACK:
            dp = os.path.join(SCRIPT_DIR, d)
            if os.path.exists(dp):
                # Add directory avoiding any internal nested archives
                for root, dirs, files in os.walk(dp):
                    for file in files:
                        if file.endswith(".tar.gz") or file.endswith(".zip"):
                            continue
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, SCRIPT_DIR)
                        tar.add(full_path, arcname=rel_path)
        for f in ROOT_FILES:
            fp = os.path.join(SCRIPT_DIR, f)
            if os.path.exists(fp):
                tar.add(fp, arcname=f)
    sz = os.path.getsize(tar_path) / (1024 * 1024)
    print("  -> Done! Size: {:.2f} MB".format(sz))

def make_zip():
    zip_path = os.path.join(SCRIPT_DIR, ZIP_NAME)
    if os.path.exists(zip_path):
        os.remove(zip_path)
    print("Creating zip archive: {}...".format(ZIP_NAME))
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for d in DIRS_TO_PACK:
            dp = os.path.join(SCRIPT_DIR, d)
            if os.path.exists(dp):
                for root, dirs, files in os.walk(dp):
                    for file in files:
                        if file.endswith(".tar.gz") or file.endswith(".zip"):
                            continue
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, SCRIPT_DIR)
                        zf.write(full_path, arcname=rel_path)
        for f in ROOT_FILES:
            fp = os.path.join(SCRIPT_DIR, f)
            if os.path.exists(fp):
                zf.write(fp, arcname=f)
    sz = os.path.getsize(zip_path) / (1024 * 1024)
    print("  -> Done! Size: {:.2f} MB".format(sz))

if __name__ == "__main__":
    make_tar()
    make_zip()
