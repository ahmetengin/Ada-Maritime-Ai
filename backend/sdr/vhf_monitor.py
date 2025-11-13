"""
Ada Observer - VHF SDR Monitor

Real-time VHF radio monitoring using RTL-SDR.
Monitors intership communications (CH 6, 72, 73, 77) and emergency channel (CH 16).

Hardware Required:
- RTL-SDR Blog V3 or compatible SDR dongle
- VHF marine antenna (156 MHz optimized)

Features:
- Multi-channel scanning
- Voice Activity Detection (VAD)
- Speech-to-Text (Whisper)
- GPS location tagging
- Audio recording (WAV)
- Real-time alerts
- Database logging
"""

import asyncio
import numpy as np
from datetime import datetime
from typing import Optional, List, Callable
import logging

try:
    from rtlsdr import RtlSdr
except ImportError:
    print("Warning: pyrtlsdr not installed. Install with: pip install pyrtlsdr")
    RtlSdr = None

try:
    import sounddevice as sd
except ImportError:
    print("Warning: sounddevice not installed. Install with: pip install sounddevice")
    sd = None

from ..config import get_config
from ..logger import setup_logger
from ..database.models import IntershipCommunication, VHFMonitoringSession


logger = setup_logger(__name__)


class VHFScanner:
    """
    VHF Marine Band Scanner using RTL-SDR

    Monitors VHF channels for intership communications and emergency broadcasts.
    Implements Voice Activity Detection and automatic channel scanning.
    """

    def __init__(
        self,
        channels: List[int] = None,
        center_freq_mhz: float = 156.5,
        sample_rate: int = 2_400_000,
        gain: str = "auto"
    ):
        """
        Initialize VHF Scanner

        Args:
            channels: List of VHF channels to monitor (default: [16, 6, 72, 73])
            center_freq_mhz: SDR center frequency in MHz
            sample_rate: Sample rate in Hz (default 2.4 MS/s)
            gain: SDR gain ("auto" or dB value)
        """
        self.channels = channels or [16, 6, 72, 73]
        self.center_freq_mhz = center_freq_mhz
        self.sample_rate = sample_rate
        self.gain = gain

        # Channel frequencies (MHz)
        self.channel_frequencies = {
            6: 156.300,
            8: 156.400,
            9: 156.450,
            10: 156.500,
            12: 156.600,
            13: 156.650,
            16: 156.800,  # Emergency
            72: 156.625,
            73: 156.675,
            77: 156.875
        }

        self.sdr = None
        self.is_scanning = False
        self.current_channel = None
        self.callbacks = []

        logger.info(f"VHF Scanner initialized: channels={self.channels}, freq={center_freq_mhz} MHz")

    def initialize_sdr(self) -> bool:
        """Initialize RTL-SDR device"""
        if RtlSdr is None:
            logger.error("RTL-SDR library not available")
            return False

        try:
            self.sdr = RtlSdr()

            # Configure SDR
            self.sdr.sample_rate = self.sample_rate
            self.sdr.center_freq = self.center_freq_mhz * 1e6  # Convert to Hz

            if self.gain == "auto":
                self.sdr.gain = 'auto'
            else:
                self.sdr.gain = float(self.gain)

            logger.info(f"SDR initialized: {self.sdr.get_device_index_by_serial()}")
            logger.info(f"  Sample rate: {self.sdr.sample_rate / 1e6:.2f} MS/s")
            logger.info(f"  Center freq: {self.sdr.center_freq / 1e6:.2f} MHz")
            logger.info(f"  Gain: {self.sdr.gain} dB")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize SDR: {e}")
            return False

    def tune_channel(self, channel: int) -> bool:
        """Tune SDR to specific VHF channel"""
        if channel not in self.channel_frequencies:
            logger.error(f"Invalid channel: {channel}")
            return False

        freq_mhz = self.channel_frequencies[channel]

        try:
            self.sdr.center_freq = freq_mhz * 1e6
            self.current_channel = channel
            logger.debug(f"Tuned to CH {channel} ({freq_mhz} MHz)")
            return True

        except Exception as e:
            logger.error(f"Failed to tune channel {channel}: {e}")
            return False

    def detect_voice_activity(self, samples: np.ndarray, threshold_db: float = -80) -> bool:
        """
        Simple Voice Activity Detection

        Args:
            samples: Complex IQ samples
            threshold_db: Energy threshold in dB

        Returns:
            True if voice activity detected
        """
        # Calculate signal power
        power = np.mean(np.abs(samples) ** 2)
        power_db = 10 * np.log10(power + 1e-10)

        return power_db > threshold_db

    async def scan_channel(
        self,
        channel: int,
        duration_seconds: float = 1.0,
        vad_threshold_db: float = -80
    ) -> Optional[dict]:
        """
        Scan a single channel for activity

        Args:
            channel: VHF channel number
            duration_seconds: How long to listen
            vad_threshold_db: Voice activity threshold

        Returns:
            Detection result dictionary or None
        """
        if not self.tune_channel(channel):
            return None

        try:
            # Read samples
            num_samples = int(self.sample_rate * duration_seconds)
            samples = self.sdr.read_samples(num_samples)

            # Detect voice activity
            has_activity = self.detect_voice_activity(samples, vad_threshold_db)

            if has_activity:
                result = {
                    "channel": channel,
                    "frequency_mhz": self.channel_frequencies[channel],
                    "timestamp": datetime.now().isoformat(),
                    "signal_detected": True,
                    "signal_strength_dbm": self._calculate_rssi(samples),
                    "duration_seconds": duration_seconds
                }

                logger.info(f"📻 Activity detected on CH {channel}")

                # Trigger callbacks
                for callback in self.callbacks:
                    try:
                        await callback(result)
                    except Exception as e:
                        logger.error(f"Callback error: {e}")

                return result

        except Exception as e:
            logger.error(f"Error scanning channel {channel}: {e}")

        return None

    async def scan_loop(
        self,
        scan_interval_seconds: float = 1.0,
        priority_channels: List[int] = None
    ):
        """
        Continuous scanning loop

        Args:
            scan_interval_seconds: Time per channel scan
            priority_channels: Channels to prioritize (longer dwell)
        """
        priority_channels = priority_channels or [16]  # Always prioritize emergency

        logger.info(f"Starting scan loop: {len(self.channels)} channels")
        logger.info(f"Priority channels: {priority_channels}")

        self.is_scanning = True

        while self.is_scanning:
            for channel in self.channels:
                if not self.is_scanning:
                    break

                # Longer dwell time for priority channels
                dwell_time = scan_interval_seconds
                if channel in priority_channels:
                    dwell_time *= 2

                await self.scan_channel(
                    channel,
                    duration_seconds=dwell_time
                )

                # Small pause between channels
                await asyncio.sleep(0.1)

    def stop_scanning(self):
        """Stop the scanning loop"""
        logger.info("Stopping VHF scanner")
        self.is_scanning = False

    def add_callback(self, callback: Callable):
        """Add callback for activity detection"""
        self.callbacks.append(callback)

    def _calculate_rssi(self, samples: np.ndarray) -> float:
        """Calculate Received Signal Strength Indicator"""
        power = np.mean(np.abs(samples) ** 2)
        rssi_dbm = 10 * np.log10(power + 1e-10) - 30  # Approximate RSSI
        return float(rssi_dbm)

    def close(self):
        """Close SDR device"""
        if self.sdr:
            self.sdr.close()
            logger.info("SDR device closed")


