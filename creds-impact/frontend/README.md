# Creds Inspect Frontend

Next.js 14 frontend for credential detection dashboard.

## Architecture

```
src/
├── app/
│   ├── layout.tsx          → Root layout
│   ├── page.tsx            → Main page with state management
│   └── globals.css         → Global styles + Tailwind
├── components/
│   ├── ContentSubmit.tsx   → Multi-method content input
│   ├── ScanResults.tsx     → Tabbed results display
│   ├── CredentialsList.tsx → Credential findings table
│   ├── RiskDashboard.tsx   → Charts and risk visualization
│   ├── RemediationPlan.tsx → Action plans display
│   ├── ExecutiveReport.tsx → Report viewer
│   ├── ScanHistory.tsx     → Past scans list
│   └── StatsOverview.tsx   → Summary statistics
├── lib/
│   └── api.ts              → API client (Axios)
└── types/
    └── index.ts            → TypeScript definitions
```

## Features

### Content Submission
- **Paste Text:** Direct text input with content type selection
- **Confluence URL:** URL-based scanning (requires backend config)
- **File Upload:** Drag-and-drop support for TXT, PDF, DOC, DOCX, HTML

### Results Display
- **Credentials Tab:** Expandable findings with severity badges
- **Risk Tab:** Pie chart + bar chart visualizations
- **Remediation Tab:** Prioritized action plans with timelines
- **Report Tab:** Formatted executive summary

### Real-time Features
- Loading states during analysis
- Error handling with user-friendly messages
- Automatic data refresh after operations

### UI/UX
- **Glassmorphism Design:** Modern frosted glass aesthetic
- **Dark Theme:** Optimized for security/monitoring context
- **Responsive Layout:** Mobile, tablet, desktop support
- **Color-Coded Risk:** Red (high), orange (medium), green (low)

## Components

### ContentSubmit
Multi-method content submission form.

**Props:**
```typescript
interface ContentSubmitProps {
  onContentSubmit: (content: string, type: string, sourceUrl?: string) => void;
  onFileSubmit: (file: File) => void;
  isAnalyzing: boolean;
}
```

**Features:**
- Tab switcher (Text / URL / File)
- Content type selector (text, confluence_page, code, configuration)
- React Dropzone for file uploads
- Loading state during analysis

### ScanResults
Tabbed results container.

**Props:**
```typescript
interface ScanResultsProps {
  result: ScanResult;
  onNewScan: () => void;
}
```

**Features:**
- Summary stats cards (total, high/medium/low risk)
- 4 tabs (Credentials, Risk, Remediation, Report)
- Overall risk level display
- New scan button

### CredentialsList
Expandable credential findings.

**Props:**
```typescript
interface CredentialsListProps {
  credentials: CredentialFinding[];
}
```

**Features:**
- Severity badges (High/Medium/Low)
- Detection method badges (Pattern/AI)
- Expandable details (value preview, context, status)
- Confidence percentage
- Line number display

### RiskDashboard
Charts and risk visualization.

**Props:**
```typescript
interface RiskDashboardProps {
  riskAssessment: RiskAssessment;
  credentials: CredentialFinding[];
}
```

**Features:**
- Doughnut chart (risk distribution)
- Bar chart (credential types)
- Critical findings list
- Compliance violations alert

### RemediationPlan
Actionable remediation guidance.

**Props:**
```typescript
interface RemediationPlanProps {
  plan: RemediationAction[];
}
```

**Features:**
- Priority badges (Immediate/Urgent/Normal)
- Timeline estimates
- Immediate actions checklist
- Verification steps
- Prevention measures
- Notification templates

### ExecutiveReport
Formatted report viewer.

**Props:**
```typescript
interface ExecutiveReportProps {
  report: string;
}
```

**Features:**
- Markdown-style parsing
- Heading detection
- Bullet/numbered lists
- Paragraph formatting

### ScanHistory
Past scans browser.

**Props:**
```typescript
interface ScanHistoryProps {
  scans: ScanListItem[];
  onScanSelect: (scanId: string) => void;
  onScanDelete: (scanId: string) => void;
  onRefresh: () => void;
}
```

