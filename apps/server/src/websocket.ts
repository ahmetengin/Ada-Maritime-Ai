/**
 * WebSocket module for Ada Maritime AI Observability
 * Handles real-time event broadcasting to connected clients
 */

import { WebSocketServer, WebSocket } from "ws";
import type { Server } from "http";
import type { Event } from "./database";

export class ObservabilityWebSocket {
  private wss: WebSocketServer;
  private clients: Set<WebSocket>;

  constructor(server: Server) {
    this.wss = new WebSocketServer({ server, path: "/ws" });
    this.clients = new Set();

    this.wss.on("connection", (ws: WebSocket) => {
      console.log("✓ New WebSocket client connected");
      this.clients.add(ws);

      ws.on("close", () => {
        console.log("✗ WebSocket client disconnected");
        this.clients.delete(ws);
      });

      ws.on("error", (error) => {
        console.error("WebSocket error:", error);
        this.clients.delete(ws);
      });

      // Send welcome message
      ws.send(
        JSON.stringify({
          type: "connected",
          message: "Connected to Ada Maritime AI Observability",
          timestamp: new Date().toISOString(),
        })
      );
    });
  }

  broadcast(event: Event) {
    const message = JSON.stringify({
      type: "event",
      event,
    });

    this.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        try {
          client.send(message);
        } catch (error) {
          console.error("Error broadcasting to client:", error);
        }
      }
    });
  }

  getClientCount(): number {
    return this.clients.size;
  }

  close() {
    this.clients.forEach((client) => client.close());
    this.wss.close();
  }
}
