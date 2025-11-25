# GitLab Interrogator Frontend

Next.js 14 frontend for the GitLab Interrogator AI agent.

## Architecture

```
Frontend Structure:
├── app/
│   ├── layout.tsx              # Root layout with providers
│   ├── page.tsx                # Main dashboard page
│   ├── providers.tsx           # React Query provider
│   └── globals.css             # Global styles
├── components/
│   ├── Header.tsx              # App header with status
│   ├── ProjectSelector.tsx     # GitLab project dropdown
│   ├── UseCaseTabs.tsx         # 4 use-case navigation
│   ├── StatsOverview.tsx       # Project statistics cards
│   ├── StoryCreator.tsx        # User story generation module
│   ├── SprintAnalyzer.tsx      # Sprint summary module
│   ├── ReleaseNotesGenerator.tsx  # Release notes module
│   └── EpicCategorizer.tsx     # Epic categorization module
├── lib/
│   └── api.ts                  # API client wrapper
├── types/
│   └── index.ts                # TypeScript type definitions
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Technology Stack

- **Next.js 14**: React framework with App Router
- **React 18**: UI library
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first styling
- **React Query**: Data fetching and caching
- **Axios**: HTTP client
- **Lucide React**: Icon library
- **Chart.js**: Charting (future sprint analytics)

## Features by Module

### 1. Story Creator (`StoryCreator.tsx`)

**Features:**
- Requirements input textarea
- Optional context field
- Real-time generation with loading state
- Formatted story preview with:
  - Title
  - Description (As a... I want... So that...)
  - Acceptance criteria (Given/When/Then)
  - Story points (Fibonacci scale)
  - Suggested labels
- GitLab issue payload (JSON)
- Execution trace viewer
- Copy to clipboard functionality

**State Management:**
```typescript
const [requirement, setRequirement] = useState('');
const [context, setContext] = useState('');
const [result, setResult] = useState<StoryCreationResult | null>(null);

