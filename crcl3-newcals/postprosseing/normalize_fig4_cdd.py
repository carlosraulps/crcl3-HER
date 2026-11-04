"""Re-render Fig4 a-c with frozen-reference CDD and one physical isovalue.

Run with the research Python environment and VESTA installed. Outputs are
review copies: the original figures and panels d-f are preserved.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import time

import cv2
import fitz
import numpy as np

POST = Path(__file__).resolve().parent
DATA = POST / 'cdd_comparison'
OUT = DATA / 'normalized_2026-10-29'
FIG = POST / 'images-juan/04_Fig4_CDD_and_Bader_Charge'
VESTA = '/Applications/VESTA.app/Contents/MacOS/VESTA'
BOHR_ANG = 0.529177210544


def vesta_level(density_e_ang3):
    # VESTA imports VASP densities in e/bohr^3 (VESTA manual, chapter 18).
    return density_e_ang3 * BOHR_ANG**3


def read_header(path):
    with path.open() as f:
        f.readline()
        scale = float(f.readline())
        cell = np.array([[float(x) for x in f.readline().split()] for _ in range(3)]) * scale
        species = f.readline().split()
        counts = list(map(int, f.readline().split()))
        mode = f.readline()
        if mode.lower().startswith('s'):
            mode = f.readline()
        coords = np.array([[float(x) for x in f.readline().split()[:3]] for _ in range(sum(counts))])
        if mode.lower().startswith(('c', 'k')):
            coords = coords @ np.linalg.inv(cell)
        offset = f.tell()
    assert species[:2] == ['Cr', 'Cl'] and counts == [8, 24, 1]
    assert np.allclose(cell, [[12.092549, 0, 0], [-6.046274, 10.472455, 0], [0, 0, 20]])
    return cell, species, counts, coords, offset


def make_project(path, density=.005, opacity=153):
    _, species, counts, coords, _ = read_header(path)
    text = (OUT / 'render_template.vesta').read_text()
    text = re.sub(r'IMPORT_DENSITY 1\n[^\n]+', f'IMPORT_DENSITY 1\n+1.000000 {path.resolve()}', text)
    atoms = []
    colors = {'Cr': (0, 0, 158), 'Cl': (49, 252, 2), 'Co': (29, 190, 193),
              'Fe': (168, 116, 31), 'Ni': (234, 32, 233)}
    sites = []
    index = 0
    for symbol, count in zip(species, counts):
        for n in range(count):
            x, y, z = coords[index]
            index += 1
            atoms += [f'{index} {symbol} {symbol}{n+1} 1.0 {x:.8f} {y:.8f} {z:.8f} 1a 1',
                      '0.0 0.0 0.0 0.0']
            rgb = ' '.join(map(str, colors[symbol]))
            radius = 1.29 if symbol == 'Cr' else .99 if symbol == 'Cl' else 1.25
            sites.append(f'{index} {symbol}{n+1} {radius} {rgb} {rgb} 204 0')
    text = re.sub(r'STRUC\n.*?\nTHERI', 'STRUC\n' + '\n'.join(atoms) + '\n0 0 0 0 0 0 0\nTHERI', text, flags=re.S)
    text = re.sub(r'SITET\n.*?\nVECTR', 'SITET\n' + '\n'.join(sites) + '\n0 0 0 0 0 0\nVECTR', text, flags=re.S)
    text = re.sub(r'ATOMT\n.*?\nSCENE', 'ATOMT\n0 0 0 0 0 0\nSCENE', text, flags=re.S)
    # Identical bond cutoffs, camera, cell boundaries and surface appearance.
    bonds = '\n'.join(f'{i+1} {s} Cl 0.0 2.90 0 0 0 0 1 .25 2.0 127 127 127'
                      for i, s in enumerate(['Cr', species[-1]]))
    text = re.sub(r'SBOND\n.*?\nSITET', 'SBOND\n' + bonds + '\n0 0 0 0\nSITET', text, flags=re.S)
    iso = vesta_level(density)
    text = re.sub(r'ISURF\n.*?\nTEX3P',
                  f'ISURF\n  1   1 {iso:.12f} 255 255 0 {opacity} {opacity}\n'
                  f'  2   1 {-iso:.12f} 0 255 255 {opacity} {opacity}\n  0 0 0 0\nTEX3P', text, flags=re.S)
    text = text.replace('COMPS 1', 'COMPS 0')
    assert text.count('ISURF\n') == 1 and len(atoms) == 66
    return text


def render(project, output):
    output.unlink(missing_ok=True)
    with output.with_suffix('.log').open('w') as log:
        proc = subprocess.Popen([VESTA, '-open', str(project), '-export_img', 'scale=2', str(output)],
                                stdout=log, stderr=subprocess.STDOUT)
        try:
            last_size, stable = 0, 0
            for _ in range(120):
                size = output.stat().st_size if output.exists() else 0
                stable = stable + 1 if size > 20000 and size == last_size else 0
                if stable >= 4:
                    break
                if proc.poll() is not None:
                    raise RuntimeError(f'VESTA exited before export: {output}')
                last_size = size
                time.sleep(.5)
            else:
                raise TimeoutError(f'VESTA did not finish: {output}')
        finally:
            if proc.poll() is None:
                proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    img = cv2.imread(str(output))
    assert img is not None
    b, g, r = cv2.split(img)
    assert np.count_nonzero((r > 120) & (g > 120) & (b < 80)) > 200, 'Missing positive isosurface'


def density_source(metal, tier, audit):
    tag = f'{metal}_{tier}'
    if metal == 'Co':
        return DATA / f'CHGCAR_diff_{tier}'
    row = audit[tag]
    assert row['cell_match'] and row['grid_match'] and row['electronic_converged']
    assert row['slab_coordinate_error_A'] < 1e-6 and row['iso_coordinate_error_A'] < 1e-6
    path = OUT / f'CHGCAR_diff_{tag}'
    if path.exists():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
        return path
    # Rendering-only rounding to 1e-8 e/A^3 avoids transferring the full text grid.
    with np.load(OUT / f'{tag}_render_grid.npz', allow_pickle=False) as pack:
        assert str(pack['sha256']) == row['sha256']
        assert float(pack['step']) == 1e-8
        assert pack['q'].size == np.prod(row['grid']) and pack['q'].dtype == np.int32
        path = OUT / f'CHGCAR_render_{tag}'
        with path.open('w') as f:
            f.write(str(pack['header']))
            raw = pack['q'].astype(float) * float(pack['step']) * float(pack['volume'])
            np.savetxt(f, raw.reshape(-1, 5), fmt='%18.11E')
    return path


def assemble(density=.005, opacity=153):
    images = {f'{m}_{u}': cv2.imread(str(OUT / f'{m}_{u}_full.png'))
              for u in ['Ucr', 'Uall'] for m in ['Co', 'Fe', 'Ni']}
    if any(img is None for img in images.values()):
        raise FileNotFoundError('All six native renders are required before assembly')
    # Calibrate to the same unit-cell width even across different display sizes.
    width, height = 1330, 820
    transforms = {}
    for tag, img in images.items():
        ys, xs = np.where(np.all(img < 60, axis=2))
        scale = 1230 / (xs.max()-xs.min())
        cx, cy = (xs.max()+xs.min())/2, (ys.max()+ys.min())/2
        matrix = np.array([[scale, 0, width/2-cx*scale], [0, scale, height/2-cy*scale]])
        yn, xn = np.where(np.any(img < 245, axis=2))
        projected = np.column_stack([xn, yn, np.ones(len(xn))]) @ matrix.T
        assert np.all(projected.min(axis=0) > 2), 'Content would be cropped'
        assert np.all(projected.max(axis=0) < [width-2, height-2]), 'Content would be cropped'
        images[tag] = cv2.warpAffine(img, matrix, (width, height), flags=cv2.INTER_LANCZOS4,
                                     borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
        transforms[tag] = matrix.tolist()
    for tier in ['Ucr', 'Uall']:
        original = cv2.imread(str(FIG / f'Fig4_{tier}.png'))
        canvas = original.copy()
        canvas[20:980, 230:4450] = 255
        for i, (metal, cx) in enumerate(zip(['Co', 'Fe', 'Ni'], [1045, 2390, 3715])):
            resized = images[f'{metal}_{tier}']
            left, top = cx-width//2, 475-height//2
            canvas[top:top+height, left:left+width] = resized
            panel = canvas[20:1180, cx-700:cx+700]
            assert cv2.imwrite(str(FIG / f'panel_{chr(97+i)}_{metal}_CDD_{tier}_normalized.png'), panel)
        assert np.array_equal(canvas[980:], original[980:]), 'Panels d-f and labels changed'
        assert np.array_equal(canvas[:, :230], original[:, :230]), 'Atom legend changed'
        name = f'Fig4_{tier}_normalized'
        png = FIG / f'{name}.png'
        assert cv2.imwrite(str(png), canvas)
        h, w = canvas.shape[:2]
        with fitz.open() as doc:
            page = doc.new_page(width=w*72/300, height=h*72/300)
            page.insert_image(page.rect, filename=str(png))
            doc.set_metadata({'title': f'Figure 4 {tier}: a-c normalized to +/-{density:g} e/Angstrom^3',
                              'subject': 'Review copy; frozen Fe/Ni references; d-f preserved; see FIG4_AUDIT.md'})
            doc.save(FIG / f'{name}.pdf', deflate=True)
        top_png = OUT / f'Fig4_{tier}_abc_normalized.png'
        assert cv2.imwrite(str(top_png), canvas[:1180])
        with fitz.open() as doc:
            page = doc.new_page(width=w*72/300, height=1180*72/300)
            page.insert_image(page.rect, filename=str(top_png))
            doc.save(FIG / f'Fig4_{tier}_abc_normalized.pdf', deflate=True)
        print(f'Assembled {name}; d-f unchanged', flush=True)
    (OUT / 'render_settings.json').write_text(json.dumps({
        'density_e_per_A3': density, 'vesta_density_e_per_bohr3': vesta_level(density),
        'positive_rgb': [255, 255, 0], 'negative_rgb': [0, 255, 255],
        'opacity': opacity/255, 'view': 'along c; native SCENE identity',
        'bounds': [0, 1, 0, 1, 0, 1], 'unit_cell_width_pixels': 1230,
        'uniform_transforms': transforms, 'spatial_density_mask': False,
    }, indent=2))


def main():
    audit = {r['tag']: r for r in json.loads((OUT / 'remote_source_audit.json').read_text())}
    for tier in ['Ucr', 'Uall']:
        for metal in ['Co', 'Fe', 'Ni']:
            tag = f'{metal}_{tier}'
            path = density_source(metal, tier, audit)
            project = OUT / f'{tag}.vesta'
            project.write_text(make_project(path))
            render(project, OUT / f'{tag}_full.png')
            print(f'Rendered {tag}', flush=True)
    assemble()


if __name__ == '__main__':
    main()
