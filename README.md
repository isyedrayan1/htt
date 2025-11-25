# 🏎️ TRINITE
## AI-Powered Driver Coaching Platform for Toyota Gazoo Racing

**Hackathon Project**: "Hack the Track" Challenge  
**Track**: Circuit of the Americas (COTA)  
**Technology**: FastAPI + React + AI (Groq LLaMA 3.3)

---

## 🚀 Quick Start (For Judges)

### Prerequisites
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 16+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))

### One-Command Setup ⚡

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

This will automatically:
1. ✅ Install all dependencies
2. ✅ Start backend server (Port 8000)
3. ✅ Start frontend server (Port 3001)
4. ✅ Open application in browser

---

## 📋 Manual Setup (Step-by-Step)

### Step 1: Clone the Repository
```bash
git clone https://github.com/isyedrayan1/htt.git
cd htt
```

### Step 2: Backend Setup

**Open Terminal 1** (for backend):

```bash
# In the root folder make virtual environment and inspall requirements.txt

# Install Python dependencies
pip install -r requirements.txt

# Start backend server
cd backend
uvicorn main:app --reload --port 8000
```

**Backend will be running at**: http://localhost:8000  
**API Documentation**: http://localhost:8000/docs

### Step 3: Frontend Setup

**Open Terminal 2** (for frontend):

**Windows:**
```bash
# Navigate to frontend folder
cd frontend

# Install Node dependencies
npm install

# Start frontend server
set PORT=3001
npm start
```

**Linux/Mac:**
```bash
# Navigate to frontend folder
cd frontend

# Install Node dependencies
npm install

# Start frontend server
export PORT=3001
npm start
```

**Frontend will be running at**: http://localhost:3001

### Step 4: Access the Application

Open your browser and navigate to:
- **Application**: http://localhost:3001
- **API Docs**: http://localhost:8000/docs

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

## 🔧 Environment Configuration

### Optional: Groq API Key

For full AI features, create `.env` file in `backend/`:

```
GROQ_API_KEY=your_groq_api_key_here
```

**Note**: The application works without an API key, but AI responses will use fallback logic.

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

## 🛠️ Troubleshooting

### Port Already in Use

**Backend:**
```bash
uvicorn main:app --reload --port 8080
```

**Frontend:**
```bash
# Windows
set PORT=3002
npm start

# Linux/Mac
export PORT=3002
npm start
```

### Python Not Found
Ensure Python is in your PATH:
```bash
python --version
# or
python3 --version
```

### Node.js Not Found
Ensure Node.js is installed:
```bash
node --version
npm --version
```

### Dependencies Installation Fails

**Backend:**
```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

**Frontend:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📁 Documentation

See `docs/` folder for:
- **PRESENTATION_PITCH.md**: 5-8 minute demo script
- **SETUP.md**: Detailed setup instructions
- **WALKTHROUGH.md**: Feature walkthrough

See `backend/README.md` for:
- Technical architecture details
- Custom ML algorithms explanation
- API endpoint documentation

---

## 🏆 Hackathon Highlights

- ✅ **Real Data**: Actual COTA telemetry from Toyota Gazoo Racing
- ✅ **Production-Ready**: FastAPI + React with proper architecture
- ✅ **AI-Powered**: Groq LLaMA 3.3 for intelligent insights
- ✅ **Innovative ML**: Custom DPTAD & SIWTL algorithms
- ✅ **Professional UI**: Modern, responsive design
- ✅ **Comprehensive**: 5 major pages, 12+ API endpoints

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
- Custom CSS (Styling)
- React Router

**ML/AI:**
- Custom DPTAD algorithm
- Custom SIWTL algorithm
- Groq LLaMA 3.3 integration

---

## 📞 Support

For any issues during evaluation:
1. Check Python and Node.js are installed
2. Verify ports 8000 and 3001 are available
3. Run `start.bat` or `start.sh` from project root

---

## 🎯 Quick Reference

| Component | URL | Description |
|-----------|-----|-------------|
| Frontend | http://localhost:3001 | Main application |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Interactive API documentation |

---

**Built with ❤️ for Toyota Gazoo Racing "Hack the Track" Challenge**
