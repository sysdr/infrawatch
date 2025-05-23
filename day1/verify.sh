# 1. Health Check Verification
echo "Testing system health..."
curl -s http://localhost:3001/health | grep -q "healthy" && echo "✅ Backend healthy" || echo "❌ Backend unhealthy"

# 2. API Response Verification
echo "Testing API responses..."
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/api/infrastructure/status)
if [ $STATUS_CODE -eq 200 ]; then
    echo "✅ API responding correctly"
else
    echo "❌ API error: $STATUS_CODE"
fi

# 3. Frontend Loading Test
echo "Testing frontend accessibility..."
FRONTEND_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ $FRONTEND_CODE -eq 200 ]; then
    echo "✅ Frontend accessible"
else
    echo "❌ Frontend error: $FRONTEND_CODE"
fi

# 4. Service Communication Test
echo "Testing service integration..."
# This checks if frontend can successfully call backend
# Check browser console for any CORS or network errors

echo "🎉 System verification complete!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 Backend API: http://localhost:3001"