<template>
  <div class="observability-dashboard">
    <header class="dashboard-header">
      <div class="header-content">
        <h1>⚓ Ada Maritime AI - Multi-Agent Observability</h1>
        <div class="connection-status">
          <span :class="['status-indicator', connectionStatus]"></span>
          <span>{{ connectionStatusText }}</span>
          <span class="events-count">{{ events.length }} events</span>
        </div>
      </div>
    </header>

    <div class="dashboard-content">
      <!-- Filters -->
      <div class="filters">
        <div class="filter-group">
          <label>Source App:</label>
          <select v-model="filters.sourceApp">
            <option value="">All Apps</option>
            <option v-for="app in sourceApps" :key="app" :value="app">{{ app }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Session:</label>
          <select v-model="filters.sessionId">
            <option value="">All Sessions</option>
            <option v-for="session in sessions" :key="session" :value="session">
              {{ session.substring(0, 20) }}...
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Event Type:</label>
          <select v-model="filters.eventType">
            <option value="">All Types</option>
            <option value="UserPromptSubmit">User Prompt</option>
            <option value="PreToolUse">Pre Tool Use</option>
            <option value="PostToolUse">Post Tool Use</option>
            <option value="SubagentStart">Subagent Start</option>
            <option value="SubagentEnd">Subagent End</option>
          </select>
        </div>

        <button @click="clearFilters" class="btn-clear">Clear Filters</button>
        <button @click="clearEvents" class="btn-danger">Clear Events</button>
      </div>

      <!-- Activity Pulse -->
      <div class="activity-pulse">
        <canvas ref="pulseCanvas" width="1200" height="100"></canvas>
      </div>

      <!-- Events Timeline -->
      <div class="events-timeline" ref="timeline">
        <div v-if="filteredEvents.length === 0" class="no-events">
          <p>No events to display. Waiting for agent activity...</p>
        </div>

        <div
          v-for="event in filteredEvents"
          :key="event.id"
          :class="['event-card', `event-${event.eventType}`]"
        >
          <div class="event-header">
            <span class="event-type">{{ event.eventType }}</span>
            <span class="event-time">{{ formatTime(event.timestamp) }}</span>
          </div>

          <div class="event-meta">
            <span class="event-app">{{ event.sourceApp }}</span>
            <span class="event-session">{{ event.sessionId.substring(0, 12) }}</span>
          </div>

          <div class="event-data">
            <pre>{{ formatEventData(event.data) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      events: [],
      sessions: [],
      sourceApps: [],
      filters: {
        sourceApp: '',
        sessionId: '',
        eventType: '',
      },
      ws: null,
      connectionStatus: 'disconnected',
      activityData: [],
      maxEvents: 500,
    }
  },

  computed: {
    connectionStatusText() {
      return this.connectionStatus === 'connected' ? 'Connected' : 'Disconnected'
    },

    filteredEvents() {
      return this.events.filter(event => {
        if (this.filters.sourceApp && event.sourceApp !== this.filters.sourceApp) {
          return false
        }
        if (this.filters.sessionId && event.sessionId !== this.filters.sessionId) {
          return false
        }
        if (this.filters.eventType && event.eventType !== this.filters.eventType) {
          return false
        }
        return true
      })
    },
  },

  mounted() {
    this.connectWebSocket()
    this.fetchInitialData()
    this.startPulseAnimation()
  },

  beforeUnmount() {
    if (this.ws) {
      this.ws.close()
    }
  },

  methods: {
    connectWebSocket() {
      const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:4000/ws'

      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.connectionStatus = 'connected'
      }

      this.ws.onmessage = (message) => {
        const data = JSON.parse(message.data)

        if (data.type === 'event') {
          this.addEvent(data.event)
          this.recordActivity()
        }
      }

      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.connectionStatus = 'disconnected'

        // Reconnect after 3 seconds
        setTimeout(() => this.connectWebSocket(), 3000)
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.connectionStatus = 'error'
      }
    },

    async fetchInitialData() {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:4000'

        // Fetch recent events
        const eventsRes = await fetch(`${apiUrl}/events?limit=100`)
        const eventsData = await eventsRes.json()
        this.events = eventsData.events.reverse()

        // Fetch sessions
        const sessionsRes = await fetch(`${apiUrl}/sessions`)
        const sessionsData = await sessionsRes.json()
        this.sessions = sessionsData.sessions

        // Fetch source apps
        const sourcesRes = await fetch(`${apiUrl}/sources`)
        const sourcesData = await sourcesRes.json()
        this.sourceApps = sourcesData.sources

      } catch (error) {
        console.error('Error fetching initial data:', error)
      }
    },

    addEvent(event) {
      this.events.push(event)

      // Limit events to prevent memory issues
      if (this.events.length > this.maxEvents) {
        this.events.shift()
      }

      // Update sessions and sources
      if (!this.sessions.includes(event.sessionId)) {
        this.sessions.push(event.sessionId)
      }

      if (!this.sourceApps.includes(event.sourceApp)) {
        this.sourceApps.push(event.sourceApp)
      }

      // Auto-scroll to bottom
      this.$nextTick(() => {
        const timeline = this.$refs.timeline
        if (timeline) {
          timeline.scrollTop = timeline.scrollHeight
        }
      })
    },

    recordActivity() {
      this.activityData.push(Date.now())

      // Keep only last 100 activity points
      if (this.activityData.length > 100) {
        this.activityData.shift()
      }
    },

    startPulseAnimation() {
      const canvas = this.$refs.pulseCanvas
      if (!canvas) return

      const ctx = canvas.getContext('2d')

      const animate = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height)

        // Draw grid
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)'
        ctx.lineWidth = 1

        for (let i = 0; i < canvas.width; i += 50) {
          ctx.beginPath()
          ctx.moveTo(i, 0)
          ctx.lineTo(i, canvas.height)
          ctx.stroke()
        }

        // Draw activity pulse
        if (this.activityData.length > 1) {
          ctx.strokeStyle = '#00d4ff'
          ctx.lineWidth = 2
          ctx.beginPath()

          const now = Date.now()
          const timeWindow = 60000 // 1 minute

          this.activityData.forEach((timestamp, index) => {
            const age = now - timestamp
            if (age < timeWindow) {
              const x = canvas.width - (age / timeWindow) * canvas.width
              const intensity = 1 - (age / timeWindow)
              const y = canvas.height / 2 - intensity * 30

              if (index === 0) {
                ctx.moveTo(x, y)
              } else {
                ctx.lineTo(x, y)
              }
            }
          })

          ctx.stroke()
        }

        requestAnimationFrame(animate)
      }

      animate()
    },

    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString()
    },

    formatEventData(data) {
      return JSON.stringify(data, null, 2)
    },

    clearFilters() {
      this.filters = {
        sourceApp: '',
        sessionId: '',
        eventType: '',
      }
    },

    clearEvents() {
      if (confirm('Are you sure you want to clear all events?')) {
        this.events = []
        this.activityData = []
      }
    },
  },
}
</script>

