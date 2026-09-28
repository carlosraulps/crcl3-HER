#!/bin/bash
# Master Dispatch for 32-core Embedded In-Allocation Pipeline on Carbono
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo '=========================================================='
echo ' Dispatching 32-core Embedded Pipeline Jobs to Carbono'
echo '=========================================================='
echo '--> Submitting Co (clean)...'
cd "${BASE_DIR}/crcl3-2x2-co_emb-pipeline/clean"
sbatch job_carbono.sh
echo '--> Submitting Co (H_ads)...'
cd "${BASE_DIR}/crcl3-2x2-co_emb-pipeline/H_ads"
sbatch job_carbono.sh
echo '--> Submitting Fe (clean)...'
cd "${BASE_DIR}/crcl3-2x2-fe_emb-pipeline/clean"
sbatch job_carbono.sh
echo '--> Submitting Fe (H_ads)...'
cd "${BASE_DIR}/crcl3-2x2-fe_emb-pipeline/H_ads"
sbatch job_carbono.sh
echo '--> Submitting Ni (clean)...'
cd "${BASE_DIR}/crcl3-2x2-ni_emb-pipeline/clean"
sbatch job_carbono.sh
echo '--> Submitting Ni (H_ads)...'
cd "${BASE_DIR}/crcl3-2x2-ni_emb-pipeline/H_ads"
sbatch job_carbono.sh
echo 'All 6 pipeline jobs submitted to nanotubo!'
