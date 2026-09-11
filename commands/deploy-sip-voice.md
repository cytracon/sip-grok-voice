---
name: deploy-sip-voice
description: Deploy or repair SIP Grok Voice on a host (REGISTER, greeting, REFER, recording, probe hardening) using this plugin's skills. Never reuse another tenant's .env.
---

Follow `deploy-sip-grok-voice`, then `configure-voice-agent`. Add `sip-human-transfer`, `sip-call-recording`, and `sip-invite-harden` when those features are wanted. Ask the user for registrar credentials and the xAI key; do not invent them.
