# Repository Guidelines & Preferences

- Always use the `master` branch (never `main`) for all git branches, operations, commits, and remote pushes.
- Use the Python environment at `~/venvs/research/bin/python3` for tasks requiring specialized packages like ASE.

## Publication Plotting & Layout Anti-Collision Policy
- **Zero-Overlap Mandate:** Never produce plots with overlapping text annotations, labels, legends, or colliding bars.
- **Adaptive Headroom:** Always compute dynamic y-limits ($y_{\max} = \max(\text{data}) + 0.25 \times \Delta y$) to ensure annotations above bars/lines never clip the upper axis or collide with legends.
- **Staggering & Smart Cards:** In dense bar charts or adjacent data points, use staggered vertical offsets and semi-transparent bounding cards (`facecolor='white', alpha=0.92, edgecolor='#cccccc'`) with `smart_plot_optimizer.py`.
- **Legend Placement:** Always place legends in the lowest-density quadrant with background framing.
