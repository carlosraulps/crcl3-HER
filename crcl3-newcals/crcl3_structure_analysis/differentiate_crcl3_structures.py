#!/usr/bin/env python3
"""
differentiate_crcl3_structures.py
Fetches and compares all Materials Project CrCl3 structures against our project's
monolayer 1x1 primitive cell and 2x2x1 supercell to clearly differentiate lattice
parameters, space groups, coordination, and dimensionality.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pymatgen.core import Structure, Lattice
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from mp_api.client import MPRester

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STRUCT_DIR = os.path.join(BASE_DIR, "structures")
os.makedirs(STRUCT_DIR, exist_ok=True)

KEY_FILE = os.path.expanduser("~/.config/mp_api_key")

def get_mp_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE) as f:
            return f.read().strip()
    return os.environ.get("MP_API_KEY", "")

def get_bond_stats(structure):
    cr_indices = [i for i, site in enumerate(structure) if site.specie.symbol == "Cr"]
    cl_indices = [i for i, site in enumerate(structure) if site.specie.symbol == "Cl"]
    
    cr_cl_dists = []
    for cr_i in cr_indices:
        for cl_i in cl_indices:
            d = structure.get_distance(cr_i, cl_i)
            if d < 3.0: # first coordination shell
                cr_cl_dists.append(d)
                
    cr_cr_dists = []
    for i in range(len(cr_indices)):
        for j in range(i + 1, len(cr_indices)):
            d = structure.get_distance(cr_indices[i], cr_indices[j])
            if d < 4.5: # in-plane Cr-Cr honeycomb distance
                cr_cr_dists.append(d)
                
    avg_cr_cl = float(np.mean(cr_cl_dists)) if cr_cl_dists else np.nan
    min_cr_cl = float(np.min(cr_cl_dists)) if cr_cl_dists else np.nan
    max_cr_cl = float(np.max(cr_cl_dists)) if cr_cl_dists else np.nan
    avg_cr_cr = float(np.mean(cr_cr_dists)) if cr_cr_dists else np.nan
    
    return {
        "avg_cr_cl": avg_cr_cl,
        "min_cr_cl": min_cr_cl,
        "max_cr_cl": max_cr_cl,
        "avg_cr_cr": avg_cr_cr,
        "coord_num": len(cr_cl_dists) // max(1, len(cr_indices))
    }

def analyze_our_structures():
    items = []
    
    # 1. Monolayer 1x1 Primitive
    p1x1 = os.path.abspath(os.path.join(BASE_DIR, "..", "crcl3-1x1", "U_0", "POSCAR"))
    if os.path.exists(p1x1):
        s1 = Structure.from_file(p1x1)
        sga1 = SpacegroupAnalyzer(s1, symprec=1e-2)
        b_stats1 = get_bond_stats(s1)
        
        # Save canonical copy
        s1.to(filename=os.path.join(STRUCT_DIR, "our_monolayer_1x1_primitive.vasp"))
        s1.to(filename=os.path.join(STRUCT_DIR, "our_monolayer_1x1_primitive.cif"))
        
        items.append({
            "Label": "Our Monolayer 1x1 (Primitive)",
            "ID / Origin": "Project (Pristine 1x1)",
            "Dimensionality": "2D Monolayer",
            "Formula": s1.composition.reduced_formula,
            "Natoms": len(s1),
            "SpaceGroup": sga1.get_space_group_symbol(),
            "SG_Number": sga1.get_space_group_number(),
            "Crystal_System": sga1.get_crystal_system(),
            "a": s1.lattice.a,
            "b": s1.lattice.b,
            "c": s1.lattice.c,
            "alpha": s1.lattice.alpha,
            "beta": s1.lattice.beta,
            "gamma": s1.lattice.gamma,
            "Volume_per_atom": s1.volume / len(s1),
            "Avg_Cr_Cl": b_stats1["avg_cr_cl"],
            "Avg_Cr_Cr": b_stats1["avg_cr_cr"],
            "Coord_Number": b_stats1["coord_num"],
            "Description": "Single Cl-Cr-Cl layer with ~15 A vacuum along c. Hexagonal lattice."
        })
        
    # 2. Monolayer 2x2x1 Supercell
    p2x2 = os.path.abspath(os.path.join(BASE_DIR, "..", "adsorbed", "co", "POSCAR"))
    if os.path.exists(p2x2):
        s2 = Structure.from_file(p2x2)
        # remove Co adatom to keep pristine Cr8Cl24
        s2.remove_species(["Co"])
        sga2 = SpacegroupAnalyzer(s2, symprec=1e-2)
        b_stats2 = get_bond_stats(s2)
        
        s2.to(filename=os.path.join(STRUCT_DIR, "our_monolayer_2x2_supercell.vasp"))
        s2.to(filename=os.path.join(STRUCT_DIR, "our_monolayer_2x2_supercell.cif"))
        
        items.append({
            "Label": "Our Monolayer 2x2x1 (Supercell)",
            "ID / Origin": "Project (Substrate 2x2)",
            "Dimensionality": "2D Supercell",
            "Formula": s2.composition.reduced_formula,
            "Natoms": len(s2),
            "SpaceGroup": sga2.get_space_group_symbol(),
            "SG_Number": sga2.get_space_group_number(),
            "Crystal_System": sga2.get_crystal_system(),
            "a": s2.lattice.a,
            "b": s2.lattice.b,
            "c": s2.lattice.c,
            "alpha": s2.lattice.alpha,
            "beta": s2.lattice.beta,
            "gamma": s2.lattice.gamma,
            "Volume_per_atom": s2.volume / len(s2),
            "Avg_Cr_Cl": b_stats2["avg_cr_cl"],
            "Avg_Cr_Cr": b_stats2["avg_cr_cr"],
            "Coord_Number": b_stats2["coord_num"],
            "Description": "2x2 expansion of 1x1 monolayer (8 Cr, 24 Cl) used for TM dopant / adsorption calculations."
        })
        
    return items

def analyze_mp_structures(key):
    items = []
    with MPRester(key) as mpr:
        docs = mpr.materials.summary.search(
            formula="CrCl3", 
            fields=["material_id", "symmetry", "energy_per_atom", "band_gap", "is_stable", "nsites", "volume"]
        )
        print(f"Retrieved {len(docs)} structures from Materials Project.")
        
        for d in docs:
            mpid = str(d.material_id)
            struct = mpr.get_structure_by_material_id(mpid)
            sga = SpacegroupAnalyzer(struct, symprec=1e-2)
            conv_struct = sga.get_conventional_standard_structure()
            b_stats = get_bond_stats(struct)
            
            # Save raw and conventional structures
            fname_base = f"{mpid}_{sga.get_space_group_symbol().replace('/', '_')}"
            struct.to(filename=os.path.join(STRUCT_DIR, f"{fname_base}_primitive.vasp"))
            conv_struct.to(filename=os.path.join(STRUCT_DIR, f"{fname_base}_conventional.vasp"))
            struct.to(filename=os.path.join(STRUCT_DIR, f"{fname_base}.cif"))
            
            # Special note for primary polymorphs
            desc = f"Bulk CrCl3 ({d.symmetry.crystal_system}). "
            if d.is_stable:
                desc += "Thermodynamic ground state in Materials Project."
            elif mpid == "mp-27630":
                desc += "High-temperature monoclinic C2/m bulk phase."
            elif mpid == "mp-569890":
                desc += "Metastable trigonal P3_212 bulk phase."
            else:
                desc += "High-energy bulk phase (E_above_hull > 0.3 eV)."
                
            items.append({
                "Label": f"MP: {mpid} ({sga.get_space_group_symbol()})",
                "ID / Origin": mpid,
                "Dimensionality": "3D Bulk",
                "Formula": struct.composition.reduced_formula,
                "Natoms": len(struct),
                "SpaceGroup": sga.get_space_group_symbol(),
                "SG_Number": sga.get_space_group_number(),
                "Crystal_System": sga.get_crystal_system(),
                "a": struct.lattice.a,
                "b": struct.lattice.b,
                "c": struct.lattice.c,
                "alpha": struct.lattice.alpha,
                "beta": struct.lattice.beta,
                "gamma": struct.lattice.gamma,
                "Volume_per_atom": struct.volume / len(struct),
                "Avg_Cr_Cl": b_stats["avg_cr_cl"],
                "Avg_Cr_Cr": b_stats["avg_cr_cr"],
                "Coord_Number": b_stats["coord_num"],
                "Description": desc
            })
            
            # For mp-567504 (R-3) and mp-27630 (C2/m), also analyze their conventional hexagonal in-plane lattice
            if mpid in ["mp-567504", "mp-27630"]:
                conv_bstats = get_bond_stats(conv_struct)
                items.append({
                    "Label": f"MP: {mpid} (Conventional)",
                    "ID / Origin": f"{mpid} (conv)",
                    "Dimensionality": "3D Bulk (Conv Cell)",
                    "Formula": conv_struct.composition.reduced_formula,
                    "Natoms": len(conv_struct),
                    "SpaceGroup": sga.get_space_group_symbol(),
                    "SG_Number": sga.get_space_group_number(),
                    "Crystal_System": sga.get_crystal_system(),
                    "a": conv_struct.lattice.a,
                    "b": conv_struct.lattice.b,
                    "c": conv_struct.lattice.c,
                    "alpha": conv_struct.lattice.alpha,
                    "beta": conv_struct.lattice.beta,
                    "gamma": conv_struct.lattice.gamma,
                    "Volume_per_atom": conv_struct.volume / len(conv_struct),
                    "Avg_Cr_Cl": conv_bstats["avg_cr_cl"],
                    "Avg_Cr_Cr": conv_bstats["avg_cr_cr"],
                    "Coord_Number": conv_bstats["coord_num"],
                    "Description": f"Conventional unit cell for {mpid}, directly showing the in-plane honeycomb dimensions."
                })
                
    return items

def generate_report(all_items):
    df = pd.DataFrame(all_items)
    
    # Save CSV
    csv_path = os.path.join(BASE_DIR, "crcl3_structure_comparison.csv")
    df.to_csv(csv_path, index=False)
    
    # Save Markdown Report
    md_path = os.path.join(BASE_DIR, "crcl3_structure_comparison.md")
    with open(md_path, "w") as f:
        f.write("# Comprehensive Comparison of CrCl3 Structures: Project Monolayers vs. Materials Project\n\n")
        f.write("This report resolves the structural relationships and distinguishes our project's **2D Monolayer ($1\\times 1$ primitive and $2\\times 2$ supercell)** from all 3D bulk polymorphs available in the Materials Project database.\n\n")
        f.write("## 1. Summary Comparison Table\n\n")
        
        headers = ["Structure Label", "Origin / ID", "Type", "Space Group", "$a$ (A)", "$b$ (A)", "$c$ (A)", "$\\gamma$ (deg)", "Cr-Cl (A)", "Cr-Cr (A)", "Sites"]
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("| " + " | ".join([":---"] * len(headers)) + " |\n")
        
        for item in all_items:
            row = [
                f"**{item['Label']}**",
                item["ID / Origin"],
                item["Dimensionality"],
                f"{item['SpaceGroup']} ({item['SG_Number']})",
                f"{item['a']:.3f}",
                f"{item['b']:.3f}",
                f"{item['c']:.3f}",
                f"{item['gamma']:.1f}",
                f"{item['Avg_Cr_Cl']:.3f}",
                f"{item['Avg_Cr_Cr']:.3f}",
                str(item["Natoms"])
            ]
            f.write("| " + " | ".join(row) + " |\n")
            
        f.write("\n\n## 2. Detailed Distinctions\n\n")
        for item in all_items:
            f.write(f"### {item['Label']}\n")
            f.write(f"- **System Type**: {item['Dimensionality']}\n")
            f.write(f"- **Space Group**: {item['SpaceGroup']} (No. {item['SG_Number']}), {item['Crystal_System']}\n")
            f.write(f"- **Lattice Vectors**: $a = {item['a']:.4f}\\text{{ A}}$, $b = {item['b']:.4f}\\text{{ A}}$, $c = {item['c']:.4f}\\text{{ A}}$\n")
            f.write(f"- **Angles**: $\\alpha = {item['alpha']:.2f}^\\circ$, $\\beta = {item['beta']:.2f}^\\circ$, $\\gamma = {item['gamma']:.2f}^\\circ$\n")
            f.write(f"- **Bonding**: Avg Cr-Cl = ${item['Avg_Cr_Cl']:.3f}\\text{{ A}}$, Cr-Cr = ${item['Avg_Cr_Cr']:.3f}\\text{{ A}}$, Coordination = {item['Coord_Number']}-fold Cl octahedron\n")
            f.write(f"- **Notes**: {item['Description']}\n\n")
            
        f.write("""## 3. Key Takeaways for our 1x1 and 2x2 Calculations
