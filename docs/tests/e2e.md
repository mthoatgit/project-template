---
status: template
---

# End-to-End Tests

> **Template file.** A single happy-path test that exercises the full
> system. If a flow is critical enough that breaking it would ship a
> broken release, it belongs here. Drop this block when done.

Covers <NFR-IDs and/or REQ-IDs> (<Task ID>).

A single happy-path test exercises the full system via <Testcontainers /
ephemeral env / staging>:

1. <Authenticate / obtain token>
2. <Set up required entities via API or fixtures>
3. <Trigger the primary user flow>
4. <Wait for any async propagation>
5. <Assert the observable end state>

The test must pass in CI without manual setup. Failure of any step
fails the test.
