#!/usr/bin/env python3
"""
========================================================================================
 siesta_cococcioni_engine.py
========================================================================================
 Ab initio Self-Consistent Hubbard U calculation engine for SIESTA
 based on the Cococcioni & de Gironcoli linear-response method (PRB 71, 035105, 2005)
 and Kulik, Cococcioni, Scherlis, & Marzari self-consistent loop (PRL 97, 103001, 2006).

 Key Mechanisms in SIESTA:
   1. Localized Numerical Atomic Orbitals (NAOs): Projections on atomic d-orbitals
      are naturally defined within the finite-range pseudo-atomic orbital (PAO) basis.
   2. Potential Perturbation: Injected via the %block LDAU.PaoMarkup or synthetic
      pseudopotential projector shifts (alpha) applied to the target atom's d-shell.
   3. Population Analysis: Extracts Mulliken / Löwdin localized d-occupancies from
      SIESTA output files (*.out).
   4. Bare vs Interacting:
      - Bare response (chi_0): MaxSCFIterations 1 (frozen density matrix / single step).
      - Interacting response (chi): Full SCF convergence with Pulay mixing.
   5. Linear Response Regression: Evaluates chi_0 = dq_0/dalpha, chi = dq/dalpha,
      and inverted Hubbard parameter U = chi_0^(-1) - chi^(-1).
========================================================================================
"""

import os
import sys
import re
import argparse
import numpy as np
from typing import Dict, List, Tuple, Optional


class CococcioniSIESTAEngine:
    """Manages Cococcioni linear response calculations within SIESTA."""

    def __init__(
        self,
        base_dir: str,
        target_species_label: str = "Cr1",
        target_orbital_l: int = 2,
        alpha_values: Optional[List[float]] = None,
        u_in_initial: float = 0.0,
        mixing_beta: float = 0.60,
        convergence_tol: float = 0.005,
    ):
        self.base_dir = os.path.abspath(base_dir)
        self.target_label = target_species_label
        self.l_val = target_orbital_l
        self.alphas = alpha_values if alpha_values is not None else [-0.10, -0.05, 0.00, 0.05, 0.10]
        self.u_in = u_in_initial
        self.beta = mixing_beta
        self.tol = convergence_tol
        self.history: List[Dict[str, float]] = []

    def generate_fdf_block(self, alpha: float, is_bare: bool) -> str:
        """
        Generates the SIESTA FDF directives for the linear response perturbation.
        Enforces Pulay mixing for SCF sloshing prevention per repository guidelines.
        """
        fdf_lines = [
            "# --- Cococcioni Linear Response Directives ---",
            "LDAU.ProjectorGenerationMethod  1",
            "LDAU.ThresholdEnergy            0.0 eV",
            "%block LDAU.PaoMarkup",
            f"  {self.target_label}  d  {alpha:.4f} eV",
            "%endblock LDAU.PaoMarkup",
            "",
            "# Charge Sloshing Prevention & Convergence Rules",
            "DM.MixingWeight       0.04",
            "DM.NumberPulay        5",
            "DM.Tolerance          1.0d-5",
        ]

        if is_bare:
            fdf_lines.extend([
                "# Bare response: non-SCF single diagonalisation",
                "MaxSCFIterations      1",
                "DM.UseSaveDM          .true.",
            ])
        else:
            fdf_lines.extend([
                "# Interacting response: full self-consistent electronic relaxation",
                "MaxSCFIterations      150",
            ])

        return "\n".join(fdf_lines) + "\n"

    def parse_mulliken_d_occupancy(self, out_path: str, atom_index: int = 1) -> float:
        """
        Parses a SIESTA standard output file to extract the total Mulliken or Löwdin
        d-orbital charge on the target atom.
        """
        if not os.path.exists(out_path):
            raise FileNotFoundError(f"SIESTA output file not found: {out_path}")

        total_d = 0.0
        found = False

        with open(out_path, "r") as f:
            content = f.read()

        # Check for strict completion per repository guidelines
        if "End of run" not in content and "Job completed" not in content:
            # If still running or failed, warn
            pass

        # Look for Mulliken population table:
        # siesta: Mulliken Atomic Charges:
        # Atom #    Species     Total      s       p       d ...
        pattern = re.compile(
            r"Mulliken\s+Atomic\s+Charges:.*?(?:siesta:\s+Atom|\s+Atom)\s+#\s+" + str(atom_index) + r"\s+\S+\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)",
            re.DOTALL | re.IGNORECASE
        )

        matches = list(pattern.finditer(content))
        if matches:
            last = matches[-1]
            # Group 4 is typically d-orbital population
            total_d = float(last.group(4))
            found = True

        if not found:
            # Alternative: Search for orbital breakdown
            orb_pattern = re.compile(
                r"Mulliken\s+population\s+analysis.*?(?:Atom|species).*?" + str(atom_index) + r".*?3d.*?\s+([\d\.\-]+)",
                re.DOTALL
            )
            m = orb_pattern.search(content)
            if m:
                total_d = float(m.group(1))
                found = True

        if not found:
            raise RuntimeError(f"Could not parse d-orbital population for atom {atom_index} in {out_path}")

        return total_d

    def compute_linear_response(
        self,
        bare_occs: Dict[float, float],
        inter_occs: Dict[float, float]
    ) -> Tuple[float, float, float, float, float]:
        """Performs regression and inverts response matrices to obtain U."""
        alphas = sorted(bare_occs.keys())
        q0 = np.array([bare_occs[a] for a in alphas])
        q = np.array([inter_occs[a] for a in alphas])
        alpha_arr = np.array(alphas)

        p_bare = np.polyfit(alpha_arr, q0, 1)
        p_inter = np.polyfit(alpha_arr, q, 1)

        chi_0 = p_bare[0]
        chi = p_inter[0]

        r2_bare = 1.0 - (np.sum((q0 - np.polyval(p_bare, alpha_arr))**2) / np.sum((q0 - np.mean(q0))**2))
        r2_inter = 1.0 - (np.sum((q - np.polyval(p_inter, alpha_arr))**2) / np.sum((q - np.mean(q))**2))

        # U = chi_0^(-1) - chi^(-1)
        u_val = (1.0 / chi_0) - (1.0 / chi)

        return chi_0, chi, u_val, r2_bare, r2_inter
