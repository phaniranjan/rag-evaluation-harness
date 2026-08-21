# IPsec Tunnel Troubleshooting

An IPsec tunnel is established in two phases. IKE Phase 1 negotiates a secure channel
between peers and authenticates them, producing an ISAKMP security association.
IKE Phase 2 negotiates the actual IPsec security associations used to encrypt traffic.

If a tunnel fails to come up, the first place to check is Phase 1 negotiation.
Common Phase 1 failures include mismatched pre-shared keys, mismatched encryption
or hashing algorithms, and mismatched Diffie-Hellman groups between peers.

If Phase 1 succeeds but Phase 2 fails, common causes include mismatched proxy IDs
(the traffic selectors defining which subnets are allowed through the tunnel),
mismatched perfect forward secrecy settings, or an expired security association
that was not renegotiated cleanly.

A tunnel that comes up but shows no traffic is often a routing issue rather than
an IPsec issue: the tunnel interface may be active, but no route points traffic
into it, or a firewall rule on one side is dropping the encrypted traffic.
