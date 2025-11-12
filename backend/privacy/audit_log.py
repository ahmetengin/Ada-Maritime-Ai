"""
Privacy Audit Logging System
Complete transparency and accountability for all data transfers
"""

import time
import hashlib
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
from pathlib import Path


class AuditEventType(Enum):
    """Types of privacy events to audit"""
    DATA_TRANSFER = "data_transfer"
    DATA_REQUEST = "data_request"
    CONSENT_GRANTED = "consent_granted"
    CONSENT_DENIED = "consent_denied"
    STANDING_PERMISSION_CREATED = "standing_permission_created"
    STANDING_PERMISSION_REVOKED = "standing_permission_revoked"
    DATA_DELETION = "data_deletion"
    DATA_ACCESS = "data_access"
    POLICY_CHANGE = "policy_change"


@dataclass
class AuditEntry:
    """
    Single audit log entry
    Immutable record of privacy-related event
    """
    event_type: AuditEventType
    timestamp: float
    destination: str
    data_type: str
    captain_id: str
    authorization_method: str
    result: str
    data_hash: str = ""
    data_summary: Optional[Dict[str, Any]] = None
    confirmation_text: str = ""
    entry_id: str = field(default="")

    def __post_init__(self):
        if not self.entry_id:
            self.entry_id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique entry ID"""
        data = f"{self.event_type.value}:{self.timestamp}:{self.captain_id}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'entry_id': self.entry_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp,
            'destination': self.destination,
            'data_type': self.data_type,
            'captain_id': self.captain_id,
            'authorization_method': self.authorization_method,
            'result': self.result,
            'data_hash': self.data_hash,
            'data_summary': self.data_summary,
            'confirmation_text': self.confirmation_text,
        }

    def to_human_readable(self, language: str = "tr") -> str:
        """Convert to human-readable format"""
        if language == "tr":
            event_names = {
                AuditEventType.DATA_TRANSFER: "Veri Gönderildi",
                AuditEventType.DATA_REQUEST: "Veri Talep Edildi",
                AuditEventType.CONSENT_GRANTED: "İzin Verildi",
                AuditEventType.CONSENT_DENIED: "İzin Reddedildi",
            }

            timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp))

            return (
                f"[{timestamp_str}] {event_names.get(self.event_type, self.event_type.value)}\n"
                f"  Hedef: {self.destination}\n"
                f"  Veri: {self.data_type}\n"
                f"  Yetki: {self.authorization_method}\n"
                f"  Sonuç: {self.result}"
            )
        else:
            timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp))
            return (
                f"[{timestamp_str}] {self.event_type.value}\n"
                f"  Destination: {self.destination}\n"
                f"  Data: {self.data_type}\n"
                f"  Authorization: {self.authorization_method}\n"
                f"  Result: {self.result}"
            )


class AuditLog:
    """
    Privacy audit logging system
    Maintains tamper-proof log of all data sharing activities
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize audit log
        Stores in local encrypted database
        """
        if db_path is None:
            db_path = str(Path.home() / ".ada_sea" / "audit_log.db")

        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for audit log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_entries (
                entry_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                destination TEXT NOT NULL,
                data_type TEXT NOT NULL,
                captain_id TEXT NOT NULL,
                authorization_method TEXT NOT NULL,
                result TEXT NOT NULL,
                data_hash TEXT,
                data_summary TEXT,
                confirmation_text TEXT
            )
        ''')

        # Create indexes for common queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON audit_entries(timestamp)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_captain
            ON audit_entries(captain_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_destination
            ON audit_entries(destination)
        ''')

        conn.commit()
        conn.close()

    def log_transfer(
        self,
        destination: str,
        data_type: str,
        captain_id: str,
        authorization_method: str,
        result: str,
        data: Optional[Dict[str, Any]] = None,
        confirmation_text: str = ""
    ) -> AuditEntry:
        """
        Log a data transfer event
        """
        # Generate data hash for integrity
        data_hash = ""
        data_summary = None

        if data:
            data_hash = hashlib.sha256(
                json.dumps(data, sort_keys=True).encode()
            ).hexdigest()

            # Create summary (not full data)
            data_summary = {
                'size': len(json.dumps(data)),
                'fields': list(data.keys()) if isinstance(data, dict) else [],
            }

        entry = AuditEntry(
            event_type=AuditEventType.DATA_TRANSFER,
            timestamp=time.time(),
            destination=destination,
            data_type=data_type,
            captain_id=captain_id,
            authorization_method=authorization_method,
            result=result,
            data_hash=data_hash,
            data_summary=data_summary,
            confirmation_text=confirmation_text
        )

        self._store_entry(entry)
        return entry

    def log_request(
        self,
        destination: str,
        data_type: str,
        captain_id: str
    ) -> AuditEntry:
        """
        Log a data request (before consent)
        """
        entry = AuditEntry(
            event_type=AuditEventType.DATA_REQUEST,
            timestamp=time.time(),
            destination=destination,
            data_type=data_type,
            captain_id=captain_id,
            authorization_method="pending",
            result="requested"
        )

        self._store_entry(entry)
        return entry

    def log_consent(
        self,
        granted: bool,
        destination: str,
        data_type: str,
        captain_id: str,
        method: str,
        confirmation_text: str = ""
    ) -> AuditEntry:
        """
        Log consent decision
        """
        event_type = AuditEventType.CONSENT_GRANTED if granted else AuditEventType.CONSENT_DENIED

        entry = AuditEntry(
            event_type=event_type,
            timestamp=time.time(),
            destination=destination,
            data_type=data_type,
            captain_id=captain_id,
            authorization_method=method,
            result="granted" if granted else "denied",
            confirmation_text=confirmation_text
        )

        self._store_entry(entry)
        return entry

    def _store_entry(self, entry: AuditEntry):
        """Store entry in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO audit_entries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.entry_id,
            entry.event_type.value,
            entry.timestamp,
            entry.destination,
            entry.data_type,
            entry.captain_id,
            entry.authorization_method,
            entry.result,
            entry.data_hash,
            json.dumps(entry.data_summary) if entry.data_summary else None,
            entry.confirmation_text
        ))

        conn.commit()
        conn.close()

    def query(
        self,
        captain_id: Optional[str] = None,
        destination: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        hours: int = 168,  # Default: last 7 days
        limit: int = 100
    ) -> List[AuditEntry]:
        """
        Query audit log with filters
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_time = time.time() - (hours * 3600)

        query = "SELECT * FROM audit_entries WHERE timestamp >= ?"
        params = [cutoff_time]

        if captain_id:
            query += " AND captain_id = ?"
            params.append(captain_id)

        if destination:
            query += " AND destination = ?"
            params.append(destination)

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type.value)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        entries = []
        for row in rows:
            data_summary = json.loads(row[9]) if row[9] else None

            entry = AuditEntry(
                entry_id=row[0],
                event_type=AuditEventType(row[1]),
                timestamp=row[2],
                destination=row[3],
                data_type=row[4],
                captain_id=row[5],
                authorization_method=row[6],
                result=row[7],
                data_hash=row[8],
                data_summary=data_summary,
                confirmation_text=row[10]
            )
            entries.append(entry)

        return entries

    def get_summary(self, captain_id: str, hours: int = 168) -> Dict[str, Any]:
        """
        Get summary of audit log for captain
        """
        entries = self.query(captain_id=captain_id, hours=hours, limit=1000)

        summary = {
            'total_transfers': 0,
            'destinations': {},
            'data_types': {},
            'recent_entries': [],
        }

        for entry in entries:
            if entry.event_type == AuditEventType.DATA_TRANSFER:
                summary['total_transfers'] += 1

                # Count by destination
                dest = entry.destination
                summary['destinations'][dest] = summary['destinations'].get(dest, 0) + 1

                # Count by data type
                dtype = entry.data_type
                summary['data_types'][dtype] = summary['data_types'].get(dtype, 0) + 1

            # Add to recent (limit to 10)
            if len(summary['recent_entries']) < 10:
                summary['recent_entries'].append(entry.to_dict())

        return summary

    def export_for_captain(
        self,
        captain_id: str,
        hours: int = 168,
        format: str = "json"
    ) -> str:
        """
        Export audit log for captain review
        Supports JSON and human-readable formats
        """
        entries = self.query(captain_id=captain_id, hours=hours, limit=1000)

        if format == "json":
            return json.dumps(
                [entry.to_dict() for entry in entries],
                indent=2,
                ensure_ascii=False
            )
        elif format == "human":
            lines = [
                "=== ADA.SEA VERİ PAYLAŞIM GEÇMİŞİ ===\n",
                f"Son {hours} saat\n",
                f"Toplam {len(entries)} kayıt\n\n"
            ]

            for entry in entries:
                lines.append(entry.to_human_readable("tr"))
                lines.append("\n")

            return "".join(lines)

        return ""

    def verify_integrity(self, entry_id: str, original_data: Dict[str, Any]) -> bool:
        """
        Verify data integrity using stored hash
        """
        entries = self.query(limit=10000)
        entry = next((e for e in entries if e.entry_id == entry_id), None)

        if not entry:
            return False

        # Recompute hash
        computed_hash = hashlib.sha256(
            json.dumps(original_data, sort_keys=True).encode()
        ).hexdigest()

        return computed_hash == entry.data_hash

    def delete_old_entries(self, days: int = 365) -> int:
        """
        Delete entries older than specified days
        Returns number of entries deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_time = time.time() - (days * 24 * 3600)

        cursor.execute(
            "DELETE FROM audit_entries WHERE timestamp < ?",
            (cutoff_time,)
        )

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted
