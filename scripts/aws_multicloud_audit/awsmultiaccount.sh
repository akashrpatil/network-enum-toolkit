#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# multi_account_exec.sh
# Run ANY AWS CLI command on multiple accounts with labels
#
# Usage:
#   ./multi_account_exec.sh "aws sts get-caller-identity"
#   ./multi_account_exec.sh "aws s3 ls"
# ============================================================

if [ $# -lt 1 ]; then
  echo "Usage: $0 \"<aws command>\""
  echo "Example: $0 \"aws sts get-caller-identity\""
  exit 1
fi

CMD="$1"

# ---------- Credential maps ----------
declare -A KEYS
declare -A SECRETS
declare -A LABELS

# Account 1
KEYS["acct1-ro"]="PUT ACCESS KEY"
SECRETS["acct1-ro"]="PUT SECRET KEY"
LABELS["acct1-ro"]="Account1 - ReadOnly"

# Account 2
KEYS["acct2-ro"]="PUT ACCESS KEY"
SECRETS["acct2-ro"]="PUT ACCESS KEY"
LABELS["acct2-ro"]="Account2 - AllAccessService"

# ============================================================

aws_with_creds() {
  local access_key="$1"
  local secret_key="$2"
  shift 2
  AWS_ACCESS_KEY_ID="$access_key" AWS_SECRET_ACCESS_KEY="$secret_key" $@
}

# Sort keys alphabetically for stable output
mapfile -t sorted_keys < <(printf "%s\n" "${!KEYS[@]}" | sort)

for key in "${sorted_keys[@]}"; do
  label="${LABELS[$key]}"
  access_key="${KEYS[$key]}"
  secret_key="${SECRETS[$key]}"

  echo "============================================================"
  echo "[$label]"
  echo "Running: $CMD"
  echo "------------------------------------------------------------"
  
  # Execute the user-supplied command with this account’s credentials
  if ! output=$(AWS_ACCESS_KEY_ID="$access_key" AWS_SECRET_ACCESS_KEY="$secret_key" bash -c "$CMD" 2>&1); then
    echo "❌ ERROR executing on $label:"
    echo "$output"
  else
    echo "$output"
  fi

  echo
done
