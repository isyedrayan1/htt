# 🏁 Racing Analytics Platform - React Frontend Setup

## Quick Start

### Prerequisites
- Node.js 16+ and npm
- Backend API running on localhost:8000

### Installation & Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The React app will open at http://localhost:3000

### Backend Connection

The frontend automatically connects to the backend API at `http://localhost:8000`. Make sure your backend is running before starting the frontend.

### Development Commands

```bash
# Install dependencies
npm install

# Start development server (hot reload)
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Features

- **🏎️ Live Race Monitor**: Real-time positions, telemetry, and race progression
- **📊 Dashboard**: Overview of race status and key metrics  
- **👤 Driver Analysis**: Detailed performance insights and AI coaching
- **🎯 Strategy Center**: Pit optimization and race strategy analysis
- **📱 Responsive Design**: Works on desktop, tablet, and mobile

### Architecture

- **Frontend**: React 18 with React Router
- **Styling**: Tailwind CSS with custom racing theme
- **Charts**: Plotly.js for interactive visualizations  
- **API**: Axios for backend communication
- **Icons**: Lucide React for modern icons

### API Endpoints Used

- `GET /api/realtime/live/summary` - Live race data
- `GET /api/realtime/live/telemetry/{driver}` - Driver telemetry
- `GET /api/realtime/strategy/pit-optimizer` - Pit strategies
- `GET /api/analysis/summary` - Session analysis
- `GET /api/drivers` - Driver list
- `POST /api/realtime/live/advance` - Advance race simulation

### Customization

The racing theme is configured in `tailwind.config.js`:
- Colors: Red (#DC2626), Black (#0F0F0F), Silver (#9CA3AF)
- Fonts: Orbitron (racing), JetBrains Mono (technical data)
- Custom components: Cards, badges, telemetry bars, etc.

### Troubleshooting

**Frontend won't start:**
- Ensure Node.js 16+ is installed
- Run `npm install` in the frontend directory
- Check for port conflicts (default: 3000)

**API connection errors:**
- Verify backend is running on localhost:8000
- Check CORS settings in backend
- Look for network/firewall issues

**Build errors:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check for TypeScript/ESLint errors
- Ensure all dependencies are up to date