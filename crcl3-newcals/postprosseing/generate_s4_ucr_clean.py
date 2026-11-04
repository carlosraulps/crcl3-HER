"""Figure S4 from spin-summed ICOHPLIST at EF; reject conflicted source files."""
from pathlib import Path
import csv
import hashlib
import json
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

POST = Path(__file__).resolve().parent
OUT = POST / 'images-juan/06_Fig6_COHP_Bonding_Analysis/S4_Ucr_checked'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'pdf.fonttype': 42})
results, audit, rows = {}, [], []
for metal in ['Co', 'Fe', 'Ni']:
    for mode, expected in [('adsorbed', 3), ('embedded', 6)]:
        # Ni's original directory contains merge conflicts; the parallel run is intact.
        folder = POST.parent / 'cohp_lobster_Ucr' / mode / (metal if metal != 'Ni' else 'Ni_parallel')
        path = folder / 'ICOHPLIST.lobster'
        source = path.read_text()
        incar = (folder / 'INCAR').read_text()
        log = (folder / 'lobsterout').read_text()
        assert '<<<<<<<' not in source + incar + log
        assert re.search(r'LDAUU\s*=\s*3\.29\s+0\.00\s+0\.00', incar)
        assert 'finished in' in log
        bonds = []
        for line in source.splitlines():
            parts = line.split()
            if len(parts) != 9 or not parts[0].isdigit():
                continue
            if metal+'33' not in parts[1:3] or not any(s.startswith('Cl') for s in parts[1:3]):
                continue
            bond = dict(metal=metal, mode=mode, pair='–'.join(parts[1:3]),
                        distance_A=float(parts[3]), ICOHP_eV=float(parts[7])+float(parts[8]))
            bonds.append(bond)
        assert len(bonds) == expected, (folder, len(bonds))
        assert len({b['pair'] for b in bonds}) == expected
        results[metal, mode] = sorted(bonds, key=lambda b: b['distance_A'])
        rows.extend(bonds)
        audit.append(dict(source=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                          bonds=len(bonds), charge_spilling_percent=re.findall(r'abs\. charge spilling:\s*([\d.]+)%', log),
                          warnings=[s for s in log.splitlines() if 'WARNING:' in s],
                          mean_ICOHP_eV=float(np.mean([b['ICOHP_eV'] for b in bonds])),
                          sum_ICOHP_eV=float(sum(b['ICOHP_eV'] for b in bonds))))

colors = {'adsorbed': '#294765', 'embedded': '#c55045'}
fig = plt.figure(figsize=(15, 9), layout='constrained')
grid = fig.add_gridspec(2, 6, height_ratios=[1.4, 1])
for i, metal in enumerate(['Co', 'Fe', 'Ni']):
    ax = fig.add_subplot(grid[0, i*2:i*2+2])
    bonds = results[metal, 'adsorbed'] + results[metal, 'embedded']
    values = [b['ICOHP_eV'] for b in bonds]
    bars = ax.barh(range(9), values, color=[colors[b['mode']] for b in bonds])
    ax.set_yticks(range(9), [b['pair'] for b in bonds])
    ax.invert_yaxis()
    ax.set_xlim(-2.8, 0)
    ax.set_xlabel('ICOHP at E$_F$ (eV/bond)')
    ax.set_title(f'({chr(97+i)}) {metal}–Cl', loc='left', weight='bold')
    ax.axhline(2.5, color='0.7', lw=.8)
    for bar, value in zip(bars, values):
        ax.text(value-.04, bar.get_y()+bar.get_height()/2, f'{value:.2f}', ha='right', va='center', fontsize=10)
for j, (reducer, title, ylabel) in enumerate([(np.mean, '(d) Average bond strength', 'ICOHP (eV/bond)'),
                                            (np.sum, '(e) Cumulative bonding', 'Σ ICOHP (eV)')]):
    ax = fig.add_subplot(grid[1, 1+2*j:3+2*j])
    for mode, dx, label in [('adsorbed', -.19, 'Adsorbed'), ('embedded', .19, 'Embedded')]:
        values = [reducer([b['ICOHP_eV'] for b in results[m, mode]]) for m in ['Co', 'Fe', 'Ni']]
        bars = ax.bar(np.arange(3)+dx, values, width=.36, color=colors[mode], label=label)
        for bar, value in zip(bars, values):
            ax.annotate(f'{value:.2f}', (bar.get_x()+bar.get_width()/2, value),
                        xytext=(0, -13), textcoords='offset points', ha='center', fontsize=10)
    ax.set_xticks(range(3), ['Co', 'Fe', 'Ni'])
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc='left', weight='bold')
    ax.set_ylim((-2.7, 0) if j == 0 else (-9, 0))
fig.suptitle('Figure S4 · U applied only to Cr (U$_{Cr}$ = 3.29 eV; U$_{TM}$ = 0)', fontsize=15)
fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=colors[m]) for m in colors],
           labels=['Adsorbed (3 TM–Cl bonds)', 'Embedded (6 TM–Cl bonds)'],
           loc='outside lower center', ncol=2, frameon=False)
for ext in ['pdf', 'png', 'svg']:
    fig.savefig(OUT / f'FigS4_Ucr.{ext}', dpi=300)
with (OUT / 'FigS4_Ucr_bond_values.csv').open('w') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
(OUT / 'source_audit.json').write_text(json.dumps(audit, indent=2))
(OUT / 'README.md').write_text('''# Figure S4: U only on Cr

UCr=3.29 eV, UTM=0. ICOHP values at EF are the sum of both spin channels
from ICOHPLIST.lobster. Each metal has three adsorbed and six embedded bonds.
Ni uses Ni_parallel because the ordinary Ni folders contain unresolved Git
merge conflicts; no conflicted calculation files were changed.
Source hashes, projection spillings, and original LOBSTER warnings are in
source_audit.json. LOBSTER logs warn about malformed explicit cohpBetweenAtom
lines; the required TM–Cl bonds are present in the generated ICOHPLIST files.
These are review copies; projection warnings and the Ni run choice require
review before publication. Original figures and manuscript files are preserved.
''')
print(OUT)
print('Verified 27 bonds across six calculations; spin-summed ICOHP at EF.')
