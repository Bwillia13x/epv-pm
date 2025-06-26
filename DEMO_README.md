# EPV Research Platform - Demo Setup Guide

## 🎯 Overview

This beautiful, modern frontend brings the EPV Research Platform to demo quality with a professional React interface, FastAPI backend, and comprehensive financial analysis capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with all dependencies installed (see `requirements.txt`)
- Node.js 16+ and npm
- Internet connection for financial data APIs

### Environment Variables

Create a `.env` file (or export variables in your shell) with at minimum:

```bash
JWT_SECRET=<secure_random_string>
ALPHA_VANTAGE_API_KEY=<your_key>   # optional
FRED_API_KEY=<your_key>            # optional
QUANDL_API_KEY=<your_key>          # optional
```

`JWT_SECRET` is mandatory for the authentication layer.  Data-provider keys unlock richer datasets but the demo can run without them (with limited capabilities).

### 1. Start the Complete Demo

```bash
# Option 1: Use the automated startup script
python start_demo.py

# Option 2: Manual startup (recommended for development)
# Terminal 1: Start API server
python src/main.py api --port 8000

# Terminal 2: Start React frontend
cd frontend
npm start
```

### 2. Access the Application

- **Frontend UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 🎨 Frontend Features

### Modern React Architecture
- **TypeScript** for type safety
- **Material-UI (MUI)** for beautiful, professional components
- **React Router** for navigation
- **Recharts** for interactive data visualization
- **Axios** for API communication

### Key Pages & Features

#### 1. Dashboard (`/`)
- System status monitoring
- Key metrics overview
- Quick start guide
- Real-time health checks

#### 2. Stock Analysis (`/analysis`)
- **Single Stock Analysis**: Detailed EPV calculation
- **Interactive Forms**: Symbol input, peer comparison, analysis type selection
- **Real-time Charts**: Price vs EPV visualization
- **Comprehensive Results**: Quality scores, risk assessment, investment thesis
- **Peer Comparison**: Side-by-side analysis with competitors

#### 3. Portfolio Management (`/portfolio`)
- **Batch Analysis**: Analyze multiple stocks simultaneously
- **Portfolio Visualization**: Pie charts and bar charts
- **Recommendation Engine**: BUY/HOLD/SELL suggestions
- **Summary Statistics**: Portfolio-wide metrics
- **Data Export**: Results table with sorting

#### 4. Reports (`/reports`)
- **Report Generation**: Executive summaries, comprehensive analysis
- **Multiple Formats**: PDF, Excel, CSV, JSON export
- **Professional Templates**: Investment-grade report layouts
- **Scheduled Reports**: Coming soon features

## 🔧 API Architecture

### FastAPI Backend (`src/api/main.py`)
- **RESTful Endpoints**: Modern API design
- **CORS Support**: Frontend integration
- **Async Operations**: High-performance data processing
- **Error Handling**: Comprehensive error responses
- **Auto-documentation**: Swagger/OpenAPI integration

### Key Endpoints
- `POST /api/v1/analysis/{symbol}` - Single stock analysis
- `POST /api/v1/batch` - Batch analysis
- `GET /api/v1/company/{symbol}` - Company profile
- `GET /health` - System health check

## 📊 Analysis Capabilities

### EPV Methodology
- **Bruce Greenwald's Approach**: Normalized earnings / cost of capital
- **Quality Scoring**: 10-point comprehensive quality assessment
- **Risk Analysis**: Multi-factor risk evaluation
- **Margin of Safety**: Value-based investment decisions

### Data Sources
- **Yahoo Finance**: Real-time prices and historical data
- **Alpha Vantage**: Fundamental data and ratios
- **FRED**: Economic indicators and risk-free rates
- **Quandl**: Alternative data sources

## 🎯 Demo Scenarios

### Scenario 1: Individual Stock Analysis
1. Navigate to "Analysis" tab
2. Enter stock symbol (e.g., "AAPL")
3. Select "Full Analysis" 
4. Add peer symbols (e.g., "MSFT,GOOGL")
5. Click "Analyze"
6. Review comprehensive results

