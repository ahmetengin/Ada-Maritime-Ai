"""Departure Operations Skill - Airport-Style (Pushback, Taxi, Follow-Me, Runway)"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from backend.skills.base_skill import BaseSkill, SkillMetadata
from backend.database.models import (
    DeparturePhase, DepartureSequence, MooringBoat,
    PilotBoat, DepartureChannel
)
from backend.logger import get_logger

logger = get_logger(__name__)


class DepartureOperationsSkill(BaseSkill):
    """
    Manages complete departure sequence like airport operations:

    1. PUSHBACK: Request mooring boat (palamar botu)
    2. LINE RELEASE: Release mooring lines (palamarları çöz)
    3. TAXI CLEARANCE: Get clearance to move in marina
    4. TAXI: Navigate through marina with pilot boat escort
    5. HOLDING: Wait at departure channel entrance
    6. DEPARTURE: Exit through departure channel (runway)
    7. CLEAR: Marina boundary crossed
    """

    def __init__(self, db_interface=None):
        super().__init__()
        self.db = db_interface

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="departure_operations",
            description="Airport-style departure operations with pushback, taxi, and channel clearance",
            version="1.0.0",
            author="Ada Maritime AI",
            requires_database=True
        )

    async def execute(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Execute complete departure sequence

        Args:
            params: {
                "vessel_id": str,
                "berth_id": str,
                "terminal_id": str,
                "requested_departure_time": datetime (optional),
                "auto_execute": bool (default: False)
            }
        """
        self.validate_params(params, ["vessel_id", "berth_id", "terminal_id"])

        vessel_id = params.get("vessel_id")
        berth_id = params.get("berth_id")
        terminal_id = params.get("terminal_id")
        auto_execute = params.get("auto_execute", False)
        requested_time = params.get(
            "requested_departure_time",
            datetime.now() + timedelta(minutes=30)
        )

        logger.info(f"Starting departure operations for vessel {vessel_id}")

        try:
            # Create departure sequence
            sequence = DepartureSequence(
                sequence_id=f"DEP-{vessel_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                vessel_id=vessel_id,
                berth_id=berth_id,
                terminal_id=terminal_id,
                requested_departure_time=requested_time
            )

            # Phase 1: Request Pushback (Palamar Botu)
            pushback_result = await self._phase_1_request_pushback(sequence)

            if auto_execute:
                # Execute all phases automatically
                await self._phase_2_pushback_operation(sequence)
                await self._phase_3_taxi_clearance(sequence)
                await self._phase_4_taxi_with_escort(sequence)
                await self._phase_5_holding_point(sequence)
                await self._phase_6_departure_clearance(sequence)
                await self._phase_7_channel_departure(sequence)
                await self._phase_8_clear_of_marina(sequence)

            return {
                "operation": "departure_operations",
                "sequence_id": sequence.sequence_id,
                "vessel_id": vessel_id,
                "current_phase": sequence.current_phase.value,
                "phase_history": sequence.phase_history,
                "clearances": sequence.clearances,
                "delays": sequence.delays,
                "total_delay_minutes": sequence.total_delay_minutes,
                "estimated_completion": sequence.estimated_completion_time.isoformat(),
                "status": sequence.status,
                "resources": {
                    "mooring_boat": sequence.mooring_boat_id,
                    "pilot_boat": sequence.pilot_boat_id,
                    "departure_channel": sequence.departure_channel_id
                },
                "success": True
            }

        except Exception as e:
            logger.error(f"Error in departure operations: {str(e)}")
            return {
                "operation": "departure_operations",
                "success": False,
                "error": str(e)
            }

    async def _phase_1_request_pushback(
        self,
        sequence: DepartureSequence
    ) -> Dict[str, Any]:
        """
        Phase 1: Request pushback (Palamar botu talep et)
        Like requesting pushback truck in airport
        """
        logger.info(f"Phase 1: Requesting pushback for {sequence.vessel_id}")

        # Find available mooring boat
        mooring_boat = await self._find_available_mooring_boat(sequence.terminal_id)

        if not mooring_boat:
            sequence.add_delay("No mooring boat available", 10)
            return {"success": False, "reason": "No mooring boat available"}

        # Assign mooring boat
        sequence.mooring_boat_id = mooring_boat.boat_id
        sequence.update_phase(DeparturePhase.PUSHBACK_REQUESTED)
        sequence.add_clearance(
            f"Pushback approved, mooring boat {mooring_boat.boat_name} assigned"
        )

        logger.info(
            f"Mooring boat {mooring_boat.boat_name} assigned to {sequence.vessel_id}"
        )

        return {
            "success": True,
            "mooring_boat": mooring_boat.boat_name,
            "eta_minutes": mooring_boat.response_time_minutes
        }

    async def _phase_2_pushback_operation(
        self,
        sequence: DepartureSequence
    ) -> Dict[str, Any]:
        """
        Phase 2: Pushback operation (Palamarları çöz, berth'ten it)
        Mooring boat releases lines and pushes vessel away from berth
        """
        logger.info(f"Phase 2: Pushback operation for {sequence.vessel_id}")

        sequence.update_phase(DeparturePhase.PUSHBACK_IN_PROGRESS)
        sequence.add_clearance("Pushback in progress - releasing mooring lines")

        # Simulate pushback duration (5 minutes)
        await asyncio.sleep(0.1)  # In production, would track actual progress

        sequence.add_clearance("Mooring lines released - clear of berth")
        sequence.notes.append(
            f"Successfully pushed back from berth {sequence.berth_id}"
        )

        logger.info(f"Pushback complete for {sequence.vessel_id}")

        return {"success": True, "phase": "pushback_complete"}

    async def _phase_3_taxi_clearance(
        self,
        sequence: DepartureSequence
    ) -> Dict[str, Any]:
        """
        Phase 3: Request and receive taxi clearance
        Like getting clearance to taxi on taxiway
        """
        logger.info(f"Phase 3: Taxi clearance for {sequence.vessel_id}")

        # Check marina traffic
        traffic_clear = await self._check_marina_traffic(sequence.terminal_id)

        if not traffic_clear:
            sequence.add_delay("Marina traffic congestion", 5)

        sequence.update_phase(DeparturePhase.TAXI_CLEARANCE)
        sequence.add_clearance(
            f"Cleared to taxi via inner channel to holding point. "
            f"Contact on VHF {sequence.vhf_channel}"
        )

        logger.info(f"Taxi clearance granted for {sequence.vessel_id}")

        return {"success": True, "vhf_channel": sequence.vhf_channel}

    async def _phase_4_taxi_with_escort(
        self,
        sequence: DepartureSequence
    ) -> Dict[str, Any]:
        """
        Phase 4: Taxi with pilot boat escort (Follow-me)
        Pilot boat guides vessel through marina
        """
        logger.info(f"Phase 4: Taxi with escort for {sequence.vessel_id}")

        # Assign pilot boat
        pilot_boat = await self._find_available_pilot_boat(sequence.terminal_id)

        if pilot_boat:
            sequence.pilot_boat_id = pilot_boat.boat_id
            sequence.update_phase(DeparturePhase.FOLLOW_ME_ACTIVE)
            sequence.add_clearance(
                f"Follow pilot boat '{pilot_boat.boat_name}' - "
                f"maintain {pilot_boat.max_escort_speed_knots} knots max speed"
            )
        else:
            sequence.update_phase(DeparturePhase.TAXIING)
            sequence.add_clearance("Taxi to holding point - no escort required")

        # Simulate taxi duration (10 minutes)
        await asyncio.sleep(0.1)

        logger.info(f"Taxiing complete for {sequence.vessel_id}")

        return {
            "success": True,
            "escort": pilot_boat.boat_name if pilot_boat else None
        }

    async def _phase_5_holding_point(
        self,
        sequence: DepartureSequence
    ) -> Dict[str, Any]:
        """
        Phase 5: Hold at departure channel entrance
        Like holding short of runway
        """
        logger.info(f"Phase 5: Holding point for {sequence.vessel_id}")

        sequence.update_phase(DeparturePhase.HOLDING_POINT)
        sequence.add_clearance("Hold position at departure channel entrance")

        # Wait for departure channel to be clear
        channel_available = await self._wait_for_channel_clearance(sequence)

        logger.info(f"Holding complete for {sequence.vessel_id}")

        return {"success": True, "channel_available": channel_available}

    async def _phase_6_departure_clearance(
        self,
        sequence: DepartureSequence
    ) -> Dict[str, Any]:
        """
        Phase 6: Departure clearance received
        Like getting takeoff clearance
        """
        logger.info(f"Phase 6: Departure clearance for {sequence.vessel_id}")

        # Find available departure channel
        channel = await self._find_available_departure_channel()

        if not channel:
            sequence.add_delay("Waiting for departure channel", 15)
            return {"success": False, "reason": "Channel not available"}

        sequence.departure_channel_id = channel.channel_id
        sequence.update_phase(DeparturePhase.DEPARTURE_CLEARANCE)
        sequence.add_clearance(
            f"Cleared for departure via {channel.channel_name}. "
            f"Contact port control after clearing marina boundary"
        )

        logger.info(
            f"Departure clearance granted for {sequence.vessel_id} "
            f"via {channel.channel_name}"
        )

        return {"success": True, "channel": channel.channel_name}

    async def _phase_7_channel_departure(
        self,
        sequence: DepartureSequence
    ) -> Dict[str, Any]:
        """
        Phase 7: Departing through channel
        Like takeoff roll on runway
        """
        logger.info(f"Phase 7: Channel departure for {sequence.vessel_id}")

        sequence.update_phase(DeparturePhase.DEPARTING)
        sequence.add_clearance("Departing via channel - maintain center line")

        # Simulate channel transit (5 minutes)
        await asyncio.sleep(0.1)

        logger.info(f"Channel transit complete for {sequence.vessel_id}")

        return {"success": True}

    async def _phase_8_clear_of_marina(
        self,
        sequence: DepartureSequence
    ) -> Dict[str, Any]:
        """
        Phase 8: Clear of marina boundary
        Like switching to departure frequency after takeoff
        """
        logger.info(f"Phase 8: Clear of marina for {sequence.vessel_id}")

        sequence.update_phase(DeparturePhase.CLEAR_OF_MARINA)
        sequence.actual_departure_time = datetime.now()
        sequence.status = "completed"
        sequence.add_clearance(
            "Clear of marina boundary - switch to port control. Have a safe voyage!"
        )

        # Release resources
        if sequence.pilot_boat_id:
            await self._release_pilot_boat(sequence.pilot_boat_id)

        if sequence.mooring_boat_id:
            await self._release_mooring_boat(sequence.mooring_boat_id)

        logger.info(f"Departure complete for {sequence.vessel_id}")

        return {"success": True, "departure_time": sequence.actual_departure_time}

    # Helper methods

    async def _find_available_mooring_boat(
        self,
        terminal_id: str
    ) -> Optional[MooringBoat]:
        """Find available mooring boat"""
        # In production, would query database
        return MooringBoat(
            boat_id="MB-001",
            boat_name="Palamar-1",
            capacity=2,
            current_status="available",
            equipment=["fenders", "lines", "radio"],
            crew_size=2,
            response_time_minutes=5
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

    async def _find_available_departure_channel(self) -> Optional[DepartureChannel]:
        """Find available departure channel"""
        return DepartureChannel(
            channel_id="CH-DEPART-1",
            channel_name="Main Departure Channel",
            width_meters=50,
            depth_meters=10,
            length_meters=500,
            max_vessel_length=100,
            status="open"
        )

    async def _check_marina_traffic(self, terminal_id: str) -> bool:
        """Check if marina traffic allows taxi"""
        # In production, would check actual traffic
        return True

    async def _wait_for_channel_clearance(
        self,
        sequence: DepartureSequence
    ) -> bool:
        """Wait for departure channel to be available"""
        # Simulate waiting
        await asyncio.sleep(0.1)
        return True

    async def _release_pilot_boat(self, pilot_boat_id: str):
        """Release pilot boat back to pool"""
        logger.info(f"Releasing pilot boat {pilot_boat_id}")

    async def _release_mooring_boat(self, mooring_boat_id: str):
        """Release mooring boat back to pool"""
        logger.info(f"Releasing mooring boat {mooring_boat_id}")