<style scoped>
.observability-dashboard {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0a0e27;
}

.dashboard-header {
  background: linear-gradient(135deg, #1a1f3a 0%, #0f1729 100%);
  padding: 1.5rem 2rem;
  border-bottom: 2px solid #00d4ff;
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard-header h1 {
  font-size: 1.8rem;
  font-weight: 600;
  color: #00d4ff;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.9rem;
  color: #a8b3cf;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-indicator.connected {
  background: #00ff88;
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

.status-indicator.disconnected {
  background: #ff4444;
  box-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
}

.status-indicator.error {
  background: #ffaa00;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.events-count {
  background: rgba(0, 212, 255, 0.2);
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-weight: 600;
}

.dashboard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.filters {
  display: flex;
  gap: 1rem;
  padding: 1rem 2rem;
  background: #151a30;
  border-bottom: 1px solid #2a3250;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.9rem;
  color: #8891aa;
}

.filter-group select {
  background: #1f2540;
  border: 1px solid #2a3250;
  color: #e0e6ed;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-group select:hover {
  border-color: #00d4ff;
}

.btn-clear, .btn-danger {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.btn-clear {
  background: #2a3250;
  color: #e0e6ed;
}

.btn-clear:hover {
  background: #3a4260;
}

.btn-danger {
  background: #ff4444;
  color: white;
}

.btn-danger:hover {
  background: #ff6666;
}

.activity-pulse {
  padding: 1rem 2rem;
  background: #0d1225;
  border-bottom: 1px solid #2a3250;
}

.activity-pulse canvas {
  width: 100%;
  height: 100px;
  display: block;
  border-radius: 8px;
  background: #151a30;
}

.events-timeline {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 2rem;
}

.no-events {
  text-align: center;
  padding: 4rem 2rem;
  color: #5a6580;
  font-size: 1.1rem;
}

.event-card {
  background: #151a30;
  border-left: 4px solid #00d4ff;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  transition: all 0.2s;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.event-card:hover {
  background: #1a2040;
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.1);
}

.event-UserPromptSubmit {
  border-left-color: #00ff88;
}

.event-PreToolUse {
  border-left-color: #ffaa00;
}

.event-PostToolUse {
  border-left-color: #00d4ff;
}

.event-SubagentStart {
  border-left-color: #aa00ff;
}

.event-SubagentEnd {
  border-left-color: #ff00aa;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.event-type {
  font-weight: 600;
  font-size: 1rem;
  color: #00d4ff;
}

.event-time {
  font-size: 0.85rem;
  color: #8891aa;
}

.event-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
  font-size: 0.85rem;
}

.event-app {
  background: rgba(0, 212, 255, 0.2);
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  color: #00d4ff;
}

.event-session {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  color: #a8b3cf;
  font-family: monospace;
}

.event-data {
  background: #0a0e1a;
  border-radius: 6px;
  padding: 0.75rem;
  overflow-x: auto;
}

.event-data pre {
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 0.85rem;
  color: #c8d0e0;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Scrollbar styling */
.events-timeline::-webkit-scrollbar {
  width: 8px;
}

.events-timeline::-webkit-scrollbar-track {
  background: #0a0e27;
}

.events-timeline::-webkit-scrollbar-thumb {
  background: #2a3250;
  border-radius: 4px;
}

.events-timeline::-webkit-scrollbar-thumb:hover {
  background: #3a4260;
}
</style>
