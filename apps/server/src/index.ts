/**
 * Ada Maritime AI Observability Server
 * Real-time monitoring and visualization for multi-agent systems
 */

import { createServer, type IncomingMessage, type ServerResponse } from "http";
import { ObservabilityDatabase, type Event } from "./database";
import { ObservabilityWebSocket } from "./websocket";

const PORT = process.env.PORT || 4000;
const db = new ObservabilityDatabase();

// Create HTTP server
const server = createServer(async (req: IncomingMessage, res: ServerResponse) => {
  // Enable CORS
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(200);
    res.end();
    return;
  }

  // Health check
  if (req.url === "/health" && req.method === "GET") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "healthy", timestamp: new Date().toISOString() }));
    return;
  }

  // POST /events - Receive new event
  if (req.url === "/events" && req.method === "POST") {
    let body = "";

    req.on("data", (chunk) => {
      body += chunk.toString();
    });

    req.on("end", () => {
      try {
        const event: Event = JSON.parse(body);

        // Validate event
        if (!event.eventType || !event.sourceApp || !event.sessionId) {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "Missing required fields" }));
          return;
        }

        // Insert into database
        const eventId = db.insertEvent(event);

        // Broadcast to WebSocket clients
        wsServer.broadcast({ ...event, id: eventId });

        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ success: true, eventId }));

        console.log(`📊 Event received: ${event.eventType} from ${event.sourceApp}`);
      } catch (error) {
        console.error("Error processing event:", error);
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Internal server error" }));
      }
    });

    return;
  }

  // GET /events - Retrieve events
  if (req.url?.startsWith("/events") && req.method === "GET") {
    try {
      const url = new URL(req.url, `http://localhost:${PORT}`);
      const limit = parseInt(url.searchParams.get("limit") || "100");
      const sourceApp = url.searchParams.get("sourceApp") || undefined;
      const sessionId = url.searchParams.get("sessionId") || undefined;
      const eventType = url.searchParams.get("eventType") || undefined;

      const events = db.getEvents(limit, sourceApp, sessionId, eventType);

      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ events, count: events.length }));
    } catch (error) {
      console.error("Error retrieving events:", error);
      res.writeHead(500, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Internal server error" }));
    }

    return;
  }

  // GET /sessions - Get all session IDs
  if (req.url === "/sessions" && req.method === "GET") {
    try {
      const sessions = db.getSessions();
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ sessions }));
    } catch (error) {
      console.error("Error retrieving sessions:", error);
      res.writeHead(500, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Internal server error" }));
    }

    return;
  }

  // GET /sources - Get all source apps
  if (req.url === "/sources" && req.method === "GET") {
    try {
      const sources = db.getSourceApps();
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ sources }));
    } catch (error) {
      console.error("Error retrieving sources:", error);
      res.writeHead(500, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Internal server error" }));
    }

    return;
  }

  // 404 Not Found
  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: "Not found" }));
});

// Initialize WebSocket server
const wsServer = new ObservabilityWebSocket(server);

// Start server
server.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════════╗
║  Ada Maritime AI - Observability Server                      ║
╟───────────────────────────────────────────────────────────────╢
║  HTTP Server: http://localhost:${PORT}                          ║
║  WebSocket:   ws://localhost:${PORT}/ws                         ║
║  Status:      Running ✓                                       ║
╚═══════════════════════════════════════════════════════════════╝
  `);
});

// Graceful shutdown
process.on("SIGINT", () => {
  console.log("\n\nShutting down gracefully...");
  wsServer.close();
  db.close();
  server.close(() => {
    console.log("Server closed ✓");
    process.exit(0);
  });
});

process.on("SIGTERM", () => {
  console.log("\n\nShutting down gracefully...");
  wsServer.close();
  db.close();
  server.close(() => {
    console.log("Server closed ✓");
    process.exit(0);
  });
});
