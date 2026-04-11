#!/bin/bash

# Verification script to ensure no browser storage is used in frontend
# Run this before deployment to verify compliance

echo "🔍 Verifying no browser storage usage in VoiceForward frontend..."
echo ""

ERRORS=0

# Check for localStorage
echo "Checking for localStorage usage..."
if grep -r "localStorage" src/ --exclude-dir=node_modules 2>/dev/null | grep -v "DATA_PRIVACY.md"; then
    echo "❌ FAIL: localStorage found in source code"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: No localStorage usage"
fi
echo ""

# Check for sessionStorage
echo "Checking for sessionStorage usage..."
if grep -r "sessionStorage" src/ --exclude-dir=node_modules 2>/dev/null | grep -v "DATA_PRIVACY.md"; then
    echo "❌ FAIL: sessionStorage found in source code"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: No sessionStorage usage"
fi
echo ""

# Check for IndexedDB
echo "Checking for IndexedDB usage..."
if grep -r -E "IndexedDB|indexedDB|openDatabase" src/ --exclude-dir=node_modules 2>/dev/null | grep -v "DATA_PRIVACY.md"; then
    echo "❌ FAIL: IndexedDB found in source code"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: No IndexedDB usage"
fi
echo ""

# Check for cookie setting (document.cookie =)
echo "Checking for cookie manipulation..."
if grep -r "document\.cookie\s*=" src/ --exclude-dir=node_modules 2>/dev/null; then
    echo "❌ FAIL: Cookie manipulation found in source code"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: No cookie manipulation"
fi
echo ""

# Check for persistence libraries in package.json
echo "Checking for persistence libraries..."
if grep -E "redux-persist|zustand.*persist|localforage|dexie|pouchdb" package.json 2>/dev/null; then
    echo "❌ FAIL: Persistence library found in package.json"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: No persistence libraries"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED - No browser storage detected"
    echo "Frontend is compliant with zero-storage policy"
    exit 0
else
    echo "❌ $ERRORS CHECK(S) FAILED"
    echo "Review and remove browser storage usage before deployment"
    exit 1
fi
