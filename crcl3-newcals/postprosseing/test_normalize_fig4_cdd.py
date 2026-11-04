import unittest

from normalize_fig4_cdd import DATA, OUT, make_project, vesta_level


class DensityNormalizationTests(unittest.TestCase):
    def test_physical_isovalue_uses_cubic_bohr_conversion(self):
        self.assertAlmostEqual(vesta_level(.005), .0007409235558528606, places=14)
        self.assertAlmostEqual(vesta_level(-.005), -.0007409235558528606, places=14)

    def test_native_project_has_two_separately_colored_surfaces(self):
        project = make_project(DATA / 'CHGCAR_diff_Ucr')
        block = project.split('\nISURF\n')[1].split('\nTEX3P')[0]
        rows = [line.split() for line in block.splitlines()[:2]]
        self.assertEqual([float(row[2]) for row in rows], [.000740923556, -.000740923556])
        self.assertEqual([row[1] for row in rows], ['1', '1'])
        self.assertEqual([row[3:6] for row in rows], [['255', '255', '0'], ['0', '255', '255']])
        self.assertIn('COMPS 0', project)
        self.assertNotIn('\nSURFC\n', project)

    def test_project_uses_corrected_fe_geometry(self):
        project = make_project(OUT / 'CHGCAR_diff_Fe_Ucr')
        structure = project.split('\nSTRUC\n')[1].split('\nTHERI')[0]
        self.assertIn('33 Fe Fe1 1.0 0.50000000 0.49876000 0.51345300', structure)
        self.assertNotIn(' Co ', structure)


if __name__ == '__main__':
    unittest.main()
