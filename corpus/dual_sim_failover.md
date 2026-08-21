# Dual-SIM Failover Behavior

A dual-SIM router keeps a primary SIM active for data traffic and a secondary SIM
on standby. Failover to the secondary SIM is normally triggered by one of a few
conditions: loss of signal on the primary carrier, a defined number of consecutive
failed connectivity checks (commonly ICMP pings or HTTP checks to a known host),
or the primary SIM's data plan being exhausted where usage tracking is supported.

Failback behavior differs by configuration. Some deployments failback to the primary
SIM automatically once it becomes reachable again; others require the primary to
remain stable for a minimum dwell time before failback is attempted, to avoid
rapid flapping between SIMs when the primary connection is marginal.

A device stuck on the secondary SIM after the primary has recovered is usually
either a dwell-time configuration issue or a connectivity check that is still
failing against the primary, for example, due to a stale route or DNS problem
that isn't actually a carrier issue.
