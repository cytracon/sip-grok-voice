---
name: configure-voice-agent
description: Use this when writing or fixing the SIP Grok Voice greeting and agent YAML — pronunciation of the brand, languages, website facts, recording notice. Not for SIP transport or REFER.
---

# Configure the voice agent

`agent_prompt.yaml` has `instructions` plus `greeting`. The greeting is spoken **verbatim** (word-for-word). Instructions are the system prompt after that.

## Greeting

Keep one line. If calls are recorded, say so here (legal notice), not later.

If TTS misreads the brand (`C` as `/s/` or `/ts/`), spell the **spoken** form in the greeting (e.g. a phonetic stand-in). Keep the written brand in instructions. Do not invent a new company name.

## Instructions

- The bot **is** the company, not a caller asking about the company. No second greeting after "hello?".
- Only facts from the public website (or the FACTS list). No invented URLs, prices, mail hosts, or `webmail.<customer-domain>`.
- The only phone number it may **speak** is the public inbound number. Never read staff mobiles, private DIDs, or owner emails.
- Unknown → offer human handoff (see `sip-human-transfer`), do not dump a callback number.
- Languages: follow the caller; default to the greeting language.

Copy `templates/agent_prompt.yaml` and fill the placeholders. Do not paste another tenant's facts.
