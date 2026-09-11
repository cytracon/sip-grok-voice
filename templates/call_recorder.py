"""Record a SIP/AI call to WAV + transcript and email it after hangup."""

from __future__ import annotations

import asyncio
import io
import subprocess
import time
import wave
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import numpy as np
import structlog

TZ = ZoneInfo("UTC")
SAMPLE_RATE = 8000
MAX_SECONDS = 30 * 60
MAX_BYTES = SAMPLE_RATE * 2 * MAX_SECONDS  # one channel PCM16


class CallRecorder:
    """Time-aligned stereo WAV (caller left, bot right) plus transcript."""

    def __init__(
        self,
        *,
        call_id: str,
        caller: str,
        email_to: str,
        email_from: str,
        record_dir: Path,
        greeting: str = "",
    ) -> None:
        self.call_id = call_id
        self.caller = caller or "unknown"
        self.email_to = email_to
        self.email_from = email_from
        self.record_dir = record_dir
        self.started = datetime.now(TZ)
        self._t0 = time.monotonic()
        self._caller = bytearray()
        self._ai = bytearray()
        self._turns: list[tuple[str, str]] = []
        self._delivered = False
        self._logger = structlog.get_logger(__name__)
        if greeting:
            self.add_turn("Bot", greeting)

    def add_caller(self, pcm: bytes) -> None:
        self._append(self._caller, pcm)

    def add_ai(self, pcm: bytes) -> None:
        self._append(self._ai, pcm)

    def add_turn(self, role: str, text: Optional[str]) -> None:
        t = (text or "").strip()
        if not t:
            return
        self._turns.append((role, t))

    def _append(self, buf: bytearray, pcm: bytes) -> None:
        if not pcm:
            return
        elapsed = time.monotonic() - self._t0
        target = int(elapsed * SAMPLE_RATE) * 2
        if target > MAX_BYTES:
            return
        if len(buf) < target:
            buf.extend(b"\x00" * (target - len(buf)))
        room = MAX_BYTES - len(buf)
        if room <= 0:
            return
        buf.extend(pcm[:room])

    def _wav_bytes(self) -> bytes:
        left = np.frombuffer(bytes(self._caller), dtype="<i2")
        right = np.frombuffer(bytes(self._ai), dtype="<i2")
        n = max(left.size, right.size, 1)
        if left.size < n:
            left = np.pad(left, (0, n - left.size))
        if right.size < n:
            right = np.pad(right, (0, n - right.size))
        stereo = np.column_stack((left, right)).ravel()
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(stereo.tobytes())
        return buf.getvalue()

    def _duration_sec(self) -> float:
        n = max(len(self._caller), len(self._ai))
        return n / (SAMPLE_RATE * 2)

    def _should_skip(self) -> bool:
        if self._duration_sec() < 1.5 and not self._turns:
            return True
        if len(self._caller) < 320 * 40:
            return True
        return False

    def _transcript_body(self, wav_name: str) -> str:
        ended = datetime.now(TZ)
        dur = self._duration_sec()
        lines = [
            f"Voice call",
            f"From: {self.caller}",
            f"Start: {self.started.strftime('%Y-%m-%d %H:%M:%S')} UTC",
            f"End:   {ended.strftime('%Y-%m-%d %H:%M:%S')} UTC",
            f"Duration: {dur:.0f} s",
            f"Call-ID: {self.call_id}",
            f"Recording: {wav_name} (left=caller, right=bot)",
            "",
            "--- Transcript ---",
            "",
        ]
        if self._turns:
            for role, text in self._turns:
                lines.append(f"{role}: {text}")
                lines.append("")
        else:
            lines.append("(no transcript — audio only)")
            lines.append("")
        lines.append("Recording stops when the call is transferred to a human.")
        return "\n".join(lines)

    async def deliver(self) -> None:
        if self._delivered:
            return
        self._delivered = True
        if self._should_skip():
            self._logger.info(
                "Call recording skipped (too short / probe)",
                call_id=self.call_id,
                caller_bytes=len(self._caller),
            )
            return
        await asyncio.to_thread(self._deliver_sync)

    def _deliver_sync(self) -> None:
        self.record_dir.mkdir(parents=True, exist_ok=True)
        stamp = self.started.strftime("%Y%m%d_%H%M%S")
        safe_caller = "".join(c if c.isalnum() else "_" for c in self.caller)[:32]
        wav_name = f"{stamp}_{safe_caller}.wav"
        wav_path = self.record_dir / wav_name
        wav_bytes = self._wav_bytes()
        wav_path.write_bytes(wav_bytes)
        body = self._transcript_body(wav_name)

        msg = EmailMessage()
        msg["From"] = f"Voice <{self.email_from}>"
        msg["To"] = self.email_to
        msg["Subject"] = f"Call {self.caller} {self.started.strftime('%Y-%m-%d %H:%M')} UTC"
        msg.set_content(body)
        msg.add_attachment(
            wav_bytes,
            maintype="audio",
            subtype="wav",
            filename=wav_name,
        )
        try:
            proc = subprocess.run(
                ["/usr/sbin/sendmail", "-t", "-oi"],
                input=msg.as_bytes(),
                capture_output=True,
                timeout=30,
                check=False,
            )
            self._logger.info(
                "Call recording mailed",
                call_id=self.call_id,
                to=self.email_to,
                wav=str(wav_path),
                wav_bytes=len(wav_bytes),
                sendmail_rc=proc.returncode,
            )
        except Exception as exc:
            self._logger.error(
                "Call recording mail failed",
                call_id=self.call_id,
                error=str(exc),
                wav=str(wav_path),
            )
