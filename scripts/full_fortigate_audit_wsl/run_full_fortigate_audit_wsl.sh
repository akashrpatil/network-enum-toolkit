#!/bin/bash
# ------------------------------------------------------------
# FortiGate CIS Audit Automation (cfg + conf)
# Fully stable version - Handles empty/missing/failed audits
# ------------------------------------------------------------

CONFIG_DIR="$(pwd)"
REPORT_DIR="${CONFIG_DIR}/combined_outputs"
mkdir -p "$REPORT_DIR"

echo "[*] Starting FortiGate CIS audits under WSL..."
echo ""

# ---------------------------
# STEP 1: Run individual audits
# ---------------------------
shopt -s nullglob
for cfg_file in "$CONFIG_DIR"/*.cfg "$CONFIG_DIR"/*.conf; do
    [ -e "$cfg_file" ] || continue
    base_name=$(basename "$cfg_file")
    base_name="${base_name%.*}"
    device_dir="${REPORT_DIR}/${base_name}"
    mkdir -p "$device_dir"

    txt_output="${device_dir}/${base_name}_output.txt"
    html_output="${device_dir}/${base_name}_output.html"

    echo "[*] Auditing: $base_name"
    ./fortigate_cis_audit.sh "$cfg_file" > "$txt_output" 2>&1
    dos2unix "$txt_output" 2>/dev/null

    # Check if audit produced PASS/FAIL lines
    if ! grep -qE "PASS:|FAIL:|Manual:" "$txt_output"; then
        echo "[!] No CIS results found in $base_name (possibly invalid config or skipped)."
        echo "NO RESULTS FOUND" > "$txt_output"
    fi

    # --- Individual HTML ---
    {
        echo "<html><head><style>
        body { font-family: Arial; margin:20px; }
        table { border-collapse: collapse; width:100%; }
        th, td { border:1px solid #ccc; padding:6px; text-align:left; }
        th { background:#f2f2f2; }
        .pass { background:#c6efce; }
        .fail { background:#ffc7ce; }
        .manual { background:#ffeb9c; }
        </style></head><body>"
        echo "<h2>FortiGate CIS Audit Report - $base_name</h2>"
        echo "<table><tr><th>Benchmark</th><th>Result</th></tr>"

        grep -E "^[0-9]{4}-[0-9]{2}-[0-9]{2}.*(PASS|FAIL|Manual):" "$txt_output" | while IFS= read -r line; do
            result=$(echo "$line" | sed -E 's/.*- ([A-Z][A-Z]+):.*/\1/')
            bench=$(echo "$line" | sed -E 's/.*- [A-Z]+:[[:space:]]*//')
            color=""; icon=""
            if [[ "$result" == "PASS" ]]; then color="pass"; icon="✅"
            elif [[ "$result" == "FAIL" ]]; then color="fail"; icon="❌"
            elif [[ "$result" =~ [Mm]anual ]]; then color="manual"; icon="🟨"
            fi
            echo "<tr class='$color'><td>${bench}</td><td>${icon} ${result}</td></tr>"
        done

        # If no results
        if ! grep -qE "PASS:|FAIL:|Manual:" "$txt_output"; then
            echo "<tr><td colspan='2'><i>No CIS results found for this device.</i></td></tr>"
        fi

        echo "</table></body></html>"
    } > "$html_output"

    echo "[+] Completed: $base_name → $device_dir"
done

echo ""
echo "[✔] All individual audits completed. Building combined summary..."

# ---------------------------
# STEP 2: Build Combined Dashboard
# ---------------------------
HTML_REPORT="${REPORT_DIR}/fortigate_audit_summary.html"
mapfile -t OUTPUT_FILES < <(find "$REPORT_DIR" -type f -name "*_output.txt" -print0 | xargs -0 -n1 echo | sort)

if [ ${#OUTPUT_FILES[@]} -eq 0 ]; then
    echo "[!] No audit outputs found. Exiting."
    exit 1
fi

{
    echo "<html><head><style>
    body { font-family: Arial; margin:20px; }
    table { border-collapse: collapse; width:100%; font-size:14px; }
    th, td { border:1px solid #ccc; padding:6px; text-align:center; }
    th { background:#f2f2f2; }
    .pass { background:#c6efce; }
    .fail { background:#ffc7ce; }
    .manual { background:#ffeb9c; }
    </style></head><body>"
    echo "<h1>FortiGate CIS Combined Compliance Dashboard</h1>"
    echo "<p>Generated on: $(date)</p>"
    echo "<table>"
    echo -n "<tr><th>Benchmark</th>"
    for file in "${OUTPUT_FILES[@]}"; do
        subdir=$(basename "$(dirname "$file")")
        echo -n "<th><a href='./${subdir}/${subdir}_output.html'>$subdir</a></th>"
    done
    echo "</tr>"
} > "$HTML_REPORT"

# Collect all unique benchmark descriptions
BENCHMARKS=$(grep -h -E "^[0-9]{4}-[0-9]{2}-[0-9]{2}.*(PASS|FAIL|Manual):" "${OUTPUT_FILES[@]}" | sed -E 's/.*- [A-Z]+:[[:space:]]*//' | sort -u)

# Add benchmark rows
while IFS= read -r bench; do
    [ -z "$bench" ] && continue
    echo -n "<tr><td>${bench}</td>" >> "$HTML_REPORT"

    for file in "${OUTPUT_FILES[@]}"; do
        if grep -qF "$bench" "$file"; then
            result=$(grep -F "$bench" "$file" | tail -1 | sed -E 's/.*- ([A-Z][A-Z]+):.*/\1/')
            icon=""; color=""
            if [[ "$result" == "PASS" ]]; then color="pass"; icon="✅ PASS"
            elif [[ "$result" == "FAIL" ]]; then color="fail"; icon="❌ FAIL"
            elif [[ "$result" =~ [Mm]anual ]]; then color="manual"; icon="🟨 Manual"
            else result="NA"; icon=""
            fi
            echo "<td class='$color'>$icon</td>" >> "$HTML_REPORT"
        else
            echo "<td><i>No Data</i></td>" >> "$HTML_REPORT"
        fi
    done

    echo "</tr>" >> "$HTML_REPORT"
done <<< "$BENCHMARKS"

# Add placeholder columns for configs with zero results
for file in "${OUTPUT_FILES[@]}"; do
    if ! grep -qE "PASS:|FAIL:|Manual:" "$file"; then
        name=$(basename "$(dirname "$file")")
        echo "<tr><td><i>$name had no CIS data.</i></td>" >> "$HTML_REPORT"
        for ((i=1; i<=${#OUTPUT_FILES[@]}; i++)); do echo "<td>NA</td>" >> "$HTML_REPORT"; done
        echo "</tr>" >> "$HTML_REPORT"
    fi
done

echo "</table></body></html>" >> "$HTML_REPORT"

echo ""
echo "[✔] Combined dashboard created successfully!"
echo "[🎯] Location: $HTML_REPORT"
echo "[🎯] Each device report is in its own folder inside $REPORT_DIR"
