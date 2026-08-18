# 📱 Native Mobile App Scoping Document — StockSense AI (Flutter Rewrite)

This document outlines the architectural requirements, backend API decoupling strategy, screen-by-screen breakdown, and complexity estimates for converting the Streamlit web application into a high-performance native mobile app for Google Play Store and Apple App Store using **Flutter (Dart)**.

---

## 🏗️ System Architecture & Backend API Decoupling

The Streamlit version combines UI presentation, data fetching, and business logic into a single Python runtime. For a native mobile app, the architecture must be split into a **Client-Server Architecture**:

```
[ Flutter Mobile App (iOS / Android) ]
                 │
           HTTP / REST (JSON)
                 │
                 ▼
[ Python FastAPI Backend Microservice ]  ──► yFinance / Groq LLM / Alpha Vantage
```

### 1. Python Backend Microservice Layer (REUSE `data_service.py`)
Instead of rewriting complex financial math and technical indicator logic in Dart, extract `data_service.py` into a lightweight **FastAPI** REST microservice (hosted on Railway, Render, or AWS Lambda):

- **`/api/v1/indices`**: Returns live Sensex, Nifty 50, S&P 500 indices.
- **`/api/v1/search`**: Auto-complete ticker search across Indian & US stock datasets.
- **`/api/v1/stock/{ticker}`**: Full stock data payload (info, fundamentals, technical indicators: RSI, MACD, Bollinger Bands, MA50).
- **`/api/v1/screen`**: `POST` endpoint accepting screener parameters (P/E, D/E, ROE, promoter %, budget) and returning ranked stock scores.
- **`/api/v1/ai-summary`**: `POST` endpoint triggering Groq Llama 3.3 for structured AI stock summaries.
- **`/api/v1/portfolio/analyze`**: `POST` endpoint accepting JSON/CSV holdings list and returning P&L analytics, sector concentration, and risk scores.
- **`/api/v1/sectors/heatmap`**: Real-time sector performance metrics.

### 2. Flutter Mobile Application Stack (NEW)
- **Framework**: Flutter 3.x (Dart)
- **State Management**: `flutter_bloc` or `riverpod`
- **Networking**: `dio` with JSON serializable models (`json_annotation`)
- **Financial Charting**: `fl_chart` or `interactive_chart` (native 60fps gesture-enabled candlestick & indicator charts)
- **Local Storage**: `flutter_secure_storage` (auth token) & `hive` / `shared_preferences` (watchlist & local settings)

---

## 📱 Screen-by-Screen Breakdown & Complexity Matrix

| Screen Name | Core Features | Reusable Python Backend Logic | Flutter UI Work Required | Complexity |
|---|---|---|---|:---:|
| **1. Auth & Onboarding** | Guest mode, Email login, Firebase Google Auth, Privacy note | None (Use Firebase Auth) | Custom onboarding carousel, Google Sign-In button, cookie token storage | 🟢 **Simple** |
| **2. Home Dashboard** | Live index ticker bar, market overview cards, quick actions, market toggle | `/api/v1/indices` | Animated horizontal ticker marquee, market selector pill, top gainers list | 🟡 **Medium** |
| **3. Beginner Wizard & SIP Calculator** | 5-Step guided flow, interactive SIP sliders, wealth projection chart | `/api/v1/screen` & `/api/v1/sip-calculator` | Multi-step PageView controller, custom dual sliders, `fl_chart` stacked area chart | 🟡 **Medium** |
| **4. Pro Screener** | Multi-slider filter modal, budget input, passed/rejected tab view, score bar chart | `/api/v1/screen` | BottomSheet filter panel, sorting dropdowns, animated progress bars | 🔴 **Complex** |
| **5. Trending & Sector Heatmap** | Daily highlighted movers list, styled sector performance cards grid | `/api/v1/sectors/heatmap` | TabBar controller, grid layout with color-coded percent change chips | 🟡 **Medium** |
| **6. Stock Detail & Intelligence** | Fundamentals grid, ELI5 cards toggle, Candlestick OHLCV, RSI/MACD charts, AI summary tab, Insider donut chart, Peer cards | `/api/v1/stock/{ticker}` & `/api/v1/ai-summary` | Nested TabBar, interactive touch candlestick chart with zoom/pan, SVG radar chart, shareholding pie chart | 🔴 **Complex** |
| **7. Head-to-Head Comparison** | 2–3 stock multi-select, 3-month normalized growth chart (base 100), 12-metric table | `/api/v1/stock/compare` | Multi-line normalized performance chart, horizontal scrolling comparison grid | 🔴 **Complex** |
| **8. Portfolio Health & Risk Analyzer** | CSV paste / manual stock entry form, P&L metric cards, sector concentration donut, allocation bar chart, risk gauge | `/api/v1/portfolio/analyze` | Holdings input form with auto-complete ticker lookup, sector donut chart, risk rating card | 🔴 **Complex** |
| **9. Watchlist & Profile** | Saved stocks list with swipe-to-delete, price change indicators, user account state | Local storage / Firebase | Dismissible ListView, swipe actions, dark mode settings toggle | 🟢 **Simple** |

---

## 💡 Summary of Backend Code Reuse

### What to REUSE As-Is (Python FastAPI):
- `data_service.py` technical indicator calculations (`compute_technicals`: RSI, MACD, Bollinger Bands, Moving Averages).
- Rule-based quantitative recommendation scoring engine (`generate_recommendation`).
- yFinance downloading & fallback data pipeline.
- Groq Llama 3.3 prompt templates and API integrations.
- Portfolio P&L, sector concentration, and risk rating algorithms (`analyze_portfolio_holdings`).
- SIP and compound wealth math (`calculate_sip_lumpsum`).

### What to REWRITE in Flutter (Dart):
- All UI layouts, Glassmorphic CSS styling, and Streamlit widgets (`ui_components.py`).
- Navigation router & session state management.
- Plotly chart rendering (replaced with native Flutter canvas `fl_chart` for smooth touch interactions).

---

## 🗓️ Rough Development Timeline (Native Flutter Rebuild)

- **Phase 1 (Week 1)**: FastAPI wrapper setup & endpoint deployment (`data_service.py` → REST API).
- **Phase 2 (Week 2)**: Flutter project setup, theme design system, Auth & Home Dashboard.
- **Phase 3 (Week 3)**: Stock Detail view with native candlestick & indicator charts (`fl_chart`).
- **Phase 4 (Week 4)**: Beginner Wizard, Pro Screener & SIP Wealth Calculator.
- **Phase 5 (Week 5)**: Portfolio Risk Analyzer & Head-to-Head Comparison tools.
- **Phase 6 (Week 6)**: Testing, performance optimization, Play Store & App Store build submission.
