# Ada Maritime AI - Web Dashboard

Modern web dashboard for Ada Maritime AI system.

## Features

- **Real-time Monitoring**: VHF communications, vessel tracking, marina operations
- **Compliance Dashboard**: VERIFY Agent status, violations, permits
- **Insurance Management**: Policy tracking, expiry alerts
- **Hot Work Permits**: Request, approve, monitor permits
- **Marina Operations**: Berth management, weather, maintenance
- **Interactive Maps**: Leaflet-based marina and vessel visualization
- **Mobile Responsive**: Works on desktop, tablet, and mobile

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Query** - Data fetching
- **Zustand** - State management
- **Recharts** - Data visualization
- **React Leaflet** - Maps
- **Lucide React** - Icons
- **Framer Motion** - Animations

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── Dashboard/   # Dashboard components
│   │   ├── Compliance/  # VERIFY Agent components
│   │   ├── VHF/         # VHF monitoring components
│   │   ├── Marina/      # Marina operations components
│   │   └── ui/          # Base UI components
│   ├── pages/           # Page components
│   │   ├── Dashboard.jsx
│   │   ├── Compliance.jsx
│   │   ├── VHFMonitor.jsx
│   │   ├── Insurance.jsx
│   │   └── Permits.jsx
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API services
│   ├── stores/          # Zustand stores
│   ├── utils/           # Utility functions
│   ├── App.jsx          # Main app component
│   └── main.jsx         # Entry point
├── public/              # Static assets
├── index.html           # HTML template
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind configuration
└── package.json         # Dependencies
```

## Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_MAPBOX_TOKEN=your_mapbox_token_here
```

## Development

```bash
# Run linter
npm run lint

# Format code
npm run format

# Type check (if using TypeScript)
npm run type-check
```

## API Integration

The dashboard connects to Ada Maritime AI REST API:

```javascript
import { apiClient } from './services/api'

// Verify vessel
const result = await apiClient.post('/api/v1/verify/vessel', {
  vessel_name: 'Sea Dream',
  vessel_registration: 'TR-123456',
  marina_id: 'marina_001'
})

// Get active permits
const permits = await apiClient.get('/api/v1/verify/permit/active', {
  params: { marina_id: 'marina_001' }
})
```

## WebSocket Integration

Real-time updates via WebSocket:

```javascript
import { useVHFMonitor } from './hooks/useVHFMonitor'

function VHFMonitor() {
  const { communications, isConnected } = useVHFMonitor()

  return (
    <div>
      {communications.map(comm => (
        <CommCard key={comm.id} data={comm} />
      ))}
    </div>
  )
}
```

## Deployment

```bash
# Build for production
npm run build

# Deploy to Netlify, Vercel, or serve with nginx
```

## Contributing

1. Create feature branch
2. Make changes
3. Run tests and linter
4. Submit pull request

## License

Proprietary - Ada Maritime AI