const createStoryMutation = useMutation({
  mutationFn: api.createUserStory,
  onSuccess: (data) => setResult(data)
});
```

### 2. Sprint Analyzer (`SprintAnalyzer.tsx`)

**Features:**
- Milestone/sprint selector dropdown
- AI-powered sprint analysis
- Assessment banner (Good/Fair/Needs Improvement)
- Metrics dashboard:
  - Velocity (story points)
  - Completion rate (%)
  - Completed/total issues
  - Merge requests count
- Key achievements list
- Blockers and risks section
- Recommendations for next sprint
- Full Markdown report viewer

**Metrics Display:**
```tsx
<MetricCard label="Velocity" value={velocity} unit="pts" color="blue" />
<MetricCard label="Completion" value={rate} unit="%" color="green" />
```

### 3. Release Notes Generator (`ReleaseNotesGenerator.tsx`)

**Features:**
- Version/tag name input
- Optional date range filter
- Categorized change list:
  - ✨ Features
  - 🐛 Bug Fixes
  - ⚠️ Breaking Changes
  - 📝 Notable Changes
- Contributor list
- Statistics cards (feature count, fix count, etc.)
- Full Markdown preview
- Download as `.md` file

**Download Functionality:**
```typescript
const downloadMarkdown = () => {
  const blob = new Blob([result.markdown], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `release-notes-${result.version}.md`;
  a.click();
};
```

### 4. Epic Categorizer (`EpicCategorizer.tsx`)

**Features:**
- One-click categorization
- Category-based epic grouping
- Confidence scores for each epic
- Rationale for categorization decisions
- Suggested new categories
- Expandable epic cards
- Markdown report export

**Category Display:**
```tsx
{Object.entries(categorized).map(([category, epics]) => (
  <CategorySection
    category={category}
    epics={epics}
    count={epics.length}
  />
))}
```

## Shared Components

### Header (`Header.tsx`)

- App branding and logo
- Real-time health status indicator:
  - 🟢 Healthy (backend + GitLab connected)
  - 🟡 Degraded (backend connected, GitLab not configured)
  - 🔴 Down (backend unreachable)

### Project Selector (`ProjectSelector.tsx`)

- Fetches GitLab projects via API
- Dropdown with project names and paths
- Selected project info card with description
- Link to GitLab project page

### Use Case Tabs (`UseCaseTabs.tsx`)

- 4 tab navigation:
  - 📝 User Stories
  - 📈 Sprint Summary
  - 📄 Release Notes
  - 📁 Epic Categorization
- Active tab highlighting
- Icon indicators

### Stats Overview (`StatsOverview.tsx`)

- Project-level statistics:
  - Total issues
  - Closed issues
  - Open issues
  - Completion rate
- Color-coded metric cards

## API Integration

### API Client (`lib/api.ts`)

Singleton Axios instance with:
- Base URL configuration
- 2-minute timeout for AI processing
- Response interceptor for error handling
- TypeScript type safety

**Example Usage:**
```typescript
import { api } from '@/lib/api';

// Create user story
const result = await api.createUserStory({
  requirement: "Add password reset",
  project_id: 123
});

// Summarize sprint
const summary = await api.summarizeSprint({
  project_id: 123,
  milestone_id: 456
});
```

### React Query Integration

**Configuration:**
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      refetchOnWindowFocus: false
    }
  }
});
```

**Queries:**
```typescript
// Fetch projects
const { data: projects, isLoading, error } = useQuery({
  queryKey: ['projects'],
  queryFn: () => api.listProjects()
});

// Fetch milestones
const { data: milestones } = useQuery({
  queryKey: ['milestones', projectId],
  queryFn: () => api.listMilestones(projectId)
});
```

**Mutations:**
```typescript
const createStoryMutation = useMutation({
  mutationFn: api.createUserStory,
  onSuccess: (data) => {
    console.log('Story created:', data.title);
  },
  onError: (error) => {
    console.error('Story creation failed:', error);
  }
});
```

## Styling

### Tailwind CSS Configuration

**Custom Colors:**
```javascript
colors: {
  agile: {
    story: '#3b82f6',    // Blue
    sprint: '#10b981',   // Green
    release: '#8b5cf6',  // Purple
    epic: '#f59e0b',     // Orange
    completed: '#22c55e',
    inprogress: '#f97316',
    blocked: '#ef4444',
    backlog: '#6b7280'
  }
}
```

**Custom Components:**
```css
.story-card {
  @apply bg-white border border-gray-200 rounded-lg p-4 
         shadow-sm hover:shadow-md transition-shadow;
}

.sprint-metric {
  @apply bg-gradient-to-br from-white to-gray-50 
         border border-gray-200 rounded-lg p-6;
}

.epic-badge {
  @apply inline-flex items-center px-3 py-1 
         rounded-full text-sm font-medium;
}
```

### Animations

```css
.fade-in {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

## Type Safety

### TypeScript Interfaces

All API request/response models have TypeScript interfaces:

```typescript
export interface StoryCreationRequest {
  requirement: string;
  project_id: number;
  context?: string;
}

export interface StoryCreationResult {
  task_id: string;
  title: string;
  description: string;
  labels: string[];
  story_points: number;
  gitlab_payload: {...};
  execution_trace: ExecutionTraceStep[];
}
```

### Type Imports

```typescript
import type {
  GitLabProject,
  GitLabMilestone,
  SprintSummary,
  ReleaseNotes,
  EpicCategorization,
  UseCaseTab
} from '@/types';
```

## Development

### Local Development

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Environment Configuration

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_GITLAB_INTEGRATION=true
NEXT_PUBLIC_ENABLE_CHARTS=true
```

### Hot Reload

Next.js automatically hot-reloads on file changes:
- Component changes: Fast refresh
- API route changes: Server restart
- Config changes: Full reload required

## Error Handling

### API Error Display

```tsx
{error && (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
    <p className="text-sm text-red-800">
      Error: {error.message}
    </p>
  </div>
)}
```

### Loading States

```tsx
{isLoading ? (
  <div className="flex items-center space-x-2">
    <Loader2 className="w-5 h-5 animate-spin" />
    <span>Loading...</span>
  </div>
) : (
  <Content />
)}
```

### Empty States

```tsx
{!selectedProject ? (
  <div className="text-center py-12">
    <GitBranch className="w-16 h-16 text-gray-300 mx-auto mb-4" />
    <h3 className="text-lg font-medium text-gray-900 mb-2">
      Select a GitLab Project
    </h3>
    <p className="text-gray-600">
      Choose a project from the dropdown above to get started
    </p>
  </div>
) : (
  <ActiveModule />
)}
```

## Accessibility

- Semantic HTML (`<header>`, `<main>`, `<nav>`, `<section>`)
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus indicators
- Color contrast (WCAG AA)

## Performance Optimization

### Code Splitting

Next.js automatically code-splits by route:
- Each page is a separate bundle
- Dynamic imports for heavy components

### Image Optimization

```tsx
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="GitLab Interrogator"
  width={200}
  height={50}
  priority
/>
```

### React Query Caching

- 1-minute stale time for queries
- Automatic background refetching
- Optimistic updates for mutations

## Testing

### Component Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import StoryCreator from '@/components/StoryCreator';

test('renders requirement input', () => {
  render(<StoryCreator project={mockProject} />);
  expect(screen.getByLabelText(/requirement/i)).toBeInTheDocument();
});

test('submits form on button click', async () => {
  render(<StoryCreator project={mockProject} />);
  
  fireEvent.change(screen.getByLabelText(/requirement/i), {
    target: { value: 'Add password reset' }
  });
  
  fireEvent.click(screen.getByText(/generate/i));
  
  // Assert mutation was called
});
```

### E2E Tests (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test('create user story flow', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Select project
  await page.selectOption('[id="project-select"]', '123');
  
  // Navigate to story tab
  await page.click('text=User Stories');
  
  // Fill requirement
  await page.fill('[id="requirement"]', 'Add password reset');
  
  // Submit
  await page.click('text=Generate User Story');
  
  // Verify result
  await expect(page.locator('text=Story Generated')).toBeVisible();
});
```

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

**Environment Variables:**
- Set `NEXT_PUBLIC_API_URL` in Vercel dashboard
- Auto-deploys on git push to main branch

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

```bash
docker build -t gitlab-interrogator-frontend .
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://backend:8000 \
  gitlab-interrogator-frontend
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Future Enhancements

- [ ] Chart.js velocity/burndown charts
- [ ] Real-time notifications via WebSocket
- [ ] Dark mode toggle
- [ ] Export to PDF
- [ ] GitLab OAuth integration
- [ ] Batch story creation wizard
- [ ] Sprint comparison view
- [ ] Epic roadmap timeline
- [ ] Historical analytics dashboard

---

For setup instructions, see [../SETUP_GUIDE.md](../SETUP_GUIDE.md)