class VHFRecorder:
    """Audio recorder for VHF communications"""

    def __init__(self, output_dir: str = "/var/ada/vhf_recordings"):
        """
        Initialize VHF Recorder

        Args:
            output_dir: Directory to save recordings
        """
        self.output_dir = output_dir
        self.is_recording = False
        self.current_recording = []

        import os
        os.makedirs(output_dir, exist_ok=True)

        logger.info(f"VHF Recorder initialized: {output_dir}")

    def start_recording(self, channel: int) -> str:
        """
        Start recording audio

        Args:
            channel: VHF channel being recorded

        Returns:
            Recording ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recording_id = f"vhf_ch{channel:02d}_{timestamp}"

        self.is_recording = True
        self.current_recording = []

        logger.info(f"Started recording: {recording_id}")

        return recording_id

    def add_samples(self, samples: np.ndarray):
        """Add audio samples to current recording"""
        if self.is_recording:
            self.current_recording.append(samples)

    def stop_recording(self, recording_id: str) -> str:
        """
        Stop recording and save to file

        Args:
            recording_id: Recording identifier

        Returns:
            Path to saved file
        """
        self.is_recording = False

        if not self.current_recording:
            logger.warning("No audio data to save")
            return None

        # Concatenate all samples
        audio_data = np.concatenate(self.current_recording)

        # Save as WAV file
        import wave
        filename = f"{self.output_dir}/{recording_id}.wav"

        try:
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(48000)  # 48 kHz

                # Convert to 16-bit PCM
                audio_int16 = (audio_data * 32767).astype(np.int16)
                wav_file.writeframes(audio_int16.tobytes())

            logger.info(f"Recording saved: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Failed to save recording: {e}")
            return None

        finally:
            self.current_recording = []


# Example usage
async def main():
    """Example VHF monitoring session"""
    print("Ada Observer - VHF Monitor")
    print("=" * 60)

    # Initialize scanner
    scanner = VHFScanner(
        channels=[16, 6, 72, 73],
        center_freq_mhz=156.5,
        sample_rate=2_400_000
    )

    if not scanner.initialize_sdr():
        print("❌ Failed to initialize SDR")
        return

    # Add activity callback
    async def on_activity(result):
        print(f"📻 Activity: CH {result['channel']} | "
              f"RSSI: {result['signal_strength_dbm']:.1f} dBm")

    scanner.add_callback(on_activity)

    # Start scanning
    try:
        print("\n🔍 Starting VHF scan...")
        print("Monitoring channels: 16, 6, 72, 73")
        print("Press Ctrl+C to stop\n")

        await scanner.scan_loop(
            scan_interval_seconds=1.0,
            priority_channels=[16]  # Prioritize emergency channel
        )

    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping...")

    finally:
        scanner.stop_scanning()
        scanner.close()
        print("✅ Scanner closed")


if __name__ == "__main__":
    asyncio.run(main())
