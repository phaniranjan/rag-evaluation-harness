# Network Telemetry Monitoring

Most network monitoring systems collect telemetry through a combination of SNMP polling,
streaming telemetry, and syslog ingestion. SNMP polling is simple but adds latency
between an event occurring and it being observed, since it depends on the poll interval.
Streaming telemetry pushes data as it changes, giving near real time visibility at the
cost of higher setup complexity.

A monitoring dashboard is only as reliable as its alert thresholds. Static thresholds
are easy to configure but generate noise when normal traffic patterns vary by time of
day. Dynamic or baseline-relative thresholds compare current values against a rolling
historical baseline and alert on meaningful deviation rather than a fixed number.

Alert fatigue is a common failure mode: when too many low-value alerts fire, operators
begin to ignore the channel, and a genuine high severity event can be missed. Tiered
alerting, where only sustained or severe deviations page an on-call engineer while
minor ones are logged for later review, is a common mitigation.
