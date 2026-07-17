import os

base_dir = "/Users/apple/Research/abc/paper-adaptation/crcl3-newcals/f_crcl3-doped-for-HER"
tms = ["co", "fe", "ni"]

def get_toten(path):
    if not os.path.exists(path):
        return None
    toten = None
    with open(path, 'r') as f:
        for line in f:
            if "free energy    TOTEN" in line:
                toten = float(line.split("=")[1].split()[0].strip())
    return toten

results = {}

for tm in tms:
    ads_path = os.path.join(base_dir, f"crcl3-{tm}/static-scf/OUTCAR")
    emb_path = os.path.join(base_dir, f"doped_hollow_crcl3/crcl3-{tm}/static-scf/OUTCAR")
    pristine_path = os.path.join(base_dir, f"isolates/crcl3-{tm}/cdd_crcl3/OUTCAR")
    iso_path = os.path.join(base_dir, f"isolates/crcl3-{tm}/cdd_{tm}/OUTCAR")
    
    e_ads = get_toten(ads_path)
    e_emb = get_toten(emb_path)
    e_pri = get_toten(pristine_path)
    e_iso = get_toten(iso_path)
    
    if None not in [e_ads, e_emb, e_pri, e_iso]:
        form_ads = e_ads - (e_pri + e_iso)
        form_emb = e_emb - (e_pri + e_iso)
    else:
        form_ads = None
        form_emb = None
        
    results[tm] = {
        'ads': e_ads,
        'emb': e_emb,
        'pri': e_pri,
        'iso': e_iso,
        'form_ads': form_ads,
        'form_emb': form_emb
    }

# Save to .dat file
out_dat = os.path.join(base_dir, "HER_energies.dat")
with open(out_dat, 'w') as f:
    f.write(f"{'TM':<5} {'E_adsorbed':>12} {'E_embedded':>12} {'E_pristine':>12} {'E_isolated':>12} {'E_form_ads':>12} {'E_form_emb':>12}\n")
    for tm in tms:
        r = results[tm]
        f.write(f"{tm.upper():<5} {r['ads']:>12.4f} {r['emb']:>12.4f} {r['pri']:>12.4f} {r['iso']:>12.4f} {r['form_ads']:>12.4f} {r['form_emb']:>12.4f}\n")

print(open(out_dat).read())
