---
name: sip-human-transfer
description: Use this when a SIP Grok Voice caller should be connected to a human — SIP REFER, verbatim pre-transfer phrase, escalate keywords. Not for playing a phone number as speech.
---

# Human transfer (SIP REFER)

When the caller wants a person, **do not speak the destination number**. Speak a short hold line, then REFER.

## Env

- `SIP_TRANSFER_TARGET` — `sip:user@registrar-host` or a bare number (normalized to `sip:<number>@SIP_REG_HOST`)
- `TRANSFER_ANNOUNCE` — spoken exactly, then wait ~8s so it finishes, then REFER. Keep the dialog up (do not BYE immediately; wait for 202/NOTIFY).

Example announce: `Please hold a moment, I am transferring you now. Have a nice day.`

## Detect

Treat as transfer intent: agent / colleague / human / operator / "please transfer" / "yes please" after the bot offered a handoff. Short affirms (`yes`, `ok`, `please`) only count **after** an offer.

If the model already spoke the announce line, skip a second one and REFER.

## Prompt

The YAML must tell the model to ask `Shall I connect you to a colleague?` and then **stop**. The bridge speaks `TRANSFER_ANNOUNCE` and sends REFER. Never list the transfer URI in the spoken prompt (models will read it out).

After REFER the AI leg ends; recording of the human conversation is out of scope unless the PBX records it.
