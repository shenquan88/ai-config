#!/bin/bash
# Keep the WorkBuddy credit-pool request-rewrite proxy alive (WSL-local, 127.0.0.1:7866 -> Windows 7863).
# Why it exists: see WORKBUDDY_MODELS.md "兼容性代理" section. Started by cron every 2 minutes and at boot.
LOG=/home/dsh/.dsh/state/wb-pool-proxy.log
if pgrep -f '/home/dsh/bin/wb-pool-proxy.py' >/dev/null 2>&1; then exit 0; fi
nohup setsid python3 /home/dsh/bin/wb-pool-proxy.py >> "$LOG" 2>&1 &
sleep 1
pgrep -f '/home/dsh/bin/wb-pool-proxy.py' >/dev/null 2>&1 || echo "$(date -Is) keepalive: failed to start proxy" >> "$LOG"
