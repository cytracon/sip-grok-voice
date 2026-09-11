# SIP Grok Voice

Cursor plugin: put [Grok Voice](https://docs.x.ai/) on a **real phone number** over SIP.

Inbound call → Grok speech-to-speech → optional **SIP REFER** to a human, optional **transcript + WAV** by email. Bring your own SIP registrar and xAI key.

This is **not** the in-app Grok Voice plugin (mic in a web app). It sits on [aicc2025/sip-to-ai](https://github.com/aicc2025/sip-to-ai).

## Install

After it is listed on the Cursor Marketplace, install **SIP Grok Voice**. Until then, clone this repo and use it as a local plugin.

## What you configure (never shipped)

| Setting | Where |
| --- | --- |
| xAI API key | `.env` `XAI_API_KEY` |
| SIP registrar | `.env` `SIP_REG_HOST` / `USER` / `PASS` |
| Human transfer URI | `.env` `SIP_TRANSFER_TARGET` |
| Spoken transfer line | `.env` `TRANSFER_ANNOUNCE` |
| INVITE allow-list | `.env` `SIP_INVITE_ALLOW` |
| Recording mailbox | `.env` `CALL_RECORD_TO` / `FROM` |
| Brand, facts, greeting | `agent_prompt.yaml` |

Templates live in `templates/` (`.env.example`, YAML, systemd unit, `call_recorder.py`).

## Skills

| Skill | When |
| --- | --- |
| `deploy-sip-grok-voice` | First install on a public host |
| `configure-voice-agent` | Greeting, pronunciation, website facts |
| `sip-human-transfer` | Connect the caller to a person via REFER |
| `sip-call-recording` | Mail transcript + stereo WAV after hangup |
| `sip-invite-harden` | Scanners, stolen Contact, INVITE=0 |

## Marketplace

Submit the repository at [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish).

## License

MIT for this plugin. sip-to-ai itself is Apache-2.0 (upstream).
