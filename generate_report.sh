#!/bin/bash

mkdir -p reports

REPORT="reports/system_report_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "=================================="
    echo "       SYSTEM INFORMATION REPORT"
    echo "=================================="

    echo ""
    echo "Date: $(date)"
    echo "Username: $(whoami)"
    echo "System Name: $(hostname)"
    echo "Operating System:"
    uname -a

    echo ""
    echo "UPTIME:"
    uptime

    echo ""
    echo "MEMORY USAGE:"
    free -h

    echo ""
    echo "DISK USAGE:"
    df -h

    echo ""
    echo "=================================="
    echo "          END OF REPORT"
    echo "=================================="

} > "$REPORT"

echo "Report generated successfully!"
echo "Saved at: $REPORT"