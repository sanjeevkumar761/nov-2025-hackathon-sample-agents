# SmartTech TSD Agent - Web UI

A modern React + TypeScript + Vite web application for testing the SmartTech TSD Ticket Classification API.

## Features

- 🎯 **Single Ticket Classification** - Submit individual tickets for AI-powered intent detection
- 📊 **Real-time Statistics** - Track classification metrics and self-service rates
- 🎨 **Modern UI** - Beautiful, responsive interface built with Tailwind CSS
- 🧪 **Mock Data Testing** - Test with 10 pre-loaded mock tickets
- 📈 **Visual Analytics** - View intent and routing distributions
- ⚡ **Real-time Updates** - Statistics auto-refresh every 5 seconds

## Prerequisites

- Node.js 18+ 
- npm or yarn
- SmartTech API server running on `http://localhost:8000`

## Quick Start

### 1. Install Dependencies

```bash
cd smarttech-ui
npm install
```

### 2. Start the API Server

In a separate terminal, ensure the FastAPI server is running:

```bash
cd ..
python smarttech_api.py
```

The API should be accessible at `http://localhost:8000`

### 3. Start the Development Server

```bash
npm run dev
```

The UI will be available at `http://localhost:3000`

## Usage

### Submit a New Ticket

1. Fill out the form with ticket details:
   - Subject (required)
   - Description (required)
   - Category
   - Priority
   - User email

2. Click "Classify Ticket"

3. View the AI analysis results:
   - Detected intent
   - Confidence score
   - Self-service eligibility
   - Recommended KB articles
   - Routing decision

### Test with Mock Tickets

- Click any ticket in the "Test with Mock Tickets" panel
- The ticket will be automatically classified
- Results appear instantly in the main area

### Monitor Statistics

- View total classifications
- See self-service eligibility rate
- Track intent distribution
- Monitor routing decisions
- Reset stats with the refresh button

## API Configuration

The UI connects to the API at `http://localhost:8000` by default.

To change this, edit `src/api.ts`:

```typescript
const API_BASE_URL = 'http://your-api-url:8000';
```

## Build for Production

```bash
npm run build
```

The production build will be in the `dist/` folder.

Preview the production build:

```bash
npm run preview
```

## Project Structure

```
smarttech-ui/
├── src/
│   ├── components/
│   │   ├── ClassificationResults.tsx  # Results display
│   │   ├── MockTicketsPanel.tsx       # Mock data panel
│   │   ├── StatsPanel.tsx             # Statistics dashboard
│   │   └── TicketForm.tsx             # Ticket submission form
│   ├── api.ts                          # API client
│   ├── types.ts                        # TypeScript interfaces
│   ├── App.tsx                         # Main app component
│   ├── main.tsx                        # Entry point
│   └── index.css                       # Global styles
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icon library

## Features Showcase

### 🎯 Intent Detection
AI analyzes ticket content to detect user intent (password reset, VPN issues, email setup, etc.)

### 📊 Confidence Scoring
Each classification includes a confidence score (0-100%)

### ✅ Self-Service Recommendation
Automatically determines if tickets can be resolved without helpdesk

### 📚 KB Article Matching
Suggests relevant knowledge base articles with success rates

### 🔀 Smart Routing
Recommends routing (Self-Service, Tier 1, Tier 2, Manual Review)

### 📈 Analytics Dashboard
Real-time statistics showing:
- Total classifications
- Self-service rate
- Intent distribution
- Routing distribution
- Potential impact on helpdesk workload

## Keyboard Shortcuts

- `Ctrl/Cmd + Enter` in form fields - Submit ticket
- `Esc` - Clear error messages

## Troubleshooting

### "Failed to fetch" Error

- Ensure the API server is running on port 8000
- Check CORS settings in `smarttech_api.py`
- Verify the API_BASE_URL in `src/api.ts`

### Slow Response Times

- First classification takes longer (LLM initialization)
- Subsequent classifications are faster
- Typical response time: 2-3 seconds

### Mock Tickets Not Loading

- Verify API health at `http://localhost:8000/api/v1/health`
- Check browser console for errors
- Ensure API endpoint `/api/v1/tickets/mock` is accessible

## Development

### Run Linter

```bash
npm run lint
```

### Type Checking

```bash
npx tsc --noEmit
```

## Contributing

1. Make changes in feature branch
2. Test thoroughly with mock and real tickets
3. Ensure TypeScript compiles without errors
4. Run linter
5. Submit pull request

## License

Part of SmartTech TSD Agent project - Internal use only

---

**Built with ❤️ for SmartTech TSD Team**
