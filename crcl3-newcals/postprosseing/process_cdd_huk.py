#!/usr/bin/env /home/carlos/offline_python/bin/python3
import os
import sys
import shutil
import subprocess
import numpy as np

BASE_DIR = "/home/carlos/crcl3-newcals/cdd_Co_Ucr_calculation"
DIR_COMPLEX = os.path.join(BASE_DIR, "01_scf_complex")
DIR_SLAB = os.path.join(BASE_DIR, "02_cdd_slab")
DIR_TM = os.path.join(BASE_DIR, "03_isolated_tm")
DIR_OUT = os.path.join(BASE_DIR, "04_cdd_output")
os.makedirs(DIR_OUT, exist_ok=True)

def parse_chgcar(file_path):
    print(f"[INFO] Reading CHGCAR: {file_path}...")
    with open(file_path, "r") as f:
        system = f.readline()
        scale = float(f.readline().strip())
        a1 = [float(x) * scale for x in f.readline().split()]
        a2 = [float(x) * scale for x in f.readline().split()]
        a3 = [float(x) * scale for x in f.readline().split()]
        
        species = f.readline().split()
        try:
            counts = [int(x) for x in species]
            species = [f"Elem{i}" for i in range(len(counts))]
        except ValueError:
            counts = [int(x) for x in f.readline().split()]
            
        coord_type = f.readline().strip()
        num_atoms = sum(counts)
        coords = []
        for _ in range(num_atoms):
            coords.append([float(x) for x in f.readline().split()[:3]])
            
        blank = f.readline()
        ngx, ngy, ngz = [int(x) for x in f.readline().split()[:3]]
        total_pts = ngx * ngy * ngz
        print(f"  Grid: {ngx} x {ngy} x {ngz} = {total_pts} points")
        
        chg_data = []
        while len(chg_data) < total_pts:
            line = f.readline()
            if not line:
                break
            chg_data.extend([float(x) for x in line.split()])
            
        chg_3d = np.array(chg_data[:total_pts]).reshape((ngz, ngy, ngx))
        
    return {
        "header_lines": {
            "system": system,
            "scale": scale,
            "a1": a1, "a2": a2, "a3": a3,
            "species": species,
            "counts": counts,
            "coord_type": coord_type,
            "coords": coords,
            "ngx": ngx, "ngy": ngy, "ngz": ngz
        },
        "chg": chg_3d
    }

def write_chgcar(file_path, header, chg_3d):
    print(f"[INFO] Writing CHGCAR to: {file_path}...")
    ngx, ngy, ngz = header["ngx"], header["ngy"], header["ngz"]
    with open(file_path, "w") as f:
        f.write(header["system"])
        f.write(f"   {header['scale']:.16f}\n")
        f.write(f" {header['a1'][0]:12.8f} {header['a1'][1]:12.8f} {header['a1'][2]:12.8f}\n")
        f.write(f" {header['a2'][0]:12.8f} {header['a2'][1]:12.8f} {header['a2'][2]:12.8f}\n")
        f.write(f" {header['a3'][0]:12.8f} {header['a3'][1]:12.8f} {header['a3'][2]:12.8f}\n")
        f.write(" " + " ".join(header["species"]) + "\n")
        f.write(" " + " ".join(str(c) for c in header["counts"]) + "\n")
        f.write(f"{header['coord_type']}\n")
        for c in header["coords"]:
            f.write(f" {c[0]:14.8f} {c[1]:14.8f} {c[2]:14.8f}\n")
        f.write("\n")
        f.write(f" {ngx:5d} {ngy:5d} {ngz:5d}\n")
        
        flat_data = chg_3d.flatten()
        for i in range(0, len(flat_data), 5):
            chunk = flat_data[i:i+5]
            f.write(" " + " ".join(f"{v:18.11E}" for v in chunk) + "\n")

def main():
    chg_cpx = os.path.join(DIR_COMPLEX, "CHGCAR")
    chg_slb = os.path.join(DIR_SLAB, "CHGCAR")
    chg_tm = os.path.join(DIR_TM, "CHGCAR")
    
    if not (os.path.exists(chg_cpx) and os.path.exists(chg_slb) and os.path.exists(chg_tm)):
        print("[ERROR] Missing one or more CHGCAR files!")
        sys.exit(1)
        
    d_cpx = parse_chgcar(chg_cpx)
    d_slb = parse_chgcar(chg_slb)
    d_tm = parse_chgcar(chg_tm)
    
    print("[INFO] Computing Delta rho = rho(complex) - rho(slab) - rho(isolated Co)...")
    delta_rho = d_cpx["chg"] - d_slb["chg"] - d_tm["chg"]
    
    diff_file = os.path.join(DIR_OUT, "CHGCAR_diff")
    write_chgcar(diff_file, d_cpx["header_lines"], delta_rho)
    print(f"[OK] Saved: {diff_file}")
    
    # 1D Planar Average
    planar_avg = np.mean(delta_rho, axis=(1, 2))
    cell_c = d_cpx["header_lines"]["a3"][2]
    z_coords = np.linspace(0, cell_c, len(planar_avg), endpoint=False)
    
    csv_file = os.path.join(DIR_OUT, "planar_average_ucr.csv")
    np.savetxt(csv_file, np.column_stack((z_coords, planar_avg)), delimiter=",", header="z_ang,delta_rho_e_per_ang", comments="")
    print(f"[OK] Saved planar average data: {csv_file}")
    
    # Run Bader
    aeccar0 = os.path.join(DIR_COMPLEX, "AECCAR0")
    aeccar2 = os.path.join(DIR_COMPLEX, "AECCAR2")
    if os.path.exists(aeccar0) and os.path.exists(aeccar2):
        print("[INFO] Running chgsum.pl and bader...")
        subprocess.run("/home/carlos/bin/chgsum.pl AECCAR0 AECCAR2", shell=True, cwd=DIR_COMPLEX, check=True)
        subprocess.run("/home/carlos/bin/bader CHGCAR -ref CHGCAR_sum", shell=True, cwd=DIR_COMPLEX, check=True)
        if os.path.exists(os.path.join(DIR_COMPLEX, "ACF.dat")):
            shutil.copy2(os.path.join(DIR_COMPLEX, "ACF.dat"), os.path.join(DIR_OUT, "ACF.dat"))
            print(f"[OK] Bader ACF.dat saved to {DIR_OUT}/ACF.dat")

if __name__ == "__main__":
    main()
