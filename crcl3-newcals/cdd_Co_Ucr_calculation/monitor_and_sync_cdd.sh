#!/bin/bash
set -e
echo "[$(date)] Monitoring 01_scf_complex on huk124 (Job 8329)..."
while true; do
  CONV=$(ssh huk "grep -E '(reached required accuracy|General timing and accounting)' /home/carlos/crcl3-newcals/cdd_Co_Ucr_calculation/01_scf_complex/OUTCAR 2>/dev/null || true")
  HAS_CHG=$(ssh huk "[ -s /home/carlos/crcl3-newcals/cdd_Co_Ucr_calculation/01_scf_complex/CHGCAR ] && echo yes || echo no")
  RUNNING=$(ssh huk "squeue -j 8329 -h | wc -l")
  
  if [ -n "$CONV" ] && [ "$HAS_CHG" = "yes" ]; then
    echo "[$(date)] 01_scf_complex COMPLETED/CONVERGED on Huk!"
    break
  fi
  
  if [ "$RUNNING" -eq 0 ] && [ "$HAS_CHG" = "yes" ]; then
    echo "[$(date)] Job 8329 finished and CHGCAR exists!"
    break
  fi
  
  sleep 8
done

echo "[$(date)] Executing CDD processing on Huk..."
ssh huk "/home/carlos/offline_python/bin/python3 /home/carlos/crcl3-newcals/cdd_Co_Ucr_calculation/process_cdd_ucr.py"

echo "[$(date)] Syncing results to Arch..."
mkdir -p /home/cr/simulations/crcl3-HER/crcl3-newcals/cdd_Co_Ucr_calculation/04_cdd_output
rsync -avz huk:/home/carlos/crcl3-newcals/cdd_Co_Ucr_calculation/04_cdd_output/ /home/cr/simulations/crcl3-HER/crcl3-newcals/cdd_Co_Ucr_calculation/04_cdd_output/
echo "[$(date)] ALL CDD PROCESSING COMPLETED SUCCESSFULLY!"
