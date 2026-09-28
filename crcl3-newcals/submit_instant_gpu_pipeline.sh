#!/bin/bash
# Master Dispatch for Instant GPU Node Calculations on Carbono
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo '=========================================================='
echo ' Dispatching Instant Jobs to metano (gn01) & etileno (gn04)'
echo '=========================================================='
echo '--> Submitting Co_emb (clean) to metano...'
cd "${BASE_DIR}/crcl3-2x2-co_emb-metano/clean"
sbatch job_carbono.sh

echo '--> Submitting Co_emb (H_ads) to metano...'
cd "${BASE_DIR}/crcl3-2x2-co_emb-metano/H_ads"
sbatch job_carbono.sh

echo '--> Submitting Fe_emb (clean) to etileno...'
cd "${BASE_DIR}/crcl3-2x2-fe_emb-metano/clean"
sbatch job_carbono.sh

echo '=========================================================='
echo ' All 3 instant pipeline jobs submitted!'
echo '=========================================================='
