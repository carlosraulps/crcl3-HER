#!/bin/bash
# ==============================================================================
#  SLURM MASTER RUNNER & TELEMETRY MONITOR FOR CrCl3 2x2 Co/Fe/Ni ADSORPTION
#  Tailored for Carbono Cluster (UFABC) - Partition: fulereno (64 CPUs / job)
# ==============================================================================
# Usage:
#   ./submit_carbono_2x2_tm_jobs.sh status                # Live telemetry & convergence matrix
#   ./submit_carbono_2x2_tm_jobs.sh test                  # Dry-run validation (sbatch --test-only)
#   ./submit_carbono_2x2_tm_jobs.sh submit-all            # Submit all 24 calculations
#   ./submit_carbono_2x2_tm_jobs.sh submit-unconverged    # Submit only non-converged & non-queued jobs
#   ./submit_carbono_2x2_tm_jobs.sh submit co             # Submit only Co jobs
#   ./submit_carbono_2x2_tm_jobs.sh submit fe             # Submit only Fe jobs
#   ./submit_carbono_2x2_tm_jobs.sh submit ni             # Submit only Ni jobs
#   ./submit_carbono_2x2_tm_jobs.sh submit yes_vdw        # Submit only yes_vdw jobs
#   ./submit_carbono_2x2_tm_jobs.sh submit no_vdw         # Submit only no_vdw jobs
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_NAME="$(whoami)"
ACTION="${1:-status}"
FILTER="${2:-all}"

# Normalize aliases
if [[ "$ACTION" == "--test" || "$ACTION" == "--dry-run" ]]; then
    ACTION="test"
fi
if [[ "$ACTION" == "all" || ("$ACTION" == "submit" && "$FILTER" == "all") ]]; then
    ACTION="submit-all"
fi

# Query active Slurm jobs for current user
SQUEUE_DATA="$(squeue -u "$USER_NAME" -h -o "%i|%P|%j|%T" 2>/dev/null)"

echo "=========================================================================================================="
echo "   CARBONO HPC JOB MANAGER: CrCl3 2x2 Transition Metal Adsorption (Co / Fe / Ni, U = 0 eV)"
echo "   Host: $(hostname) | Partition: fulereno (64 CPUs/job) | User: $USER_NAME"
echo "   Mode: $ACTION | Target Filter: $FILTER | Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================================================================================="
printf "%-26s | %-18s | %-9s | %-5s | %-14s | %-9s | %-13s\n" \
       "System / Site" "Job Name" "Slurm" "Steps" "Energy (eV)" "Max Force" "Status"
echo "----------------------------------------------------------------------------------------------------------"

TOTAL=0
SUBMITTED=0
QUEUED=0
RUNNING=0
CONVERGED=0
STOPPED=0

