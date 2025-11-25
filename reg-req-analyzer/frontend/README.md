# Regulatory Requirements Analyzer - Frontend

Modern Next.js frontend for the Regulatory Requirements Analyzer with real-time analysis visualization.

## Features

- 🎨 Modern UI with glassmorphism effects and gradient backgrounds
- 📁 Drag-and-drop document upload (PDF, DOCX, TXT)
- ⚡ Real-time analysis status tracking
- 📊 Interactive visualization of:
  - Laws, Rules & Regulations (LRR) with severity badges
  - Taxonomy impact assessments
  - Risk assessment dashboard
  - Workflow graph visualization
- 🎯 Document management with list and delete capabilities
- 💾 Type-safe API client with TypeScript
- 🎨 Tailwind CSS with custom regulatory color scheme

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript 5.3
- **Styling**: Tailwind CSS 3.3
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **File Upload**: React Dropzone

## Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend server running on `http://localhost:8000` (or custom URL)

## Installation

```bash
# Install dependencies
npm install

# Or with yarn
yarn install

# Or with pnpm
pnpm install
```

## Environment Configuration

Create a `.env.local` file:

```env
# Backend API URL (optional, defaults to http://localhost:8000)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

```bash
# Start development server (runs on http://localhost:3000)
npm run dev

# Or with yarn
yarn dev

# Or with pnpm
pnpm dev
```

Visit [http://localhost:3000](http://localhost:3000) to access the application.

## Building for Production

```bash
# Build optimized production bundle
npm run build

# Start production server
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout with header
│   │   ├── page.tsx            # Main page with state management
│   │   └── globals.css         # Global styles & Tailwind
│   ├── components/             # React components
│   │   ├── DocumentUpload.tsx  # File upload with dropzone
│   │   ├── DocumentsList.tsx   # Document list & selection
│   │   ├── AnalysisResults.tsx # Results display with tabs
│   │   ├── RiskAssessment.tsx  # Risk dashboard
│   │   └── WorkflowVisualization.tsx  # Graph display
│   ├── lib/                    # Utilities
│   │   └── api.ts              # Axios API client
│   └── types/                  # TypeScript definitions
│       └── index.ts            # All type definitions
├── public/                     # Static assets
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript config
├── tailwind.config.js          # Tailwind CSS config
├── next.config.js              # Next.js config
└── postcss.config.js           # PostCSS config
```

## Component Overview

### Main Page (`app/page.tsx`)
- State management for documents and analysis
- Server health check
- Coordinates all child components

### DocumentUpload (`components/DocumentUpload.tsx`)
- Drag-and-drop file upload
- Metadata form (source, regulator, document type)
- Upload status indicators

### AnalysisResults (`components/AnalysisResults.tsx`)
- Tabbed interface for results
- LRR display with badges
- Taxonomy impacts visualization
- Executive summary

### RiskAssessment (`components/RiskAssessment.tsx`)
- Overall risk level indicator
- Categorized risk lists (high/medium/low)
- Summary statistics

### DocumentsList (`components/DocumentsList.tsx`)
- List of uploaded documents
- Document selection
- Delete functionality

### WorkflowVisualization (`components/WorkflowVisualization.tsx`)
- Visual workflow graph
- Node descriptions
- Edge connections

## API Client

The `lib/api.ts` module provides typed functions for all backend endpoints:

```typescript
import {
  healthCheck,
  uploadDocument,
  analyzeDocument,
  getAnalysisResults,
  listDocuments,
  deleteDocument,
  getWorkflowGraph
} from '@/lib/api'

// Check server status
const health = await healthCheck()

// Upload document
const { document_id } = await uploadDocument(file, {
  source: 'European Commission',
  regulator: 'ESMA',
  document_type: 'regulation'
})

// Start analysis
await analyzeDocument(document_id)

// Get results
const results = await getAnalysisResults(document_id)
```

## Styling

Custom Tailwind CSS utilities are defined in `globals.css`:

- `.card` - Card container with glassmorphism
- `.btn-primary` - Primary button with gradient
- `.btn-secondary` - Secondary button outline
- `.badge-law` - Green badge for laws
- `.badge-rule` - Blue badge for rules
- `.badge-regulation` - Purple badge for regulations
- `.badge-high/medium/low` - Risk severity badges

## TypeScript Types

All API types are centrally defined in `src/types/index.ts`:

```typescript
interface AnalysisResult {
  document_id: string
  document_metadata: DocumentMetadata
  identified_lrr: LRRItem[]
  taxonomy_impacts: TaxonomyImpact[]
  risk_assessment?: RiskAssessment
  summary: string
  // ... more fields
}
```

## Troubleshooting

### Backend Connection Issues

```typescript
// Check if backend is running
curl http://localhost:8000/api/v1/health

// Or visit in browser:
// http://localhost:8000/docs (FastAPI Swagger UI)
```

### TypeScript Errors

```bash
# Check for type errors
npm run type-check

# Or run build (includes type checking)
npm run build
```

### Styling Issues

```bash
# Rebuild Tailwind CSS
npm run dev
# (Tailwind watches for changes automatically in dev mode)
```

## Performance

- Next.js automatic code splitting
- Image optimization with `next/image`
- API response caching (add if needed)
- Lazy loading for large result sets

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL
```

### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### Build Docker image

```bash
docker build -t reg-analyzer-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://api:8000 reg-analyzer-frontend
```

## Future Enhancements

- [ ] Add dark mode support
- [ ] Implement caching for analysis results
- [ ] Add export to PDF/Excel functionality
- [ ] Real-time WebSocket updates for analysis progress
- [ ] Multi-document comparison view
- [ ] User authentication and document history
- [ ] Customizable dashboards
- [ ] Advanced filtering and search

## License

Private - Internal Use Only
