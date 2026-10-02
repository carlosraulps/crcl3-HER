#!/bin/bash
# Submit all U_all=3.29 calculations to Carbono
echo 'Submitting embedded/Co/clean on Carbono...'
(cd /home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/embedded/Co/clean && sbatch job_carbono.sh)
echo 'Submitting embedded/Co/H_ads on Carbono...'
(cd /home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/embedded/Co/H_ads && sbatch job_carbono.sh)
echo 'Submitting embedded/Fe/clean on Carbono...'
(cd /home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/embedded/Fe/clean && sbatch job_carbono.sh)
echo 'Submitting embedded/Fe/H_ads on Carbono...'
(cd /home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/embedded/Fe/H_ads && sbatch job_carbono.sh)
echo 'Submitting embedded/Ni/clean on Carbono...'
(cd /home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/embedded/Ni/clean && sbatch job_carbono.sh)
echo 'Submitting embedded/Ni/H_ads on Carbono...'
(cd /home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/embedded/Ni/H_ads && sbatch job_carbono.sh)
echo 'Submitting adsorbed/Co/clean on Carbono...'
(cd /home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/adsorbed/Co/clean && sbatch job_carbono.sh)
echo 'Submitting adsorbed/Co/H_ads on Carbono...'
(cd /home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/adsorbed/Co/H_ads && sbatch job_carbono.sh)
echo 'Submitting adsorbed/Fe/clean on Carbono...'
(cd /home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/adsorbed/Fe/clean && sbatch job_carbono.sh)
echo 'Submitting adsorbed/Fe/H_ads on Carbono...'
(cd /home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/adsorbed/Fe/H_ads && sbatch job_carbono.sh)
echo 'Submitting adsorbed/Ni/clean on Carbono...'
(cd /home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/adsorbed/Ni/clean && sbatch job_carbono.sh)
echo 'Submitting adsorbed/Ni/H_ads on Carbono...'
(cd /home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/adsorbed/Ni/H_ads && sbatch job_carbono.sh)
