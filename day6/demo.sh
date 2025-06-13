#!/bin/bash

# Demo script to showcase the testing framework
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🎬 Testing Framework Demo${NC}"
echo "========================="

echo -e "${YELLOW}1️⃣  Running backend unit tests...${NC}"
cd backend
source venv/bin/activate
python -m pytest tests/unit/test_log_event.py::TestLogEvent::test_log_event_creation -v
python -m pytest tests/unit/test_log_event.py::TestLogEventFactory::test_create_single_log -v
python -m pytest tests/unit/test_log_event.py::TestLogEventFactory::test_error_scenario_generation -v
echo -e "${GREEN}✅ Backend unit tests passed${NC}"

echo ""
echo -e "${YELLOW}2️⃣  Testing data factories...${NC}"
python -c "
from tests.factories.log_event_factory import LogEventFactory
from src.models.log_event import LogLevel

# Test single log creation
log = LogEventFactory.build()
print(f'✅ Created log: {log.level} - {log.message[:50]}...')

# Test batch creation
logs = LogEventFactory.build_batch(3)
print(f'✅ Created batch of {len(logs)} logs')

# Test error scenario
error_logs = LogEventFactory.create_error_scenario(error_count=2, normal_count=3)
print(f'✅ Created error scenario with {len(error_logs)} logs')
"

echo ""
echo -e "${YELLOW}3️⃣  Testing frontend components...${NC}"
cd ../frontend
npm test -- --testNamePattern="renders log processing system title" --watchAll=false --silent
echo -e "${GREEN}✅ Frontend component tests passed${NC}"

echo ""
echo -e "${YELLOW}4️⃣  Testing user interactions...${NC}"
npm test -- --testNamePattern="handles log creation" --watchAll=false --silent
echo -e "${GREEN}✅ User interaction tests passed${NC}"

echo ""
echo -e "${GREEN}🎉 Demo completed! Your testing framework is working correctly.${NC}"
echo ""
echo "Next steps:"
echo "• Run 'npm start' in frontend/ to see the UI"
echo "• Run './build_and_verify.sh' for full test suite"
echo "• Check coverage reports after running tests"
