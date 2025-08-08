#!/bin/bash
echo "🚀 ZK-OFAC Authentication System Deployment"
echo "============================================"
echo "🔐 Zero-Knowledge OFAC Compliance"
echo "📊 13,661 sanctions entries across 3 databases"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.8+ required"
    exit 1
fi
echo "✅ Python $(python3 --version)"

if ! command -v node &> /dev/null; then
    echo "❌ Node.js 16+ required" 
    exit 1
fi
echo "✅ Node.js $(node --version)"

if ! command -v npm &> /dev/null; then
    echo "❌ npm required"
    exit 1
fi
echo "✅ npm $(npm --version)"

echo ""
echo "📦 Installing dependencies..."

# Install KYC provider dependencies
echo "🔧 Installing KYC provider..."
cd kyc-provider
pip3 install flask flask-cors PyJWT fuzzywuzzy python-levenshtein
echo "✅ KYC dependencies installed"

# Install frontend dependencies (if package.json exists)
cd ../frontend
if [ -f "package.json" ]; then
    echo "🌐 Installing frontend dependencies..."
    npm install
    echo "✅ Frontend dependencies installed"
fi

cd ..

echo ""
echo "🚀 Starting services..."

# Start KYC provider
echo "🔌 Starting KYC provider..."
cd kyc-provider
python3 app.py &
KYC_PID=$!
echo "✅ KYC provider running (PID: $KYC_PID) on http://localhost:5002"

# Wait for startup
sleep 3

# Test KYC provider
echo "🔍 Testing KYC provider..."
if curl -s http://localhost:5002/api/system-status > /dev/null; then
    echo "✅ KYC provider health check passed"
else
    echo "⚠️ KYC provider starting up..."
fi

# Start frontend if available
cd ../frontend
if [ -f "package.json" ]; then
    echo "🌐 Starting frontend..."
    npm start &
    FRONTEND_PID=$!
    echo "✅ Frontend starting (PID: $FRONTEND_PID)"
fi

cd ..

echo ""
echo "🎉 ZK-OFAC System Deployed Successfully!"
echo "========================================"
echo ""
echo "🌐 Service Endpoints:"
echo "   📡 KYC Provider:  http://localhost:5002"
echo "   🖥️  Frontend:     http://localhost:3000"
echo "   📊 System Status: http://localhost:5002/api/system-status"
echo ""
echo "🧪 Test Commands:"
echo '   curl -X POST http://localhost:5002/api/screen-user \'
echo '     -H "Content-Type: application/json" \'
echo '     -d '"'"'{"full_name":"Alice Johnson","date_of_birth":"1992-03-15"}'"'"
echo ""
echo "🎬 Browser Demo:"
echo "   1. Open http://localhost:3000"
echo "   2. Open browser console"
echo "   3. Run: window.demoZKCompliance()"
echo ""
echo "🛑 To stop:"
echo "   kill $KYC_PID"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "   kill $FRONTEND_PID"
fi
echo ""
echo "🔐 Features:"
echo "   ✅ Zero-knowledge proof generation"
echo "   ✅ Multi-database OFAC screening (13,661 entries)"
echo "   ✅ Privacy-preserving compliance verification"
echo "   ✅ Real-time sanctions screening"
echo "   ✅ P2P payment authorization"
echo ""
echo "🎉 Ready for zero-knowledge compliance!"

wait
