#!/bin/bash

echo "🎬 Day 46 Demo: Notification Preferences System"
echo "=============================================="

echo "📱 Demo Instructions:"
echo ""
echo "1. Open browser to http://localhost:3000"
echo "2. Create a new user or select existing user"
echo "3. Configure notification preferences:"
echo "   - Set channel priorities (email, SMS, push, in-app)"
echo "   - Configure quiet hours with timezone"
echo "   - Create escalation rules for different categories"
echo "4. Test the preferences with the notification tester"
echo "5. Try different notification types and priorities"
echo ""
echo "🔍 Key Features to Test:"
echo "• Channel prioritization affects delivery order"
echo "• Quiet hours block notifications (except exceptions)"
echo "• Escalation rules define retry behavior"
echo "• Real-time preference processing simulation"
echo ""
echo "🏆 Success Criteria:"
echo "✅ User can create and modify preferences"  
echo "✅ Channel priorities are respected"
echo "✅ Quiet hours block appropriate notifications"
echo "✅ Escalation rules are applied correctly"
echo "✅ Testing simulation shows preference processing"
echo ""
echo "Press any key to open the application..."
read

if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:3000
elif command -v open > /dev/null; then
    open http://localhost:3000
else
    echo "Please open http://localhost:3000 in your browser"
fi
