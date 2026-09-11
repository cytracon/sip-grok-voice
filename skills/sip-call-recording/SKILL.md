---
name: sip-call-recording
description: Use this when emailing a SIP Grok Voice call transcript and stereo WAV after hangup. Not for live barge-in or human-leg recording after REFER.
---

# Call recording email

After a real call ends, mail a transcript plus a stereo WAV (left = caller, right = bot). Skip probes (almost no RTP).

## Env

- `CALL_RECORD_EMAIL=1`
- `CALL_RECORD_TO` / `CALL_RECORD_FROM`
- `CALL_RECORD_DIR=recordings`
- Host must have `sendmail` (or change the helper to your MTA)

Copy `templates/call_recorder.py` into the sip-to-ai app (`app/bridge/call_recorder.py`). Wire it from the audio adapter (caller RX + bot TX) and from Grok transcript events. On `call.stop()`, `await recorder.deliver()`.

Greeting YAML should mention that the call may be recorded.

Time zone in the template defaults to UTC — change `TZ` if you want local stamps. Do not hard-code a tenant mailbox or DID in the module; pass them into the constructor from env.