**Features:**
- Scan list with metadata
- Click to view results
- Delete with confirmation
- Refresh button

### StatsOverview
Dashboard statistics.

**Props:**
```typescript
interface StatsOverviewProps {
  stats: StatsResponse;
}
```

**Features:**
- Total scans count
- Total findings count
- High/medium risk counts
- Icon-coded metrics

## API Client

Located in `src/lib/api.ts`.

**Methods:**
```typescript
api.healthCheck()                            → HealthResponse
api.submitContent(submission)                → ScanSubmissionResponse
api.uploadFile(file, contentType?)           → ScanSubmissionResponse
api.analyzeScan(scanId)                      → ScanResult
api.getScanResult(scanId)                    → ScanResult
api.listScans(limit?, offset?)               → ScanListItem[]
api.deleteScan(scanId)                       → { message, scan_id }
api.getWorkflowGraph()                       → WorkflowGraph
api.getStats()                               → StatsResponse
```

## Styling

### Tailwind Configuration
Located in `tailwind.config.js`.

**Custom Colors:**
```javascript
colors: {
  risk: {
    high: '#ef4444',    // Red
    medium: '#f97316',  // Orange
    low: '#22c55e',     // Green
  }
}
```

### Global Styles
Located in `src/app/globals.css`.

**Custom Classes:**
- `.glass` - Basic glassmorphism
- `.glass-card` - Enhanced card with shadow
- `.risk-high` - High risk styling
- `.risk-medium` - Medium risk styling
- `.risk-low` - Low risk styling
- `.animate-pulse-slow` - Slow pulse animation

## Installation

```powershell
# Install dependencies
npm install

# Configure environment
Copy-Item .env.example .env.local
# Edit .env.local with API URL

# Start dev server
npm run dev

# Build for production
npm run build
npm start
```

## Environment Configuration

### .env.local
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note:** `NEXT_PUBLIC_` prefix exposes variable to browser.

## Development

### Start Dev Server
```powershell
npm run dev
```

Runs on http://localhost:3001 with:
- Hot module replacement
- Fast refresh
- Error overlay

### Build Production
```powershell
npm run build
```

Creates optimized build in `.next/` with:
- Minified JS/CSS
- Image optimization
- Static page generation

### Lint
```powershell
npm run lint
```

Checks for:
- TypeScript errors
- ESLint violations
- Unused imports

## TypeScript Types

Located in `src/types/index.ts`.

**Key Interfaces:**
```typescript
CredentialFinding      → Individual credential data
RiskAssessment         → Risk analysis results
RemediationAction      → Action plan item
ScanResult             → Complete scan output
ScanListItem           → Scan history item
WorkflowNode/Edge      → Workflow visualization
HealthResponse         → Health check data
StatsResponse          → Dashboard statistics
```

## State Management

Main page (`src/app/page.tsx`) uses React hooks:

```typescript
const [currentScan, setCurrentScan] = useState<ScanResult | null>(null);
const [scans, setScans] = useState<ScanListItem[]>([]);
const [stats, setStats] = useState<StatsResponse | null>(null);
const [isAnalyzing, setIsAnalyzing] = useState(false);
const [error, setError] = useState<string | null>(null);
const [view, setView] = useState<'submit' | 'results' | 'history'>('submit');
```

**Flow:**
1. User submits content → `handleContentSubmit()`
2. Call `api.submitContent()` → Get `scan_id`
3. Call `api.analyzeScan(scan_id)` → Get `ScanResult`
4. Update `currentScan` and switch to results view
5. Refresh scans list and stats

## Responsive Design

**Breakpoints:**
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

**Grid Layouts:**
- Stats: 2 cols mobile, 4 cols desktop
- Charts: 1 col mobile, 2 cols desktop
- Summary: Stacked mobile, flex desktop

## Charts

Using **Chart.js** with **react-chartjs-2**.

