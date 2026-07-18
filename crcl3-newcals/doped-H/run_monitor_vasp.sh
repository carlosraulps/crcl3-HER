#!/bin/bash
# run_monitor_vasp.sh
# Automated VASP job submission and status monitoring script for doped-H calculations.
# Submits all calculations to the 'normal' partition with safety checks.

# ----------------- Configuration -----------------
PARTITION="normal"
USER_NAME=$(whoami)

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define search folders relative to script location
SEARCH_PATHS=(
    "adsorbed/Co"
    "adsorbed/Fe"
    "adsorbed/NI"
    "embeded/Co"
    "embeded/Fe"
    "embeded/NI"
)
# -------------------------------------------------

# Fetch currently active job names from SLURM to prevent double-submitting
ACTIVE_JOBS=$(squeue -u "$USER_NAME" -h -o "%j" 2>/dev/null)

echo "=========================================================="
echo " 🚀 VASP Job Automation & Status Monitor (Partition: $PARTITION) "
echo "=========================================================="
printf "%-18s | %-12s | %-16s | %-12s\n" "Directory" "Job Name" "Status" "Job ID/Info"
echo "----------------------------------------------------------"

submitted_count=0
running_count=0
completed_count=0
failed_count=0

for rel_path in "${SEARCH_PATHS[@]}"; do
    target_dir="$SCRIPT_DIR/$rel_path"
    
    # Check if target directory exists
    if [ ! -d "$target_dir" ]; then
        printf "%-18s | %-12s | %-16s | %-12s\n" "$rel_path" "N/A" "⚠️ Dir Missing" "-"
        ((failed_count++))
        continue
    fi
    
    # Generate unique, descriptive job name based on system type
    dir_name=$(basename "$rel_path")
    parent_name=$(basename "$(dirname "$rel_path")")
    if [ "$parent_name" = "adsorbed" ]; then
        job_name="H_ads_${dir_name}"
    else
        job_name="H_emb_${dir_name}"
    fi
    
    # 1. Pre-flight inputs verification
    missing_files=()
    for file in INCAR POSCAR POTCAR KPOINTS job.sh; do
        if [ ! -f "$target_dir/$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        # Join missing files with commas
        missing_str=$(IFS=,; echo "${missing_files[*]}")
        printf "%-18s | %-12s | %-16s | %-12s\n" "$rel_path" "$job_name" "❌ Missing Inputs" "$missing_str"
        ((failed_count++))
        continue
    fi
    
    # 2. Check if job is already running or queued in SLURM
    is_active=false
    if echo "$ACTIVE_JOBS" | grep -Fqx "$job_name" &>/dev/null; then
        is_active=true
    fi
    
    if [ "$is_active" = true ]; then
        # Retrieve actual Job ID for active job
        job_id=$(squeue -u "$USER_NAME" -name "$job_name" -h -o "%A" 2>/dev/null | head -n 1)
        printf "%-18s | %-12s | %-16s | %-12s\n" "$rel_path" "$job_name" "⏳ Active/Queued" "$job_id"
        ((running_count++))
        continue
    fi
    
    # 3. Check if calculation completed successfully in a previous run
    outcar_file="$target_dir/OUTCAR"
    if [ -f "$outcar_file" ] && grep -q "General timing" "$outcar_file" 2>/dev/null; then
        printf "%-18s | %-12s | %-16s | %-12s\n" "$rel_path" "$job_name" "✅ Completed" "OUTCAR Ok"
        ((completed_count++))
        continue
    fi
    
    # 4. Submit the job using sbatch --chdir/--D flag
    submit_out=$(sbatch -p "$PARTITION" -J "$job_name" -D "$target_dir" "$target_dir/job.sh" 2>&1)
    if [ $? -eq 0 ]; then
        job_id=$(echo "$submit_out" | awk '{print $NF}')
        printf "%-18s | %-12s | %-16s | %-12s\n" "$rel_path" "$job_name" "🚀 Submitted" "$job_id"
        ((submitted_count++))
    else
        printf "%-18s | %-12s | %-16s | %-12s\n" "$rel_path" "$job_name" "❌ Submit Failed" "Error"
        ((failed_count++))
    fi
    
done

echo "----------------------------------------------------------"
echo "Summary: Completed: $completed_count | Active: $running_count | Submitted: $submitted_count | Failed/Missing: $failed_count"
echo "=========================================================="
