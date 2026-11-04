"""Less crowded Fig4 review copies: identical +/-0.020 e/A^3, 40% opacity."""
import json
import shutil
import normalize_fig4_cdd as n


def main():
    previous = n.OUT
    output = previous / 'isovalue_0p020'
    figures = n.FIG / 'isovalue_0p020'
    output.mkdir(exist_ok=True)
    figures.mkdir(exist_ok=True)
    audit = {r['tag']: r for r in json.loads((previous / 'remote_source_audit.json').read_text())}
    for tier in ['Ucr', 'Uall']:
        shutil.copy2(n.FIG / f'Fig4_{tier}.png', figures / f'Fig4_{tier}.png')
        for metal in ['Co', 'Fe', 'Ni']:
            tag = f'{metal}_{tier}'
            path = n.density_source(metal, tier, audit)
            project = output / f'{tag}.vesta'
            project.write_text(n.make_project(path, density=.020, opacity=102))
            n.render(project, output / f'{tag}_full.png')
            print(f'Rendered {tag}: +/-0.020 e/A^3, opacity 40%', flush=True)
    n.OUT, n.FIG = output, figures
    n.assemble(density=.020, opacity=102)


if __name__ == '__main__':
    main()
