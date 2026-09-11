---
name: deploy-sip-grok-voice
description: Use this when putting Grok Voice on a real phone number via SIP — inbound PSTN/SIP calls, REGISTER to a registrar, systemd, firewall, xAI key. Not for in-app web voice (that is the Grok Voice plugin).
---

# Deploy SIP Grok Voice

Bridge a SIP registrar to xAI Grok Voice using [aicc2025/sip-to-ai](https://github.com/aicc2025/sip-to-ai) (`AI_VENDOR=grok`). This plugin does not ship tenant numbers, passwords, or brand facts.

## You need from the user

- Public host with UDP **5060** and RTP **10000–20000** open
- SIP registrar: host, user, password (and realm if different)
- xAI API key used only for this service
- Spoken greeting + facts YAML (see `configure-voice-agent`)
- Optional: human-transfer URI (`sip-human-transfer`), recording mailbox (`sip-call-recording`)

Never copy another tenant's `.env`.

## Steps

1. Clone `https://github.com/aicc2025/sip-to-ai` onto the host. Python 3.12+, `uv` or venv as in upstream README.
2. Copy `templates/.env.example` to `.env` (mode 600). Fill `XAI_API_KEY`, `SIP_REG_*`, `GROK_VOICE` (try `leo`).
3. Copy `templates/agent_prompt.yaml` and fill the FACTS block. Set `AGENT_PROMPT_FILE=agent_prompt.yaml`. YAML is loaded per call — greeting changes do not need a restart; **code** changes do (`systemctl restart`).
4. Bind `SIP_DOMAIN=0.0.0.0` and `SIP_PORT=5060`. Contact must be the **public** IP:port the registrar will INVITE (STUN on the SIP socket, or a public host). A private Contact IP means INVITEs never arrive.
5. One REGISTER Contact only. A second SIP client (softphone) with the same account steals the Contact and the host sees `INVITE=0`.
6. Install `templates/sip-to-ai.service` (adjust `WorkingDirectory`). `Restart=always`. Do not run ad-hoc `nohup` — leftovers hold 5060.
7. Firewall: UDP 5060 + RTP range. Registrar OPTIONS can stay 200 (NAT keepalive).
8. Prove: REGISTER 200, then a real call produces an INVITE from the registrar IP (not from scanners). Apply `sip-invite-harden` before going public.

## Out of scope

- In-app mic/speaker Grok Voice (marketplace plugin "Grok Voice")
- Selling or embedding someone else's DID, key, or prompt facts
