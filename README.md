# 🏎️ GR-X BLINDSPOT COMMAND
## AI-Powered Driver Coaching Platform for Toyota Gazoo Racing

**Hackathon Project**: "Hack the Track" Challenge  
**Track**: Circuit of the Americas (COTA)  
**Technology**: FastAPI + React + AI (Groq LLaMA 3.3)

---

## 🚀 Quick Start (For Judges)

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### One-Command Setup

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

This will:
1. ✅ Install all dependencies
2. ✅ Start backend server (Port 8000)
3. ✅ Start frontend server (Port 3001)
4. ✅ Open the application automatically

### Access Points
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 🎯 Project Overview

An intelligent racing analytics platform that uses AI to provide real-time driver coaching, performance analysis, and telemetry insights for Toyota Gazoo Racing drivers at COTA.

### Key Features

#### 1. **AI-Powered Coaching**
- Real-time driver performance analysis
- Personalized coaching recommendations
- AI chatbot with context-aware assistance

#### 2. **Advanced ML Algorithms**
- **DPTAD**: Driver Performance & Telemetry Anomaly Detection
- **SIWTL**: Smart Ideal Weighted Target Lap calculation
- Consistency scoring and variance analysis

#### 3. **Comprehensive Analytics**
- Fleet-wide performance dashboard
- Driver comparison (head-to-head)
- Evidence Explorer (deep telemetry analysis)
- Sector-by-sector breakdown

#### 4. **Interactive Visualizations**
- Real-time telemetry graphs
- Lap progression charts
- Sector performance comparisons
- Top performers leaderboard

---

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── main.py                 # FastAPI application
├── api/
│   ├── drivers.py         # Driver endpoints
│   ├── laps.py            # Lap data endpoints
│   ├── telemetry.py       # Telemetry endpoints
│   ├── ml_analysis.py     # DPTAD & SIWTL algorithms
│   ├── compare.py         # Driver comparison
│   ├── fleet.py           # Fleet summary
│   ├── coaching.py        # AI coaching
│   └── ai_assistant.py    # AI chatbot
├── db/                    # Database layer (DuckDB)
├── src/
│   └── coaching/
│       └── llm_client.py  # Groq AI integration
└── data/                  # Telemetry data
```

### Frontend (React)
```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard/         # Fleet overview
│   │   ├── DriverAnalysis/    # Individual driver analysis
│   │   ├── Compare/           # Driver comparison
│   │   ├── Evidence/          # Telemetry explorer
│   │   └── AI/                # AI chatbot
│   └── services/
│       └── apiService.js      # API client
```

---

## 🔧 Manual Setup (If Needed)

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
set PORT=3001  # Windows
export PORT=3001  # Linux/Mac
npm start
```

---

## 📊 Data Pipeline

1. **Ingestion**: Telemetry data from COTA (parquet files)
2. **Processing**: DuckDB for fast analytics
3. **ML Analysis**: DPTAD & SIWTL algorithms
4. **AI Coaching**: Groq LLaMA 3.3 for insights
5. **Visualization**: React + Plotly charts

---

## 🤖 AI Features

### Context-Aware Chatbot
- **Global Knowledge**: Knows entire fleet performance
- **Page-Specific**: Adapts to current page context
- **Dynamic Suggestions**: Intelligent follow-up questions
- **Quick Actions**: One-click common queries

### AI Coaching
- Personalized recommendations per driver
- Sector-specific improvement tips
- Consistency analysis
- Anomaly explanations

---

## 🎨 Key Pages

1. **Dashboard**: Fleet-wide overview with AI insights
2. **Driver Analysis**: Individual performance + coaching
3. **Compare**: Head-to-head driver comparison
4. **Evidence Explorer**: Deep telemetry analysis
5. **Strategy Center**: Race strategy & pit optimization

---

## 🔑 Environment Variables

Create `.env` file in backend/:
```
GROQ_API_KEY=your_groq_api_key_here
```

*Note: App works without API key but AI features will use fallback responses*

---

## 📁 Documentation

See `docs/` folder for:
- Implementation plan
- Development walkthrough
- Task breakdown
- Technical details

---

## 🏆 Hackathon Highlights

- ✅ **Real Data**: Actual COTA telemetry from Toyota Gazoo Racing
- ✅ **Production-Ready**: FastAPI + React with proper architecture
- ✅ **AI-Powered**: Groq LLaMA 3.3 for intelligent insights
- ✅ **Innovative ML**: Custom DPTAD & SIWTL algorithms
- ✅ **Professional UI**: Modern, responsive design
- ✅ **Comprehensive**: 5 major pages, 10+ API endpoints

---

## 👨‍💻 Tech Stack

**Backend:**
- FastAPI (Python)
- DuckDB (Analytics DB)
- Pandas (Data processing)
- Groq AI (LLaMA 3.3)

**Frontend:**
- React 18
- Plotly.js (Charts)
- TailwindCSS (Styling)
- React Router

**ML/AI:**
- Custom DPTAD algorithm
- Custom SIWTL algorithm
- Groq LLaMA 3.3 integration

---

## 📞 Support

For any issues during evaluation, please check:
1. Python and Node.js are installed
2. Ports 8000 and 3001 are available
3. Run `start.bat` or `start.sh` from project root

---

**Built with ❤️ for Toyota Gazoo Racing "Hack the Track" Challenge**