**Registered Components:**
```typescript
ChartJS.register(
  ArcElement,         // Doughnut chart
  CategoryScale,      // Bar chart X-axis
  LinearScale,        // Bar chart Y-axis
  BarElement,         // Bar chart bars
  Title,
  Tooltip,
  Legend
);
```

**Dark Theme:**
```typescript
plugins: {
  legend: {
    labels: { color: '#9ca3af' }
  }
},
scales: {
  y: {
    ticks: { color: '#9ca3af' },
    grid: { color: '#374151' }
  },
  x: {
    ticks: { color: '#9ca3af' },
    grid: { color: '#374151' }
  }
}
```

## Icons

Using **Lucide React** for consistent iconography.

**Common Icons:**
- `Shield` - Security/protection
- `AlertTriangle` - Warnings/high risk
- `CheckCircle2` - Success/completion
- `Upload` - File uploads
- `FileText` - Documents
- `Key` - Credentials
- `History` - Past scans
- `Trash2` - Delete actions

## Error Handling

**API Errors:**
```typescript
try {
  const result = await api.analyzeScan(scanId);
  setCurrentScan(result);
} catch (err: any) {
  setError(err.response?.data?.detail || 'Analysis failed');
}
```

**Display:**
- Error banner at top of page
- Red alert styling
- Dismissible with × button

## Accessibility

- Semantic HTML elements
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus states on all buttons/inputs
- High contrast colors
- Screen reader friendly

## Performance

### Optimization Techniques
- Next.js automatic code splitting
- Image optimization via `next/image`
- CSS-in-JS (Tailwind) for minimal bundle
- Tree shaking for unused code
- Static page generation where possible

### Bundle Size
- Main JS: ~200KB (gzipped)
- CSS: ~10KB (gzipped)
- Total First Load: ~250KB

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Testing

### Type Checking
```powershell
npx tsc --noEmit
```

### Lint
```powershell
npm run lint
```

### Manual Testing
1. Submit various content types
2. Test file uploads (all formats)
3. Verify error handling
4. Check responsive layout
5. Test scan history operations

## Deployment

### Vercel (Recommended)
```powershell
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Static Export
```powershell
# Build static files
npm run build
npx next export

# Deploy 'out/' directory to any static host
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

## Customization

### Change Theme Colors
Edit `tailwind.config.js`:
```javascript
colors: {
  risk: {
    high: '#your-color',
    medium: '#your-color',
    low: '#your-color',
  }
}
```

### Modify Layout
Edit `src/app/page.tsx`:
- Change grid columns
- Reorder components
- Add new sections

### Add New Component
1. Create `src/components/NewComponent.tsx`
2. Define props interface
3. Import in `page.tsx`
4. Use in render

## Troubleshooting

### Module not found errors
```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### Styles not applying
```powershell
Remove-Item -Recurse -Force .next
npm run dev
```

### API connection fails
- Check backend is running (http://localhost:8000/health)
- Verify `.env.local` has correct API URL
- Check browser console for CORS errors

### Build fails
```powershell
# Clean build
Remove-Item -Recurse -Force .next
npm run build
```

## Dependencies

### Core
- `next@14.0.4` - React framework
- `react@18.2.0` - UI library
- `react-dom@18.2.0` - DOM rendering

### Styling
- `tailwindcss@3.3.6` - Utility CSS
- `autoprefixer@10.4.16` - CSS prefixes
- `postcss@8.4.32` - CSS processing

### Data & Charts
- `axios@1.6.2` - HTTP client
- `chart.js@4.4.0` - Charts
- `react-chartjs-2@5.2.0` - Chart.js for React

### UI Components
- `lucide-react@0.294.0` - Icons
- `react-dropzone@14.2.3` - File uploads

### Dev Tools
- `typescript@5.3.2` - Type checking
- `eslint@8.56.0` - Linting
- `@types/*` - TypeScript definitions

## Resources

- Next.js Docs: https://nextjs.org/docs
- Tailwind Docs: https://tailwindcss.com/docs
- Chart.js Docs: https://www.chartjs.org/docs
- React Docs: https://react.dev
