#!/usr/bin/env bash
#
# fetch_proxies.sh — Fetch proxy list, validate proxies, and optionally
# fetch a URL through the first working one.
#
# Usage:
#     ./fetch_proxies.sh --list [--country XX]
#     ./fetch_proxies.sh [options] host1:port1 host2:port2 ...
#
# Modes:
#     --list             Fetch and print raw JSON from the Browsec API.
#                        The agent parses it (any LLM can read JSON).
#     (no --list)        Validate the given host:port proxies.
#
# Validation options:
#     --timeout S        Validation timeout per proxy in seconds (default 90)
#     --all              Print all working proxies, not just the first one
#     --url URL          Fetch URL through the first working proxy and print
#                        the response body
#     --url-timeout S    Timeout for --url fetch in seconds (default 60)
#
# Exit code is always 0. Check stdout for results.
#
# Requires: curl

set -uo pipefail

API_URL="https://browsec.com/api/v1/servers?uc=ru&stdomains=1"
TIMEOUT=29
URL_TIMEOUT=60
ALL=false
URL=""
LIST=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --list)        LIST=true; shift ;;
        --timeout)     TIMEOUT="$2"; shift 2 ;;
        --url-timeout) URL_TIMEOUT="$2"; shift 2 ;;
        --all)         ALL=true; shift ;;
        --url)         URL="$2"; shift 2 ;;
        -*)            echo "Unknown option: $1" >&2; shift ;;
        *)             break ;;
    esac
done

# --- List mode: fetch API and print JSON ---
if $LIST; then
    RAW=$(curl -sfSL --max-time 15 -H "Accept: application/json" "$API_URL" 2>/dev/null) || true
    if [[ -z "$RAW" ]]; then
        echo "{}"
        exit 0
    fi
    echo "$RAW"
    exit 0
fi

# --- Validation mode ---
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 --list [--country XX]" >&2
    echo "       $0 [--url URL] host1:port1 host2:port2 ..." >&2
    exit 0
fi

check_proxy() {
    local proxy="$1"
    local status
    status=$(curl -x "https://${proxy}" -sfSL --max-time "$TIMEOUT" \
        -o /dev/null -w "%{http_code}" "http://httpbin.org/ip" 2>/dev/null) || true
    [[ "$status" == "200" ]]
}

for proxy in "$@"; do
    if check_proxy "$proxy"; then
        if [[ -n "$URL" ]]; then
            curl -x "https://${proxy}" -sfSL --max-time "$URL_TIMEOUT" "$URL" 2>/dev/null || true
            exit 0
        fi
        echo "$proxy"
        $ALL || exit 0
    fi
done

exit 0
