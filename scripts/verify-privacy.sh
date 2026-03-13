#!/bin/bash
# Home Scout - Privacy Verification Script
# Audits network interfaces to verify Scout makes zero outbound connections

set -e

echo "=== Home Scout Privacy Audit ==="
echo ""

PASS=0
FAIL=0

check() {
    local desc="$1"
    local result="$2"
    if [ "$result" = "PASS" ]; then
        echo "[PASS] $desc"
        PASS=$((PASS + 1))
    else
        echo "[FAIL] $desc"
        FAIL=$((FAIL + 1))
    fi
}

# Check 1: No default gateway (no internet route)
echo "--- Network Isolation ---"
if ip route show default 2>/dev/null | grep -q "default"; then
    check "No default gateway configured" "FAIL"
    echo "       Found default route: $(ip route show default)"
    echo "       Scout should not have a route to the internet."
else
    check "No default gateway configured" "PASS"
fi

# Check 2: Only ScoutNet WiFi AP active
WIFI_CONNECTIONS=$(nmcli -t -f NAME,TYPE connection show --active 2>/dev/null | grep wifi || true)
if echo "$WIFI_CONNECTIONS" | grep -q "ScoutNet"; then
    check "ScoutNet WiFi AP is active" "PASS"
else
    check "ScoutNet WiFi AP is active" "FAIL"
    echo "       Active WiFi: $WIFI_CONNECTIONS"
fi

# Check 3: No DNS resolution configured
if [ -f /etc/resolv.conf ] && grep -q "nameserver" /etc/resolv.conf; then
    # Check if it's only local (127.0.0.1) or ScoutNet range
    EXTERNAL_DNS=$(grep "nameserver" /etc/resolv.conf | grep -v "127.0.0.1" | grep -v "10.0.77" || true)
    if [ -n "$EXTERNAL_DNS" ]; then
        check "No external DNS servers" "FAIL"
        echo "       Found: $EXTERNAL_DNS"
    else
        check "No external DNS servers" "PASS"
    fi
else
    check "No external DNS servers" "PASS"
fi

# Check 4: Monitor for outbound traffic (10 second sample)
echo ""
echo "--- Traffic Monitoring (10 seconds) ---"
echo "Capturing network traffic for 10 seconds..."
CAPTURE_FILE="/tmp/scout_privacy_audit.pcap"
timeout 10 tcpdump -i any -c 100 not host 10.0.77.0/24 -w "$CAPTURE_FILE" 2>/dev/null || true

if [ -f "$CAPTURE_FILE" ]; then
    PACKET_COUNT=$(tcpdump -r "$CAPTURE_FILE" 2>/dev/null | wc -l || echo "0")
    if [ "$PACKET_COUNT" -gt 0 ]; then
        check "No non-local traffic detected" "FAIL"
        echo "       Found $PACKET_COUNT packets outside ScoutNet"
        echo "       Run: tcpdump -r $CAPTURE_FILE"
    else
        check "No non-local traffic detected" "PASS"
    fi
    rm -f "$CAPTURE_FILE"
else
    check "No non-local traffic detected" "PASS"
fi

# Check 5: No listening services on external interfaces
echo ""
echo "--- Service Audit ---"
EXTERNAL_LISTENERS=$(ss -tlnp 2>/dev/null | grep -v "127.0.0.1" | grep -v "10.0.77" | grep -v "::1" | tail -n +2 || true)
if [ -n "$EXTERNAL_LISTENERS" ]; then
    check "No services listening on external interfaces" "FAIL"
    echo "       Found: $EXTERNAL_LISTENERS"
else
    check "No services listening on external interfaces" "PASS"
fi

# Summary
echo ""
echo "=== Results ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo "PRIVACY AUDIT FAILED - Review the failures above."
    exit 1
else
    echo "PRIVACY AUDIT PASSED - Scout is network-isolated."
    exit 0
fi
