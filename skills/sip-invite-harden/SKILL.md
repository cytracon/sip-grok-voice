---
name: sip-invite-harden
description: Use this when a public SIP Grok Voice listener is flooded by scanner INVITEs, hanging Grok WebSockets, or INVITE=0 after REGISTER. Not for codec/SDP tuning unless RTP never starts.
---

# Harden inbound SIP

Public UDP 5060 attracts probes. They open Grok WebSockets and kill real calls.

## Must

- Reject probe INVITE (`c=IN IP4 0.0.0.0` or RTP port 4000) with 488
- `SIP_INVITE_ALLOW` = registrar/SBC IPs only; others 403. OPTIONS from anyone may stay 200 (NAT).
- Cap live calls (`SIP_MAX_CALLS`, default 2) → 486
- Drop if no inbound RTP in ~8s
- systemd `Restart=always`

## REGISTER / no INVITE

If REGISTER is 200 but INVITE count stays 0: the DID is not forked here. Check competing Contact (home public IP / a softphone), voice-mail forwards on the DID, and that Contact is `sip:user@<public-host>:5060`.

Do not publish a tenant allow-list IP in this plugin; take it from the registrar's signalling address.
