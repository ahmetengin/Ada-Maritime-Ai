# Ada Maritime AI - Mobile Application

Mobile application for Ada Maritime AI system built with React Native and Expo.

## Features

- **Real-time VHF Monitoring**: Listen to ship-to-ship and marina communications
- **Vessel Compliance Dashboard**: View insurance status, violations, permits
- **Hot Work Permit Management**: Request, approve, monitor permits on-the-go
- **Marina Operations**: Berth availability, weather, maintenance alerts
- **Push Notifications**: Real-time alerts for violations, permit approvals, emergencies
- **Offline Mode**: Critical features available without internet
- **Map View**: Interactive marina and vessel locations

## Tech Stack

- **React Native** - Mobile framework
- **Expo** - Development platform
- **React Navigation** - Routing
- **Zustand** - State management
- **React Query** - Data fetching
- **React Native Maps** - Map integration
- **Axios** - HTTP client

## Quick Start

### Prerequisites

```bash
# Install Node.js 18+
node --version

# Install Expo CLI
npm install -g expo-cli

# Install EAS CLI (for builds)
npm install -g eas-cli
```

### Development

```bash
# Install dependencies
cd mobile
npm install

# Start development server
npm start

# Run on Android
npm run android

# Run on iOS
npm run ios

# Run on web
npm run web
```

### Testing on Device

1. Install **Expo Go** app on your phone
2. Scan QR code from terminal
3. App will load on your device

## Project Structure

```
mobile/
├── src/
│   ├── screens/          # Screen components
│   │   ├── Dashboard.tsx
│   │   ├── VHFMonitor.tsx
│   │   ├── Compliance.tsx
│   │   ├── Permits.tsx
│   │   └── Settings.tsx
│   ├── components/       # Reusable components
│   │   ├── VesselCard.tsx
│   │   ├── PermitCard.tsx
│   │   ├── ViolationAlert.tsx
│   │   └── VHFChannel.tsx
│   ├── navigation/       # Navigation configuration
│   ├── services/         # API services
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── stores/           # Zustand stores
│   ├── hooks/            # Custom hooks
│   ├── utils/            # Utilities
│   └── types/            # TypeScript types
├── assets/               # Images, fonts, icons
├── app.json              # Expo configuration
├── package.json          # Dependencies
└── tsconfig.json         # TypeScript config
```

## Environment Configuration

Create `.env` file:

```env
API_URL=http://your-api-url:8000
WS_URL=ws://your-api-url:8000/ws
```

For local development:
```env
API_URL=http://192.168.1.100:8000  # Your computer's IP
WS_URL=ws://192.168.1.100:8000/ws
```

## Key Features Implementation

### 1. Real-time VHF Monitoring

```typescript
import { useVHFMonitor } from './hooks/useVHFMonitor'

function VHFScreen() {
  const { communications, activeChannels } = useVHFMonitor()

  return (
    <View>
      {communications.map(comm => (
        <VHFChannelCard key={comm.id} data={comm} />
      ))}
    </View>
  )
}
```

### 2. Vessel Compliance Check

```typescript
import { useVesselCompliance } from './hooks/useVesselCompliance'

function ComplianceScreen() {
  const { vessels, violations } = useVesselCompliance('marina_001')

  return (
    <FlatList
      data={vessels}
      renderItem={({ item }) => <VesselCard vessel={item} />}
    />
  )
}
```

### 3. Push Notifications

```typescript
import * as Notifications from 'expo-notifications'

// Setup notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
})

// Listen for violations
useEffect(() => {
  const subscription = notificationService.onViolation((violation) => {
    Notifications.scheduleNotificationAsync({
      content: {
        title: '⚠️ Compliance Violation',
        body: `Article ${violation.article}: ${violation.description}`,
        data: { violation },
      },
      trigger: null,
    })
  })

  return () => subscription.unsubscribe()
}, [])
```

## Building for Production

### Android

```bash
# Build APK
eas build --platform android --profile preview

# Build AAB for Play Store
eas build --platform android --profile production
```

### iOS

```bash
# Build for TestFlight
eas build --platform ios --profile production

# Submit to App Store
eas submit --platform ios
```

## API Integration

```typescript
import axios from 'axios'
import { API_URL } from '@env'

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
})

// Verify vessel
const verifyVessel = async (vesselName: string, registration: string) => {
  const response = await apiClient.post('/api/v1/verify/vessel', {
    vessel_name: vesselName,
    vessel_registration: registration,
    marina_id: 'marina_001'
  })
  return response.data
}

// Request permit
const requestPermit = async (data: PermitRequest) => {
  const response = await apiClient.post('/api/v1/verify/permit/request', data)
  return response.data
}
```

## Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- VesselCard.test.tsx
```

## Troubleshooting

### Metro bundler issues
```bash
# Clear cache
expo start -c
```

### Network request failed
- Check API_URL is correct
- Ensure backend is running
- Check firewall settings
- Use your computer's local IP, not localhost

### Map not loading
- Add your Mapbox token to app.json
- Check location permissions

## Performance

- Use React.memo for heavy components
- Implement FlatList virtualization
- Enable Hermes engine (default in Expo)
- Optimize images with expo-optimize

## Security

- Store sensitive data in SecureStore
- Implement JWT authentication
- Use HTTPS in production
- Validate all user inputs

## Contributing

1. Create feature branch
2. Make changes
3. Test on both iOS and Android
4. Submit pull request

## License

Proprietary - Ada Maritime AI

## Support

For issues or questions, contact the development team.
