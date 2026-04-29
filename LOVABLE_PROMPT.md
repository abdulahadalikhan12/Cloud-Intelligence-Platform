# Cloud Intelligence Platform — Lovable Frontend Prompt

> **Copy-paste this entire prompt into Lovable to generate the frontend.**

---

## Prompt

Build a **Cloud Intelligence Platform** — a premium, modern dashboard web application for real-time global weather and air quality monitoring with AI-powered insights. The app connects to a FastAPI backend API.

### Tech Stack
- React + TypeScript + Vite
- Mapbox GL JS for interactive maps (use `react-map-gl` library)
- Recharts for data visualizations
- Lucide React for icons
- Framer Motion for animations
- CSS animations + Lottie for micro-interactions (NO Three.js)
- Tailwind CSS for styling

### Backend API
The backend is hosted at: `https://abdulahadalikhan12-cloud-intelligence.hf.space`
All API calls should use this base URL. Add CORS headers. The API returns JSON.

Key endpoints:
- `GET /api/v1/cities/all` → list of all cities with lat/lon
- `GET /api/v1/cities/search?q={query}` → fuzzy city search
- `GET /api/v1/weather/current/{city}` → current weather
- `GET /api/v1/weather/forecast/{city}` → 7-day forecast
- `GET /api/v1/air-quality/current/{city}` → current AQI, PM2.5, PM10, NO2, O3
- `GET /api/v1/air-quality/rankings` → cleanest and most polluted cities
- `POST /api/v1/agents/analyze/{city}` → full AI analysis (weather + AQ + predictions + recommendations)
- `POST /api/v1/agents/compare` → compare multiple cities (body: array of city name strings)
- `POST /api/v1/agents/search` → semantic search (body: `{"query": "...", "top_k": 5}`)
- `POST /api/v1/predict/aqi-risk` → AQI risk prediction
- `POST /api/v1/predict/pollution` → PM2.5 prediction
- `GET /health` → health check

### Environment Variables
- `VITE_API_BASE_URL` = backend URL (default: `https://abdulahadalikhan12-cloud-intelligence.hf.space`)
- `VITE_MAPBOX_TOKEN` = Mapbox public token (user will add this in Vercel)

### Design System

**Color Palette (Dark Mode Primary):**
- Background: `#0a0a0f` (deep dark), `#12121a` (card bg), `#1a1a2e` (elevated)
- Primary accent: `#6366f1` (indigo), `#818cf8` (lighter indigo)
- Success/Good AQI: `#10b981` (emerald)
- Warning/Moderate: `#f59e0b` (amber)
- Danger/Unhealthy: `#ef4444` (red)
- Critical: `#dc2626` (deep red)
- Text primary: `#f1f5f9`, Text secondary: `#94a3b8`
- Glass effect: `rgba(255, 255, 255, 0.05)` with `backdrop-filter: blur(12px)`

**Typography:**
- Font family: Inter (from Google Fonts)
- Headings: bold, tracking tight
- Numbers/metrics: tabular-nums font-feature

**Design Principles:**
- Glassmorphism cards with subtle borders (`border: 1px solid rgba(255,255,255,0.08)`)
- Smooth gradient backgrounds on hero section
- Hover effects on all interactive elements (scale, glow)
- Loading skeletons for async data
- All transitions: `transition-all duration-300 ease-out`

### Pages & Components

#### 1. Layout (Persistent)
- **Sidebar** (left, collapsible on mobile):
  - Logo: "🌍 Cloud Intel" with gradient text
  - Nav items with Lucide icons: Dashboard, Map, Rankings, Compare, AI Search
  - Active state: indigo highlight with rounded bg
  - Bottom: health status indicator (green dot + "API Online")
- **Top Bar**:
  - Search bar (city search using `/api/v1/cities/search?q=...`) with debounced input
  - When user selects a city, navigate to that city's detail page
  - Clock showing current UTC time

#### 2. Dashboard Page (Home `/`)
- **Hero Section**: Animated gradient background (indigo → purple → blue shifting). Title: "Cloud Intelligence Platform". Subtitle: "Real-time environmental intelligence for 120+ global cities". Call-to-action button: "Explore Map →"
- **Quick Stats Row** (4 cards):
  - Total cities monitored (from `/api/v1/cities/all` count)
  - Average global AQI (calculated from rankings)
  - Cities with Good air quality (count from rankings)
  - Active AI agents: "3" (static)
- **AQ Rankings Section**: Two side-by-side glassmorphism cards:
  - "🌿 Cleanest Cities" — top 5 from `/api/v1/air-quality/rankings` → `cleanest`
  - "⚠️ Most Polluted" — top 5 from `most_polluted`
  - Each row: rank, city name, country flag emoji, AQI badge (color-coded by category)
- **Mini Map Preview**: Small Mapbox map showing all city markers color-coded by AQI

