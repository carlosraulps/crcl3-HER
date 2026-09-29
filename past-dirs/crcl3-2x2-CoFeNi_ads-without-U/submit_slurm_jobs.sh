#!/bin/bash
# ==============================================================================
#  SLURM MASTER RUNNER & STATUS MONITOR FOR CrCl3 2x2 Co/Fe/Ni ADSORPTION
# ==============================================================================
# Usage:
#   ./submit_slurm_jobs.sh status          # View status of all 24 calculations
#   ./submit_slurm_jobs.sh submit-all      # Submit all 24 jobs
#   ./submit_slurm_jobs.sh submit co       # Submit only Co jobs (8 calcs)
#   ./submit_slurm_jobs.sh submit fe       # Submit only Fe jobs (8 calcs)
#   ./submit_slurm_jobs.sh submit ni       # Submit only Ni jobs (8 calcs)
#   ./submit_slurm_jobs.sh submit yes_vdw  # Submit only yes_vdw (IVDW=12) jobs
#   ./submit_slurm_jobs.sh submit no_vdw   # Submit only no_vdw jobs
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_NAME="$(whoami)"
ACTION="${1:-status}"
FILTER="${2:-all}"

# Active SLURM jobs for this user
ACTIVE_JOBS="$(squeue -u "$USER_NAME" -h -o "%j" 2>/dev/null)"

echo "================================================================================"
echo "   SLURM JOB MANAGER: CrCl3 2x2 Co/Fe/Ni Adsorption Suite"
echo "================================================================================"
echo "Mode: $ACTION | Target Filter: $FILTER | User: $USER_NAME"
echo "--------------------------------------------------------------------------------"
printf "%-40s | %-16s | %-16s\n" "Calculation Directory" "Job Name" "Status"
echo "--------------------------------------------------------------------------------"

TOTAL=0
SUBMITTED=0
RUNNING=0
COMPLETED=0

for tm_dir in crcl3-2x2-co_ads-without-U crcl3-2x2-fe_ads-without-U crcl3-2x2-ni_ads-without-U; do
    tm_short=$(echo "$tm_dir" | cut -d'-' -f3 | cut -d'_' -f1)
    
    # Filter by metal if requested
    if [ "$FILTER" != "all" ] && [ "$FILTER" != "yes_vdw" ] && [ "$FILTER" != "no_vdw" ]; then
        if [ "$FILTER" != "$tm_short" ]; then
            continue
        fi
    fi

    for vdw in no_vdw yes_vdw; do
        # Filter by vdw if requested
        if [ "$FILTER" = "yes_vdw" ] && [ "$vdw" != "yes_vdw" ]; then
            continue
        fi
        if [ "$FILTER" = "no_vdw" ] && [ "$vdw" != "no_vdw" ]; then
            continue
        fi

        for site in clean S1 S2 S3; do
            calc_dir="$SCRIPT_DIR/$tm_dir/$vdw/$site"
            rel_path="$tm_dir/$vdw/$site"
            
            if [ ! -d "$calc_dir" ]; then
                continue
            fi
            ((TOTAL++))

            # Extract job name from job.sh
            job_name=$(grep "^#SBATCH -J" "$calc_dir/job.sh" | awk '{print $3}')
            
            # Check status
            status="Not Submitted"
            if [ -f "$calc_dir/OUTCAR" ] && grep -q "General timing and accounting informations" "$calc_dir/OUTCAR" 2>/dev/null; then
                status="COMPLETED"
                ((COMPLETED++))
            elif echo "$ACTIVE_JOBS" | grep -qw "$job_name"; then
                status="RUNNING"
                ((RUNNING++))
            elif [ -f "$calc_dir/vasp_run.log" ]; then
                status="FAILED/STOPPED"
            fi

            printf "%-40s | %-16s | %-16s\n" "$rel_path" "$job_name" "$status"

            # If action is submit-all or submit
            if [[ "$ACTION" == "submit"* ]]; then
                if [ "$status" = "RUNNING" ]; then
                    echo "  -> Skipped: Already running in SLURM queue."
                elif [ "$status" = "COMPLETED" ]; then
                    echo "  -> Skipped: Already completed."
                else
                    echo "  -> Submitting: sbatch job.sh"
                    (cd "$calc_dir" && sbatch job.sh)
                    ((SUBMITTED++))
                fi
            fi
        done
    done
done

echo "================================================================================"
echo "Summary: Total: $TOTAL | Completed: $COMPLETED | Running: $RUNNING | Submitted this run: $SUBMITTED"
echo "================================================================================"
