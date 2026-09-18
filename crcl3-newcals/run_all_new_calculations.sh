#!/bin/bash
# run_all_new_calculations.sh
# Master submission and status monitor for all new revision calculations (DFT_D3, DFT_U, Freq).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================================================"
echo "                     🚀 MASTER VASP REVISION RUNNER                             "
echo "================================================================================"
echo ""

for suite in DFT_D3 DFT_U Freq; do
    runner="$SCRIPT_DIR/$suite/run_monitor_vasp.sh"
    if [ -f "$runner" ]; then
        bash "$runner"
        echo ""
    fi
done

echo "Master scan complete."