for tm_dir in crcl3-2x2-co_ads-without-U crcl3-2x2-fe_ads-without-U crcl3-2x2-ni_ads-without-U; do
    tm_short=$(echo "$tm_dir" | cut -d'-' -f3 | cut -d'_' -f1)

    # Filter by element if specified
    if [[ "$FILTER" != "all" && "$FILTER" != "yes_vdw" && "$FILTER" != "no_vdw" ]]; then
        if [ "$FILTER" != "$tm_short" ]; then
            continue
        fi
    fi

    for vdw in no_vdw yes_vdw; do
        # Filter by vdw if specified
        if [ "$FILTER" = "yes_vdw" ] && [ "$vdw" != "yes_vdw" ]; then
            continue
        fi
        if [ "$FILTER" = "no_vdw" ] && [ "$vdw" != "no_vdw" ]; then
            continue
        fi

        for site in clean S1 S2 S3; do
            calc_dir="$SCRIPT_DIR/$tm_dir/$vdw/$site"
            short_path="${tm_short^^}/$vdw/$site"

            if [ ! -d "$calc_dir" ] || [ ! -f "$calc_dir/job.sh" ]; then
                continue
            fi
            ((TOTAL++))

            job_name=$(grep -m1 "^#SBATCH -J" "$calc_dir/job.sh" | awk '{print $NF}')
            
            # Check Slurm status
            slurm_entry=$(echo "$SQUEUE_DATA" | grep "|${job_name}|" | head -n 1)
            if [ -n "$slurm_entry" ]; then
                slurm_state=$(echo "$slurm_entry" | awk -F'|' '{print $4}')
                slurm_id=$(echo "$slurm_entry" | awk -F'|' '{print $1}')
                slurm_disp="${slurm_state:0:3} #$slurm_id"
                if [ "$slurm_state" = "RUNNING" ]; then
                    ((RUNNING++))
                else
                    ((QUEUED++))
                fi
            else
                slurm_disp="NONE"
            fi

            # Check Ionic Steps & Energy from OSZICAR
            steps=0
            energy="N/A"
            if [ -f "$calc_dir/OSZICAR" ]; then
                steps=$(grep "^  *[0-9]* F=" "$calc_dir/OSZICAR" 2>/dev/null | tail -n 1 | awk '{print $1}')
                [ -z "$steps" ] && steps=0
                energy=$(grep "^  *[0-9]* F=" "$calc_dir/OSZICAR" 2>/dev/null | tail -n 1 | awk '{print $3}')
                [ -z "$energy" ] && energy="N/A"
            fi

            # Check Maximum Force from OUTCAR
            max_force="N/A"
            if [ -f "$calc_dir/OUTCAR" ] && [ "$steps" -gt 0 ]; then
                max_force=$(awk '
                    /TOTAL-FORCE/ { flag=1; count=0; next }
                    flag && /-----------------------------------------------------------------------------------/ {
                        if (++count == 2) { flag=0 }
                        next
                    }
                    flag {
                        fx = ($4 < 0) ? -$4 : $4
                        fy = ($5 < 0) ? -$5 : $5
                        fz = ($6 < 0) ? -$6 : $6
                        f = sqrt(fx^2 + fy^2 + fz^2)
                        if (f > max_f) max_f = f
                    }
                    END { if (max_f > 0) printf "%.4f", max_f; else print "N/A" }
                ' "$calc_dir/OUTCAR" 2>/dev/null)
            fi

            # Determine Convergence State
            calc_status="NOT_SUBMITTED"
            if [ -f "$calc_dir/OUTCAR" ] && grep -q "reached required accuracy" "$calc_dir/OUTCAR" 2>/dev/null; then
                calc_status="CONVERGED"
                ((CONVERGED++))
            elif [ -n "$slurm_entry" ]; then
                calc_status="IN_PROGRESS"
            elif [ "$steps" -gt 0 ]; then
                calc_status="STOPPED"
                ((STOPPED++))
            fi

            printf "%-26s | %-18s | %-9s | %-5s | %-14s | %-9s | %-13s\n" \
                   "$short_path" "$job_name" "$slurm_disp" "$steps" "$energy" "$max_force" "$calc_status"

            # Execute submission actions
            if [ "$ACTION" = "test" ]; then
                cd "$calc_dir"
                test_msg=$(sbatch --test-only job.sh 2>&1 | head -n 1)
                echo "       └─ Test: $test_msg"
                cd "$SCRIPT_DIR"
            elif [ "$ACTION" = "submit-all" ]; then
                if [ "$calc_status" != "CONVERGED" ] && [ "$slurm_disp" = "NONE" ]; then
                    cd "$calc_dir"
                    sub_out=$(sbatch job.sh 2>&1)
                    echo "       └─ Submitted: $sub_out"
                    ((SUBMITTED++))
                    cd "$SCRIPT_DIR"
                fi
            elif [ "$ACTION" = "submit-unconverged" ]; then
                if [ "$calc_status" != "CONVERGED" ] && [ "$slurm_disp" = "NONE" ]; then
                    cd "$calc_dir"
                    sub_out=$(sbatch job.sh 2>&1)
                    echo "       └─ Submitted: $sub_out"
                    ((SUBMITTED++))
                    cd "$SCRIPT_DIR"
                fi
            elif [ "$ACTION" = "submit" ]; then
                if [ "$calc_status" != "CONVERGED" ] && [ "$slurm_disp" = "NONE" ]; then
                    cd "$calc_dir"
                    sub_out=$(sbatch job.sh 2>&1)
                    echo "       └─ Submitted: $sub_out"
                    ((SUBMITTED++))
                    cd "$SCRIPT_DIR"
                fi
            fi
        done
    done
done

echo "=========================================================================================================="
echo "Summary: Total: $TOTAL | Converged: $CONVERGED | Running: $RUNNING | Queued: $QUEUED | Stopped: $STOPPED | Submitted Now: $SUBMITTED"
echo "=========================================================================================================="