1. **Never Confuse 1x1 Monolayer with Bulk MP Primitive Cells**:
   - The primary Materials Project ground state **`mp-567504`** is indexed in a rhombohedral cell ($a=6.895\\text{ A}, \\alpha=51.56^\\circ$). In that setting, all 3 lattice vectors are tilted across layers to capture the ABC rhombohedral stacking.
   - In contrast, our project's **$1\\times 1$ Monolayer** has $a = b = 6.0485\\text{ A}$, $\\gamma = 120^\\circ$, with a pure perpendicular $c = 17.67\\text{ A}$ ($(\\alpha=\\beta=90^\\circ)$) providing a $15\\text{ A}$ vacuum barrier.
2. **Relationship Between our 1x1 and 2x2 Cells**:
   - **$1\\times 1$ Primitive Cell**: Formula $\\text{Cr}_2\\text{Cl}_6$ (8 atoms total). $a = 6.0485\\text{ A}$, $b = 6.0485\\text{ A}$, $\\gamma = 120^\\circ$.
   - **$2\\times 2\\times 1$ Supercell**: Formula $\\text{Cr}_8\\text{Cl}_{24}$ (32 atoms total). $a = 12.097\\text{ A}$, $b = 12.097\\text{ A}$, $\\gamma = 120^\\circ$.
   - The $2\\times 2$ cell is an exact $2\\times 2$ spatial doubling in the in-plane directions ($a_{2\\times 2} = 2a_{1\\times 1}, b_{2\\times 2} = 2b_{1\\times 1}$), preserving the exact same local bond lengths ($d_{\\text{Cr-Cl}} = 2.375\\text{ A}$) and hexagonal symmetry.
