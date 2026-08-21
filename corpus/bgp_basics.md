# BGP Route Flapping

Route flapping occurs when a BGP route repeatedly becomes available and unavailable in
rapid succession. Common causes include unstable physical links, interface hardware
faults, misconfigured route filters, and software bugs in the routing process.

Route flapping is typically diagnosed by inspecting the BGP log for repeated
UPDATE and WITHDRAW messages for the same prefix within a short time window.
A flap count above a defined threshold within a rolling window (for example,
5 flaps within 15 minutes) is generally treated as an anomaly worth investigating.

Route dampening is a common mitigation: BGP assigns a penalty to a flapping route,
and once the penalty crosses a suppress threshold, the route is temporarily withdrawn
from the routing table until the penalty decays below a reuse threshold.

Flapping should not be confused with normal convergence after a planned maintenance
window, which produces a single UPDATE and WITHDRAW pair rather than a repeating pattern.