#### 3. Map Page (`/map`)
- **Full-screen Mapbox GL map** (dark style: `mapbox://styles/mapbox/dark-v11`)
- Load all cities from `/api/v1/cities/all`
- **City Markers**: Colored circles based on AQI (green=good, yellow=moderate, red=unhealthy)
  - On hover: show tooltip with city name + AQI
  - On click: slide-in panel from right with city details (call `/api/v1/agents/analyze/{city}`)
- **Slide-in Panel** (right side, 400px wide):
  - City name + country
  - Current weather: temperature, humidity, wind, condition icon
  - Air quality: AQI gauge (circular), pollutant bars (PM2.5, PM10, NO2, O3)
  - AI Recommendations: list of recommendations with emoji icons
  - "Full Analysis →" button linking to city detail page
- **Map Controls**: Zoom, style toggle (dark/satellite), legend
- **Layer Toggle**: Button group to toggle between "AQI Overlay", "Temperature Overlay", "Wind Overlay"

#### 4. City Detail Page (`/city/:cityName`)
- Call `POST /api/v1/agents/analyze/{cityName}` on mount
- Show loading skeleton while fetching
- **Header**: City name, country, lat/lon, overall livability score (circular gauge, 0-100)
- **Weather Card**: Current conditions with weather icon, temperature (large), feels like, humidity, wind, pressure
- **7-Day Forecast**: Horizontal scrollable cards from `/api/v1/weather/forecast/{city}` — each card shows date, icon, high/low temp, rain probability
- **Air Quality Card**:
  - Large AQI number with colored background
  - Category badge
  - Pollutant breakdown: 4 horizontal progress bars (PM2.5, PM10, NO2, O3) with labels and values
  - Dominant pollutant highlighted
- **AI Insights Panel** (glassmorphism card with purple border glow):
  - Title: "🤖 AI Intelligence Report"
  - List of insights from `analysis.insights` — each with severity badge, title, description
  - Cluster assignment: chip showing "Temperate & Clean" or similar
- **Recommendations Section**:
  - Grid of recommendation cards (2 columns)
  - Each card: emoji icon, title, description, priority badge
  - Health advisory banner at top (yellow/red based on severity)
  - "Best time to visit" info
- **Comparison text**: e.g., "Better air quality than 75% of major cities"

#### 5. Compare Page (`/compare`)
- Multi-select city picker (max 5 cities)
- "Compare" button calls `POST /api/v1/agents/compare` with selected city names
- **Results**:
  - "Best Overall" badge on winning city
  - Comparison table: rows = metrics (AQI, Temperature, Humidity, PM2.5, Score), columns = cities
  - Radar chart (Recharts) comparing cities across 5 dimensions
  - Summary text from API response

#### 6. AI Search Page (`/search`)
- Large search input with placeholder: "Find cities with clean air and warm weather..."
- On submit: `POST /api/v1/agents/search` with `{"query": "...", "top_k": 10}`
- **Results**: List of city cards with:
  - City name, country
  - Relevance score (percentage bar)
  - Summary text
  - "View Details →" link to city page
- Example queries as clickable chips below search bar:
  - "warm cities with clean air"
  - "cold climate low pollution"
  - "tropical megacities"
  - "best air quality in Europe"

### Animations
- Page transitions: fade-in with slight upward slide (Framer Motion)
- Cards: stagger animation on load (each card appears 50ms after previous)
- Number counters: animate from 0 to target value on mount
- AQI gauge: smooth fill animation over 1s
- Map markers: pulse animation on the selected city
- Hover effects: subtle scale(1.02) + shadow glow on cards
- Loading: skeleton pulse animation (not spinners)
- Sidebar: smooth collapse/expand with 300ms transition

### Responsive Design
- Desktop: sidebar + main content
- Tablet (< 1024px): collapsible sidebar, 2-column grids → 1-column
- Mobile (< 768px): bottom navigation bar (replacing sidebar), stacked layout, full-width cards

### Error Handling
- If API is unreachable, show a banner: "⚠️ Backend is starting up. Some features may be temporarily unavailable."
- Individual component error boundaries with "Retry" buttons
- Graceful fallbacks for missing data (show "N/A" not blank)

### Performance
- Lazy load pages with React.lazy + Suspense
- Debounce search input (300ms)
- Cache API responses in React Query (staleTime: 5 minutes for weather, 1 hour for cities)
- Use React Query for all API calls

### SEO
- Title: "Cloud Intelligence Platform — Real-time Global Environmental Monitoring"
- Meta description: "AI-powered weather and air quality intelligence for 120+ cities worldwide. Real-time monitoring, predictions, and recommendations."

### Important Notes
- The Mapbox token should be read from `import.meta.env.VITE_MAPBOX_TOKEN`
- If no Mapbox token is available, show a static placeholder map with a message
- All API errors should be handled gracefully — never show raw error JSON to users
- Use React Router v6 for routing
- Store the API base URL in a constants file, read from `import.meta.env.VITE_API_BASE_URL`
