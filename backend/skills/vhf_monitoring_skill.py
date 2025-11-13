"""
VHF Monitoring Skill - Ada Observer

Real-time VHF radio monitoring for:
- Intership communications (gemiden gemiye)
- Marina operations
- Safety broadcasts
- Race net monitoring
- SDR integration

Monitors channels: 6, 8, 9, 10, 12, 13, 16, 72, 73, 77
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

try:
    from .base_skill import BaseSkill, SkillMetadata
    from ..database.models import (
        VHFChannel, MarinaVHFConfig, IntershipCommunication,
        VHFMonitoringSession, VHFChannelType
    )
    from ..logger import setup_logger
except ImportError:
    from base_skill import BaseSkill, SkillMetadata
    from database.models import (
        VHFChannel, MarinaVHFConfig, IntershipCommunication,
        VHFMonitoringSession, VHFChannelType
    )
    from logger import setup_logger


logger = setup_logger(__name__)


class VHFMonitoringSkill(BaseSkill):
    """
    VHF Monitoring Skill for Ada Observer

    Capabilities:
    - Load and manage VHF channel database
    - Monitor intership communications
    - Track marina-specific channels
    - Provide SDR scanning profiles
    - Log detected communications
    - Support race net monitoring
    """

    def __init__(self):
        super().__init__()
        self.channels: Dict[int, VHFChannel] = {}
        self.marinas: Dict[str, MarinaVHFConfig] = {}
        self.communications: Dict[str, IntershipCommunication] = {}
        self.active_sessions: Dict[str, VHFMonitoringSession] = {}

        # Load VHF channel configuration
        self._load_vhf_database()

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="vhf_monitoring",
            description="VHF radio monitoring for intership communications and marina operations",
            version="1.0.0",
            author="Ada Maritime AI - Observer System",
            requires_database=True
        )

    def _load_vhf_database(self) -> None:
        """Load VHF channel database from configuration"""
        try:
            config_path = Path(__file__).parent.parent / "config" / "vhf_channels_turkey.json"

            if not config_path.exists():
                logger.warning(f"VHF database not found: {config_path}")
                return

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Load standard channels
            if "standard_channels" in config:
                # Distress channel
                distress = config["standard_channels"]["distress"]
                self.channels[distress["channel"]] = VHFChannel(
                    channel_number=distress["channel"],
                    frequency_mhz=distress["frequency"],
                    channel_type=distress["type"],
                    usage_description=distress["description"],
                    mode="simplex",
                    power_restriction=distress.get("power"),
                    is_priority=True,
                    notes=distress.get("notes")
                )

                # Intership channels
                for channel_data in config["standard_channels"]["intership"]:
                    self.channels[channel_data["channel"]] = VHFChannel(
                        channel_number=channel_data["channel"],
                        frequency_mhz=channel_data["frequency"],
                        channel_type=channel_data["type"],
                        usage_description=channel_data["description"],
                        mode="simplex",
                        power_restriction=channel_data.get("power"),
                        region="turkey",
                        notes=channel_data.get("notes")
                    )

                # Working channels
                for channel_data in config["standard_channels"]["working"]:
                    self.channels[channel_data["channel"]] = VHFChannel(
                        channel_number=channel_data["channel"],
                        frequency_mhz=channel_data["frequency"],
                        channel_type=channel_data["type"],
                        usage_description=channel_data["description"],
                        mode="simplex"
                    )

            # Load marina configurations
            if "turkey_marinas" in config:
                for marina_data in config["turkey_marinas"]:
                    vhf = marina_data["vhf_config"]
                    self.marinas[marina_data["marina_id"]] = MarinaVHFConfig(
                        marina_id=marina_data["marina_id"],
                        marina_name=marina_data["name"],
                        primary_channel=vhf["primary_channel"],
                        primary_frequency=vhf["primary_frequency"],
                        working_channels=vhf.get("working_channels", []),
                        intership_channels=vhf.get("intership_channels", []),
                        monitoring_channels=vhf.get("monitoring_channels", []),
                        call_sign=vhf.get("call_sign"),
                        operating_hours=vhf.get("operating_hours"),
                        languages=vhf.get("languages", ["Turkish", "English"]),
                        notes=vhf.get("notes")
                    )

            logger.info(f"Loaded {len(self.channels)} VHF channels and {len(self.marinas)} marina configs")

        except Exception as e:
            logger.error(f"Failed to load VHF database: {e}")

    async def execute(self, params: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        """Execute VHF monitoring operation"""
        operation = params.get("operation", "get_channels")

        if operation == "get_channels":
            return await self._get_channels(params, context)
        elif operation == "get_marina_channels":
            return await self._get_marina_channels(params, context)
        elif operation == "get_intership_channels":
            return await self._get_intership_channels(params, context)
        elif operation == "start_monitoring":
            return await self._start_monitoring(params, context)
        elif operation == "stop_monitoring":
            return await self._stop_monitoring(params, context)
        elif operation == "log_communication":
            return await self._log_communication(params, context)
        elif operation == "get_scanning_profile":
            return await self._get_scanning_profile(params, context)
        elif operation == "get_active_sessions":
            return await self._get_active_sessions(params, context)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    async def _get_channels(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Get VHF channels

        Optional params:
        - channel_type: Filter by type (intership, marina, distress, etc.)
        - region: Filter by region
        """
        channel_type = params.get("channel_type")
        region = params.get("region")

        channels = list(self.channels.values())

        if channel_type:
            channels = [c for c in channels if c.channel_type == channel_type]

        if region:
            channels = [c for c in channels if c.region == region]

        return {
            "success": True,
            "total_channels": len(channels),
            "channels": [
                {
                    "channel": c.channel_number,
                    "frequency": c.frequency_mhz,
                    "type": c.channel_type,
                    "description": c.usage_description,
                    "display": c.get_display_name(),
                    "is_priority": c.is_priority,
                    "notes": c.notes
                }
                for c in sorted(channels, key=lambda x: x.channel_number)
            ]
        }

    async def _get_marina_channels(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Get marina-specific VHF channels

        Required params:
        - marina_id: Marina identifier
        """
        marina_id = params.get("marina_id")

        if not marina_id:
            return {
                "success": False,
                "error": "marina_id is required"
            }

        if marina_id not in self.marinas:
            return {
                "success": False,
                "error": f"Marina {marina_id} not found in database"
            }

        marina = self.marinas[marina_id]

        return {
            "success": True,
            "marina_id": marina_id,
            "marina_name": marina.marina_name,
            "vhf_config": {
                "primary_channel": marina.primary_channel,
                "primary_frequency": marina.primary_frequency,
                "call_sign": marina.call_sign,
                "working_channels": marina.working_channels,
                "intership_channels": marina.intership_channels,
                "monitoring_channels": marina.monitoring_channels,
                "operating_hours": marina.operating_hours,
                "languages": marina.languages,
                "all_channels": marina.get_all_channels()
            },
            "notes": marina.notes
        }

    async def _get_intership_channels(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Get all intership communication channels"""
        intership = [c for c in self.channels.values() if c.is_intership_channel()]

        return {
            "success": True,
            "total_channels": len(intership),
            "priority_channels": [6, 72, 73],  # Most used in Turkey
            "channels": [
                {
                    "channel": c.channel_number,
                    "frequency": c.frequency_mhz,
                    "description": c.usage_description,
                    "power": c.power_restriction,
                    "notes": c.notes
                }
                for c in sorted(intership, key=lambda x: x.channel_number)
            ],
            "usage_notes": {
                "6": "Most common intership in Turkey - operational safety",
                "72": "General ship-to-ship - very popular",
                "73": "Yacht & marina intership - Ataköy, Göcek, Bodrum",
                "77": "Short-range - tender/mooring assistance"
            }
        }

    async def _start_monitoring(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Start VHF monitoring session

        Optional params:
        - channels: List of channels to monitor (default: priority intership)
        - mode: passive, active, race_net
        - vessel_name: Name of monitoring vessel
        - location: {"lat": float, "lon": float}
        """
        session_id = str(uuid.uuid4())

        channels = params.get("channels", [16, 6, 72, 73])
        mode = params.get("mode", "passive")
        vessel_name = params.get("vessel_name")
        location = params.get("location")

        session = VHFMonitoringSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            channels_monitored=channels,
            location=location,
            vessel_name=vessel_name,
            mode=mode,
            priority_channels=[16, 72, 73],
            scan_interval_seconds=1.0 if mode == "passive" else 0.5
        )

        self.active_sessions[session_id] = session

        logger.info(f"Started VHF monitoring session: {session_id}, mode={mode}, channels={channels}")

        return {
            "success": True,
            "session_id": session_id,
            "mode": mode,
            "channels": channels,
            "start_time": session.start_time,
            "monitoring_info": {
                "channel_16": "ALWAYS monitored (distress/safety)",
                "intership_channels": [c for c in channels if c in [6, 72, 73, 77]],
                "scan_interval": f"{session.scan_interval_seconds}s"
            },
            "channel_details": [
                {
                    "channel": ch,
                    "frequency": self.channels[ch].frequency_mhz if ch in self.channels else None,
                    "type": self.channels[ch].channel_type if ch in self.channels else "unknown"
                }
                for ch in channels
            ]
        }

    async def _stop_monitoring(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Stop VHF monitoring session

        Required params:
        - session_id: Session to stop
        """
        session_id = params.get("session_id")

        if not session_id or session_id not in self.active_sessions:
            return {
                "success": False,
                "error": "Session not found or invalid session_id"
            }

        session = self.active_sessions[session_id]
        session.end_time = datetime.now().isoformat()
        session.is_active = False

        duration = session.get_duration_minutes()

        logger.info(f"Stopped VHF monitoring session: {session_id}, duration={duration}min")

        return {
            "success": True,
            "session_id": session_id,
            "end_time": session.end_time,
            "duration_minutes": duration,
            "total_communications_detected": len(session.detected_communications),
            "channels_monitored": session.channels_monitored
        }

    async def _log_communication(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Log detected intership communication

        Required params:
        - channel: Channel number
        - session_id: Monitoring session

        Optional params:
        - vessel1_name, vessel2_name, duration_seconds,
          content_summary, communication_type, signal_strength,
          audio_file_url, transcription
        """
        channel = params.get("channel")
        session_id = params.get("session_id")

        if not channel:
            return {
                "success": False,
                "error": "channel is required"
            }

        comm_id = str(uuid.uuid4())

        communication = IntershipCommunication(
            comm_id=comm_id,
            timestamp=datetime.now().isoformat(),
            channel_number=channel,
            frequency_mhz=self.channels[channel].frequency_mhz if channel in self.channels else 0.0,
            vessel1_name=params.get("vessel1_name"),
            vessel2_name=params.get("vessel2_name"),
            duration_seconds=params.get("duration_seconds"),
            content_summary=params.get("content_summary"),
            communication_type=params.get("communication_type", "operational"),
            location=params.get("location"),
            detected_by=params.get("detected_by", "sdr"),
            signal_strength=params.get("signal_strength"),
            audio_file_url=params.get("audio_file_url"),
            transcription=params.get("transcription")
        )

        self.communications[comm_id] = communication

        # Add to session if specified
        if session_id and session_id in self.active_sessions:
            self.active_sessions[session_id].add_communication(comm_id)

        logger.info(f"Logged intership communication: {comm_id} on CH{channel}")

        return {
            "success": True,
            "comm_id": comm_id,
            "channel": channel,
            "frequency": communication.frequency_mhz,
            "timestamp": communication.timestamp,
            "communication_type": communication.communication_type,
            "message": "Communication logged successfully"
        }

    async def _get_scanning_profile(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Get SDR scanning profile for VHF monitoring

        Required params:
        - profile_type: passive_monitoring, race_net_monitoring,
                       marina_operations, comprehensive_scan

        Returns channel list and scanning parameters for SDR
        """
        profile_type = params.get("profile_type", "passive_monitoring")

        profiles = {
            "passive_monitoring": {
                "description": "General passive monitoring for Ada Observer",
                "channels": [16, 6, 72, 73],
                "scan_interval_seconds": 1.0,
                "priority_dwell_ms": 500,
                "squelch_level": -100,
                "notes": "Always include CH 16 for safety"
            },
            "race_net_monitoring": {
                "description": "Active monitoring during sailing races",
                "channels": [72, 73, 77, 6],
                "scan_interval_seconds": 0.5,
                "priority_dwell_ms": 1000,
                "squelch_level": -95,
                "notes": "Fast scanning for race communications"
            },
            "marina_operations": {
                "description": "Marina-specific monitoring",
                "channels": [16, 9, 12, 73],
                "scan_interval_seconds": 2.0,
                "priority_dwell_ms": 500,
                "squelch_level": -100,
                "notes": "Focus on marina working channels"
            },
            "comprehensive_scan": {
                "description": "Full band monitoring",
                "channels": [16, 6, 8, 9, 10, 12, 13, 72, 73, 77],
                "scan_interval_seconds": 0.2,
                "priority_dwell_ms": 200,
                "squelch_level": -105,
                "notes": "Complete intership and marina coverage"
            }
        }

        if profile_type not in profiles:
            return {
                "success": False,
                "error": f"Unknown profile: {profile_type}",
                "available_profiles": list(profiles.keys())
            }

        profile = profiles[profile_type]

        # Add frequency information for each channel
        channel_frequencies = [
            {
                "channel": ch,
                "frequency_mhz": self.channels[ch].frequency_mhz if ch in self.channels else None,
                "type": self.channels[ch].channel_type if ch in self.channels else "unknown",
                "description": self.channels[ch].usage_description if ch in self.channels else ""
            }
            for ch in profile["channels"]
        ]

        return {
            "success": True,
            "profile_type": profile_type,
            "description": profile["description"],
            "scanning_parameters": {
                "channels": profile["channels"],
                "scan_interval_seconds": profile["scan_interval_seconds"],
                "priority_dwell_ms": profile["priority_dwell_ms"],
                "squelch_level_dbm": profile["squelch_level"]
            },
            "channel_frequencies": channel_frequencies,
            "sdr_config": {
                "center_frequency_mhz": 156.500,  # Middle of VHF marine band
                "sample_rate_mhz": 2.4,
                "bandwidth_khz": 25,
                "modulation": "NFM",  # Narrow FM
                "demodulation": "FM",
                "audio_sample_rate_hz": 48000
            },
            "notes": profile["notes"]
        }

    async def _get_active_sessions(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Get all active monitoring sessions"""
        active = [s for s in self.active_sessions.values() if s.is_active]

        return {
            "success": True,
            "total_active_sessions": len(active),
            "sessions": [
                {
                    "session_id": s.session_id,
                    "vessel_name": s.vessel_name,
                    "mode": s.mode,
                    "channels": s.channels_monitored,
                    "start_time": s.start_time,
                    "communications_detected": len(s.detected_communications)
                }
                for s in active
            ]
        }
