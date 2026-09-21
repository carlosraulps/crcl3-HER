#!/bin/bash
# run_monitor_relax_isif3.sh
# Automated VASP submission and monitor script for CrCl3 1x1 ISIF=3 LATTICE_CONSTRAINTS (U = 0 .. 6 eV)

PARTITION="batch"
USER_NAME=$(whoami)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRATCH_ROOT="/home/cr/scratch_vasp/relax-crcl3-i3-dvw-u"
U_VALUES=(0 1 2 3 4 5 6)

ACTIVE_JOBS=$(squeue -u "$USER_NAME" -h -o "%j" 2>/dev/null)

echo "================================================================================"
echo " 🚀 VASP Job Automation & Monitor: relax-crcl3-i3-dvw-u (Partition: $PARTITION) "
echo "================================================================================"
printf "%-10s | %-18s | %-18s | %-20s\n" "Folder" "Job Name" "Status" "Job ID/Info"
echo "--------------------------------------------------------------------------------"

submitted_count=0
running_count=0
completed_count=0
failed_count=0

for u in "${U_VALUES[@]}"; do
    target_dir="$SCRIPT_DIR/U_${u}"
    scratch_dir="$SCRATCH_ROOT/U_${u}"
    job_name="CrCl3_i3_U_${u}"
    
    if [ ! -d "$target_dir" ]; then
        printf "%-10s | %-18s | %-18s | %-20s\n" "U_${u}" "$job_name" "⚠️ Dir Missing" "-"
        ((failed_count++))
        continue
    fi
    
    # 1. Inputs check in target directory
    missing=()
    for f in INCAR POSCAR POTCAR KPOINTS job.sh; do
        if [ ! -f "$target_dir/$f" ]; then
            missing+=("$f")
        fi
    done
    if [ ${#missing[@]} -gt 0 ]; then
        printf "%-10s | %-18s | %-18s | %-20s\n" "U_${u}" "$job_name" "❌ Missing Inputs" "${missing[*]}"
        ((failed_count++))
        continue
    fi
    
    # 2. Check if active in SLURM
    if echo "$ACTIVE_JOBS" | grep -Fqx "$job_name" &>/dev/null; then
        job_info=$(squeue -u "$USER_NAME" --name "$job_name" -h -o "%A %T %M" 2>/dev/null | head -n 1)
        printf "%-10s | %-18s | %-18s | %-20s\n" "U_${u}" "$job_name" "⏳ Active/Queued" "$job_info"
        ((running_count++))
        continue
    fi
    
    # 3. Check if completed in project directory (or sync if completed in scratch)
    outcar="$target_dir/OUTCAR"
    scratch_outcar="$scratch_dir/OUTCAR"
    
    if [ -f "$scratch_outcar" ] && grep -q "General timing and accounting" "$scratch_outcar" 2>/dev/null; then
        cp -u "$scratch_dir"/{OUTCAR,CONTCAR,EIGENVAL,DOSCAR,vasprun.xml,OSZICAR,vasp_run.log} "$target_dir"/ 2>/dev/null || true
    fi
    
    if [ -f "$outcar" ] && grep -q "General timing and accounting" "$outcar" 2>/dev/null; then
        toten=$(grep "free  energy   TOTEN" "$outcar" 2>/dev/null | tail -n 1 | awk "{print \$(NF-1)}")
        printf "%-10s | %-18s | %-18s | %-20s\n" "U_${u}" "$job_name" "✅ Completed" "TOTEN: ${toten} eV"
        ((completed_count++))
        continue
    fi
    
    # 4. Prepare scratch directory and submit job via sbatch with -D $scratch_dir
    mkdir -p "$scratch_dir"
    cp -u "$target_dir"/{INCAR,POSCAR,POTCAR,KPOINTS,job.sh} "$scratch_dir"/ 2>/dev/null
    chmod +x "$scratch_dir/job.sh"
    
    submit_out=$(sbatch -p "$PARTITION" -J "$job_name" -D "$scratch_dir" "$scratch_dir/job.sh" 2>&1)
    if [ $? -eq 0 ]; then
        job_id=$(echo "$submit_out" | awk "{print \$NF}")
        printf "%-10s | %-18s | %-18s | %-20s\n" "U_${u}" "$job_name" "🚀 Submitted" "SLURM ID: $job_id"
        ((submitted_count++))
    else
        err_msg=$(echo "$submit_out" | head -n 1)
        printf "%-10s | %-18s | %-18s | %-20s\n" "U_${u}" "$job_name" "❌ Submit Failed" "$err_msg"
        ((failed_count++))
    fi
done

echo "--------------------------------------------------------------------------------"
echo "Summary: Completed: $completed_count | Active: $running_count | Submitted: $submitted_count | Failed/Pending: $failed_count"
echo "================================================================================"
