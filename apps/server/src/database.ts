/**
 * Database module for Ada Maritime AI Observability
 * Handles SQLite storage with WAL mode for concurrent access
 */

import Database from "better-sqlite3";
import type { Database as DatabaseType } from "better-sqlite3";
import { join } from "path";

export interface Event {
  id?: number;
  eventType: string;
  sourceApp: string;
  sessionId: string;
  timestamp: string;
  data: any;
}

export class ObservabilityDatabase {
  private db: DatabaseType;

  constructor(dbPath: string = "./observability.db") {
    this.db = new Database(dbPath);

    // Enable WAL mode for better concurrent access
    this.db.pragma("journal_mode = WAL");

    // Initialize schema
    this.initSchema();
  }

  private initSchema() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eventType TEXT NOT NULL,
        sourceApp TEXT NOT NULL,
        sessionId TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        data TEXT NOT NULL,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC);
      CREATE INDEX IF NOT EXISTS idx_events_session ON events(sessionId);
      CREATE INDEX IF NOT EXISTS idx_events_source ON events(sourceApp);
      CREATE INDEX IF NOT EXISTS idx_events_type ON events(eventType);
    `);
  }

  insertEvent(event: Event): number {
    const stmt = this.db.prepare(`
      INSERT INTO events (eventType, sourceApp, sessionId, timestamp, data)
      VALUES (?, ?, ?, ?, ?)
    `);

    const result = stmt.run(
      event.eventType,
      event.sourceApp,
      event.sessionId,
      event.timestamp,
      JSON.stringify(event.data)
    );

    return result.lastInsertRowid as number;
  }

  getEvents(
    limit: number = 100,
    sourceApp?: string,
    sessionId?: string,
    eventType?: string
  ): Event[] {
    let query = "SELECT * FROM events WHERE 1=1";
    const params: any[] = [];

    if (sourceApp) {
      query += " AND sourceApp = ?";
      params.push(sourceApp);
    }

    if (sessionId) {
      query += " AND sessionId = ?";
      params.push(sessionId);
    }

    if (eventType) {
      query += " AND eventType = ?";
      params.push(eventType);
    }

    query += " ORDER BY timestamp DESC LIMIT ?";
    params.push(limit);

    const stmt = this.db.prepare(query);
    const rows = stmt.all(...params) as any[];

    return rows.map((row) => ({
      id: row.id,
      eventType: row.eventType,
      sourceApp: row.sourceApp,
      sessionId: row.sessionId,
      timestamp: row.timestamp,
      data: JSON.parse(row.data),
    }));
  }

  getRecentEvents(limit: number = 100): Event[] {
    return this.getEvents(limit);
  }

  getSessions(): string[] {
    const stmt = this.db.prepare(`
      SELECT DISTINCT sessionId
      FROM events
      ORDER BY timestamp DESC
    `);

    const rows = stmt.all() as any[];
    return rows.map((row) => row.sessionId);
  }

  getSourceApps(): string[] {
    const stmt = this.db.prepare(`
      SELECT DISTINCT sourceApp
      FROM events
      ORDER BY sourceApp ASC
    `);

    const rows = stmt.all() as any[];
    return rows.map((row) => row.sourceApp);
  }

  clearOldEvents(daysToKeep: number = 7) {
    const stmt = this.db.prepare(`
      DELETE FROM events
      WHERE createdAt < datetime('now', '-' || ? || ' days')
    `);

    const result = stmt.run(daysToKeep);
    return result.changes;
  }

  close() {
    this.db.close();
  }
}
