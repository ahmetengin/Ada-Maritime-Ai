"""Arrival Operations Skill - Airport-Style (Approach, Landing, Taxi-In, Gate)"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from backend.skills.base_skill import BaseSkill, SkillMetadata
from backend.database.models import (
    ArrivalPhase, ArrivalSequence, MooringBoat,
    PilotBoat, DepartureChannel
)
from backend.logger import get_logger

logger = get_logger(__name__)


class ArrivalOperationsSkill(BaseSkill):
    """
    Manages complete arrival sequence like airport operations:

    1. APPROACHING: Vessel approaching marina (like on approach)
    2. ENTRY CLEARANCE: Get permission to enter (like landing clearance)
    3. IN CHANNEL: Navigate arrival channel (like runway)
    4. FOLLOW-ME ASSIGNED: Pilot boat assigned to guide
    5. TAXI TO BERTH: Navigate to assigned berth
    6. MOORING REQUEST: Request mooring boat (like requesting marshaller)
    7. MOORING IN PROGRESS: Lines being secured
    8. DOCKED: Securely moored at berth (like at gate)
    """

    def __init__(self, db_interface=None):
        super().__init__()
        self.db = db_interface

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="arrival_operations",
            description="Airport-style arrival operations with channel entry, escort, and mooring",
            version="1.0.0",
            author="Ada Maritime AI",
            requires_database=True
        )

    async def execute(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Execute complete arrival sequence

        Args:
            params: {
                "vessel_id": str,
                "destination_berth_id": str,
                "terminal_id": str,
                "estimated_arrival_time": datetime (optional),
                "auto_execute": bool (default: False)
            }
        """
        self.validate_params(params, ["vessel_id", "destination_berth_id", "terminal_id"])

        vessel_id = params.get("vessel_id")
        berth_id = params.get("destination_berth_id")
        terminal_id = params.get("terminal_id")
        auto_execute = params.get("auto_execute", False)
        eta = params.get("estimated_arrival_time", datetime.now() + timedelta(minutes=15))

        logger.info(f"Starting arrival operations for vessel {vessel_id}")

        try:
            # Create arrival sequence
            sequence = ArrivalSequence(
                sequence_id=f"ARR-{vessel_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                vessel_id=vessel_id,
                destination_berth_id=berth_id,
                terminal_id=terminal_id,
                estimated_arrival_time=eta
            )

            # Phase 1: Approaching
            await self._phase_1_approaching(sequence)

            if auto_execute:
                # Execute all phases automatically
                await self._phase_2_entry_clearance(sequence)
                await self._phase_3_in_channel(sequence)
                await self._phase_4_assign_follow_me(sequence)
                await self._phase_5_taxi_to_berth(sequence)
                await self._phase_6_request_mooring(sequence)
                await self._phase_7_mooring_in_progress(sequence)
                await self._phase_8_docked(sequence)

            return {
                "operation": "arrival_operations",
                "sequence_id": sequence.sequence_id,
                "vessel_id": vessel_id,
                "current_phase": sequence.current_phase.value,
                "phase_history": sequence.phase_history,
                "clearances": sequence.clearances,
                "delays": sequence.delays,
                "destination_berth": berth_id,
                "status": sequence.status,
                "resources": {
                    "pilot_boat": sequence.pilot_boat_id,
                    "mooring_boat": sequence.mooring_boat_id,
                    "arrival_channel": sequence.arrival_channel_id
                },
                "success": True
            }

        except Exception as e:
            logger.error(f"Error in arrival operations: {str(e)}")
            return {
                "operation": "arrival_operations",
                "success": False,
                "error": str(e)
            }

    async def _phase_1_approaching(
        self,
        sequence: ArrivalSequence
    ) -> Dict[str, Any]:
        """
        Phase 1: Vessel approaching marina
        Like aircraft on approach to airport
        """
        logger.info(f"Phase 1: Approaching for {sequence.vessel_id}")

        sequence.update_phase(ArrivalPhase.APPROACHING)
        sequence.add_clearance(
            f"Good day. Contact marina control on VHF {sequence.vhf_channel} "
            f"when 2 nautical miles out"
        )

        logger.info(f"Vessel {sequence.vessel_id} approaching marina")

        return {"success": True, "phase": "approaching"}

    async def _phase_2_entry_clearance(
        self,
        sequence: ArrivalSequence
    ) -> Dict[str, Any]:
        """
        Phase 2: Request and receive entry clearance
        Like landing clearance
        """
        logger.info(f"Phase 2: Entry clearance for {sequence.vessel_id}")

        # Check weather and channel availability
        weather_ok = await self._check_weather_conditions()
        channel = await self._find_available_arrival_channel()

        if not weather_ok:
            sequence.add_clearance(
                "Hold position - weather conditions not suitable for entry"
            )
            return {"success": False, "reason": "Weather hold"}

        if not channel:
            sequence.add_clearance(
                "Hold position outside marina - arrival channel occupied"
            )
            return {"success": False, "reason": "Channel busy"}

        sequence.arrival_channel_id = channel.channel_id
        sequence.update_phase(ArrivalPhase.ENTRY_CLEARANCE)
        sequence.add_clearance(
            f"Cleared to enter via {channel.channel_name}. "
            f"Berth {sequence.destination_berth_id} assigned. "
            f"Pilot boat will meet you at channel entrance"
        )

        logger.info(
            f"Entry clearance granted for {sequence.vessel_id} "
            f"via {channel.channel_name}"
        )

        return {"success": True, "channel": channel.channel_name}

    async def _phase_3_in_channel(
        self,
        sequence: ArrivalSequence
    ) -> Dict[str, Any]:
        """
        Phase 3: Navigating arrival channel
        Like runway landing
        """
        logger.info(f"Phase 3: In arrival channel for {sequence.vessel_id}")

        sequence.update_phase(ArrivalPhase.IN_CHANNEL)
        sequence.add_clearance(
            "Entering channel - maintain center line, reduce speed to 3 knots"
        )

        # Simulate channel transit (5 minutes)
        await asyncio.sleep(0.1)

        sequence.add_clearance("Channel clear - proceed to inner harbor")

        logger.info(f"Channel transit complete for {sequence.vessel_id}")

        return {"success": True}

    async def _phase_4_assign_follow_me(
        self,
        sequence: ArrivalSequence
    ) -> Dict[str, Any]:
        """
        Phase 4: Assign pilot boat for escort
        Like follow-me car at airport
        """
        logger.info(f"Phase 4: Assigning follow-me for {sequence.vessel_id}")

        # Find available pilot boat
        pilot_boat = await self._find_available_pilot_boat(sequence.terminal_id)

        if not pilot_boat:
            sequence.add_clearance(
                "Proceed independently to berth - no escort available"
            )
            return {"success": True, "escort": None}

        sequence.pilot_boat_id = pilot_boat.boat_id
        sequence.update_phase(ArrivalPhase.FOLLOW_ME_ASSIGNED)
        sequence.add_clearance(
            f"Pilot boat '{pilot_boat.boat_name}' will guide you to berth. "
            f"Follow at safe distance, max speed {pilot_boat.max_escort_speed_knots} knots"
        )

        logger.info(
            f"Pilot boat {pilot_boat.boat_name} assigned to {sequence.vessel_id}"
        )

        return {"success": True, "escort": pilot_boat.boat_name}

    async def _phase_5_taxi_to_berth(
        self,
        sequence: ArrivalSequence
    ) -> Dict[str, Any]:
        """
        Phase 5: Navigate to assigned berth
        Like taxiing to gate
        """
        logger.info(f"Phase 5: Taxi to berth for {sequence.vessel_id}")

        sequence.update_phase(ArrivalPhase.TAXIING_TO_BERTH)
        sequence.add_clearance(
            f"Follow pilot boat to berth {sequence.destination_berth_id}"
        )

        # Simulate taxi duration (10 minutes)
        await asyncio.sleep(0.1)

        sequence.add_clearance(
            f"Approaching berth {sequence.destination_berth_id} - "
            "prepare for mooring"
        )

        logger.info(f"Taxi to berth complete for {sequence.vessel_id}")

        return {"success": True}

    async def _phase_6_request_mooring(
        self,
        sequence: ArrivalSequence
    ) -> Dict[str, Any]:
        """
        Phase 6: Request mooring assistance
        Like requesting marshaller at gate
        """
        logger.info(f"Phase 6: Request mooring for {sequence.vessel_id}")

        # Find available mooring boat
        mooring_boat = await self._find_available_mooring_boat(sequence.terminal_id)

        if not mooring_boat:
            sequence.add_clearance("Stand by - mooring boat en route")
            await asyncio.sleep(0.2)  # Wait for mooring boat
            mooring_boat = await self._find_available_mooring_boat(sequence.terminal_id)

        sequence.mooring_boat_id = mooring_boat.boat_id
        sequence.update_phase(ArrivalPhase.MOORING_REQUESTED)
        sequence.add_clearance(
            f"Mooring boat '{mooring_boat.boat_name}' standing by. "
            f"Prepare to receive lines"
        )

        logger.info(
            f"Mooring boat {mooring_boat.boat_name} assigned to {sequence.vessel_id}"
        )

        return {"success": True, "mooring_boat": mooring_boat.boat_name}

    async def _phase_7_mooring_in_progress(
        self,
        sequence: ArrivalSequence
    ) -> Dict[str, Any]:
        """
        Phase 7: Mooring lines being secured
        Like connecting jetway and securing aircraft
        """
        logger.info(f"Phase 7: Mooring in progress for {sequence.vessel_id}")

        sequence.update_phase(ArrivalPhase.MOORING_IN_PROGRESS)
        sequence.add_clearance("Mooring in progress - securing lines")

        # Simulate mooring operation (5 minutes)
        await asyncio.sleep(0.1)

        sequence.add_clearance("All lines secured - vessel fast")

        logger.info(f"Mooring complete for {sequence.vessel_id}")

        return {"success": True}

    async def _phase_8_docked(
        self,
        sequence: ArrivalSequence
    ) -> Dict[str, Any]:
        """
        Phase 8: Vessel securely docked
        Like aircraft at gate, engines off
        """
        logger.info(f"Phase 8: Docked for {sequence.vessel_id}")

        sequence.update_phase(ArrivalPhase.DOCKED)
        sequence.actual_arrival_time = datetime.now()
        sequence.status = "completed"
        sequence.add_clearance(
            f"Welcome to the marina! Vessel secured at berth {sequence.destination_berth_id}. "
            f"Contact harbor office on VHF {sequence.vhf_channel} for services. "
            "Enjoy your stay!"
        )

        # Release resources
        if sequence.pilot_boat_id:
            await self._release_pilot_boat(sequence.pilot_boat_id)

        if sequence.mooring_boat_id:
            await self._release_mooring_boat(sequence.mooring_boat_id)

        logger.info(f"Arrival complete for {sequence.vessel_id}")

        return {"success": True, "arrival_time": sequence.actual_arrival_time}

    # Helper methods

    async def _check_weather_conditions(self) -> bool:
        """Check if weather is suitable for entry"""
        # In production, would check actual weather data
        return True

    async def _find_available_arrival_channel(self) -> Optional[DepartureChannel]:
        """Find available arrival channel"""
        return DepartureChannel(
            channel_id="CH-ARRIVE-1",
            channel_name="Main Arrival Channel",
            width_meters=50,
            depth_meters=10,
            length_meters=500,
            max_vessel_length=100,
            status="open"
        )

    async def _find_available_pilot_boat(
        self,
        terminal_id: str
    ) -> Optional[PilotBoat]:
        """Find available pilot boat"""
        return PilotBoat(
            boat_id="PB-001",
            boat_name="Rehber-1",
            current_status="available",
            pilot_name="Captain Mehmet",
            vhf_channel=16,
            max_escort_speed_knots=5.0
        )

    async def _find_available_mooring_boat(
        self,
        terminal_id: str
    ) -> Optional[MooringBoat]:
        """Find available mooring boat"""
        return MooringBoat(
            boat_id="MB-001",
            boat_name="Palamar-1",
            capacity=2,
            current_status="available",
            equipment=["fenders", "lines", "radio"],
            crew_size=2,
            response_time_minutes=5
        )

    async def _release_pilot_boat(self, pilot_boat_id: str):
        """Release pilot boat back to pool"""
        logger.info(f"Releasing pilot boat {pilot_boat_id}")

    async def _release_mooring_boat(self, mooring_boat_id: str):
        """Release mooring boat back to pool"""
        logger.info(f"Releasing mooring boat {mooring_boat_id}")