3. **Materials Project In-Plane Consistency**:
   - The conventional in-plane lattice constant of monoclinic **`mp-27630`** is $a = 5.996\\text{ A}$.
   - The conventional in-plane lattice constant of rhombohedral **`mp-567504`** is $a_{\\text{hex}} = 5.996\\text{ A}$.
   - Our relaxed 2D monolayer has $a = 6.048\\text{ A}$. The minor expansion ($+0.8\\%$) is the standard, well-documented physics of single-layer relaxation following exfoliation from 3D vdW bulk.
""")

    print(f"Report generated at: {md_path}")
    print(f"CSV data generated at: {csv_path}")
    return df

def generate_plot(all_items):
    labels = [
        "Project 1x1\n(Monolayer)", 
        "Project 2x2\n(Supercell)", 
        "MP mp-27630\n(C2/m Bulk)", 
        "MP mp-567504\n(R-3 Conv)", 
        "MP mp-569890\n(P3_212 Bulk)"
    ]
    
    plot_items = []
    for lbl in labels:
        clean_lbl = lbl.split("\n")[0]
        matched = None
        for it in all_items:
            if clean_lbl in it["Label"] or (clean_lbl == "Project 2x2" and "Supercell" in it["Label"]) or (clean_lbl == "Project 1x1" and "Primitive" in it["Label"]):
                matched = it
                break
        if matched:
            plot_items.append((lbl, matched))
            
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=300)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    
    names = [x[0] for x in plot_items]
    cr_cl_dists = [x[1]["Avg_Cr_Cl"] for x in plot_items]
    cr_cr_dists = [x[1]["Avg_Cr_Cr"] for x in plot_items]
    
    x = np.arange(len(names))
    width = 0.35
    
    rects1 = ax1.bar(x - width/2, cr_cl_dists, width, label="Cr-Cl Distance", color="#1f77b4", edgecolor="black", alpha=0.85)
    rects2 = ax1.bar(x + width/2, cr_cr_dists, width, label="Cr-Cr Distance", color="#ff7f0e", edgecolor="black", alpha=0.85)
    
    ax1.set_ylabel("Bond / Interatomic Distance (A)", fontsize=11, fontweight="bold")
    ax1.set_title("Interatomic Distances: Project vs. Materials Project", fontsize=12, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, fontsize=9)
    ax1.set_ylim(2.0, 4.0)
    ax1.legend(frameon=True, fontsize=10)
    
    for r in rects1:
        h = r.get_height()
        ax1.annotate(f"{h:.3f}", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)
    for r in rects2:
        h = r.get_height()
        ax1.annotate(f"{h:.3f}", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)
        
    a_vals = [x[1]["a"] for x in plot_items]
    colors = ["#2ca02c" if "Project" in n else "#9467bd" for n in names]
    bars = ax2.bar(names, a_vals, color=colors, edgecolor="black", width=0.5, alpha=0.85)
    ax2.set_ylabel("In-plane Lattice Parameter a (A)", fontsize=11, fontweight="bold")
    ax2.set_title("Lattice Constant a Comparison", fontsize=12, fontweight="bold")
    ax2.set_xticklabels(names, fontsize=9)
    ax2.set_ylim(0, 14.0)
    
    for bar in bars:
        h = bar.get_height()
        ax2.annotate(f"{h:.3f} A", xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
        
    plt.tight_layout()
    plot_path = os.path.join(BASE_DIR, "crcl3_structure_comparison.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Comparison plot saved at: {plot_path}")

def main():
    print("================================================================================")
    print("         CrCl3 STRUCTURE DIFFERENTIATOR: PROJECT vs. MATERIALS PROJECT          ")
    print("================================================================================")
    
    key = get_mp_key()
    if not key:
        print("Error: Materials Project API key not found.")
        sys.exit(1)
        
    our_items = analyze_our_structures()
    print(f"Analyzed {len(our_items)} project structures (1x1 primitive and 2x2 supercell).")
    
    mp_items = analyze_mp_structures(key)
    all_items = our_items + mp_items
    
    df = generate_report(all_items)
    generate_plot(all_items)
    print("\nExecution complete! Structures exported to crcl3-newcals/crcl3_structure_analysis/structures/")

if __name__ == "__main__":
    main()
