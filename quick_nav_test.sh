#!/bin/bash
# Quick navigation test script
echo "Testing key navigation routes..."
echo ""
for url in / /assets /add /users /suppliers /database /reports/inventory; do
    code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000$url)
    if [ "$code" = "200" ] || [ "$code" = "302" ]; then
        echo "✅ $url - OK ($code)"
    else
        echo "❌ $url - FAILED ($code)"
    fi
done
echo ""
echo "Navigation test complete!"