### Scenario 2: Portfolio Analysis  
1. Navigate to "Portfolio" tab
2. Enter multiple symbols: "AAPL,MSFT,GOOGL,AMZN,TSLA"
3. Click "Analyze Portfolio"
4. Review batch analysis results
5. Examine charts and recommendations

### Scenario 3: System Monitoring
1. Check Dashboard for system status
2. Verify API connectivity
3. Review data source availability
4. Monitor cache status

## 🔧 Technical Architecture

### Frontend Structure
```
frontend/
├── src/
│   ├── components/
│   │   └── layout/
│   │       └── Navbar.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── StockAnalysis.tsx
│   │   │   ├── Portfolio.tsx
│   │   │   └── Reports.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── App.tsx
```

### Backend Structure
```
src/
├── api/
│   └── main.py          # FastAPI application
├── analysis/            # Core analysis engines
├── data/               # Data collection services
├── models/             # Data models
└── main.py            # CLI entry point
```

## 🎨 Design System

### Color Palette
- **Primary**: Blue (#1976d2) - Trust, stability
- **Secondary**: Pink (#dc004e) - Attention, warnings
- **Success**: Green (#4caf50) - Positive results
- **Warning**: Orange (#ff9800) - Caution
- **Background**: Light gray (#f5f5f5) - Clean, professional

### Typography
- **Headers**: Roboto, 600 weight
- **Body**: Roboto, 400 weight
- **Emphasis**: 500 weight for key metrics

### UI Components
- **Cards**: Elevated shadows with hover effects
- **Buttons**: Rounded corners, no text transform
- **Charts**: Professional color schemes
- **Tables**: Clean, sortable, responsive

## 🚀 Performance Features

### Optimization
- **Caching**: API response caching with TTL
- **Rate Limiting**: API protection
- **Async Processing**: Non-blocking operations
- **Error Boundaries**: Graceful error handling

### Scalability
- **Component Architecture**: Reusable, maintainable
- **State Management**: Efficient data flow
- **API Design**: RESTful, versioned endpoints
- **Database Ready**: SQLAlchemy integration prepared

## 📱 Responsive Design

- **Mobile-First**: Optimized for all screen sizes
- **Tablet Support**: Optimized layouts
- **Desktop**: Full feature set
- **Accessibility**: WCAG compliance ready

## 🔮 Future Enhancements

### Advanced Features (Planned)
- **Real-time Data**: WebSocket integration
- **User Authentication**: Multi-user support
- **Database Integration**: Persistent data storage
- **Advanced Charts**: Interactive financial visualizations
- **AI Integration**: Enhanced analysis capabilities

### Professional Features
- **Report Scheduling**: Automated report generation
- **Email Integration**: Report delivery
- **Team Collaboration**: Shared analysis workspace
- **Custom Templates**: Branded report templates

## 🎯 Demo Quality Checklist

✅ **Modern UI/UX**: Professional, intuitive interface  
✅ **Responsive Design**: Works on all devices  
✅ **Real-time Data**: Live financial data integration  
✅ **Interactive Charts**: Engaging data visualization  
✅ **Error Handling**: Graceful error management  
✅ **Loading States**: Professional loading indicators  
✅ **API Integration**: Seamless backend connectivity  
✅ **Navigation**: Intuitive menu system  
✅ **Performance**: Fast, optimized experience  
✅ **Documentation**: Comprehensive setup guide  

## 🛠️ Development Commands

```bash
# Backend development
python src/main.py api --port 8000    # Start API server
python src/main.py analyze -s AAPL    # CLI analysis

# Frontend development  
cd frontend
npm start                             # Development server
npm run build                         # Production build
npm test                             # Run tests

# Complete demo
python start_demo.py                  # Start both servers
```

## 📈 Success Metrics

The platform is now demo-ready with:
- **Professional UI**: Modern, clean design
- **Comprehensive Analysis**: Full EPV methodology
- **Interactive Experience**: Engaging user interface  
- **Scalable Architecture**: Production-ready foundation
- **Documentation**: Complete setup and usage guide

This represents a significant upgrade from the basic Dash interface to a modern, professional financial analysis platform suitable for demonstrations and further development.