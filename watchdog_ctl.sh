#!/bin/bash
# ==============================================================================
# VASP WATCHDOG & ELECTRICAL FAULT CONTROLLER (systemd user service wrapper)
# ==============================================================================

SERVICE_NAME="vasp-watchdog.service"
DAEMON_SCRIPT="/home/juan/Carlos/vasp_watchdog.py"
LOG_FILE="/home/juan/Carlos/watchdog.log"

case "$1" in
    start)
        systemctl --user start "$SERVICE_NAME"
        echo "[WATCHDOG] Started systemd service: $SERVICE_NAME"
        systemctl --user status "$SERVICE_NAME" --no-pager
        ;;
    stop)
        systemctl --user stop "$SERVICE_NAME"
        echo "[WATCHDOG] Stopped systemd service: $SERVICE_NAME"
        ;;
    restart)
        systemctl --user restart "$SERVICE_NAME"
        echo "[WATCHDOG] Restarted systemd service: $SERVICE_NAME"
        ;;
    status)
        systemctl --user status "$SERVICE_NAME" --no-pager
        echo ""
        echo "--- Recent Log Entries ($LOG_FILE) ---"
        tail -n 10 "$LOG_FILE" 2>/dev/null
        ;;
    emergency-stop)
        echo "=========================================================="
        echo " [ALERT] BROADCASTING GRACEFUL STOP TO ALL VASP RUNS"
        echo "=========================================================="
        python3 "$DAEMON_SCRIPT" --emergency-stop
        ;;
    log)
        tail -f "$LOG_FILE"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|emergency-stop|log}"
        exit 1
        ;;
esac
