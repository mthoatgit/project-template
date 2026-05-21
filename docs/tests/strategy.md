---
status: template
---

# Test Strategy

> **Template file.** Replace placeholders to describe the test approach
> for your project. Drop this block when done.

How we test, what each layer covers, and what "done" means.

## Test Pyramid

| Layer | Purpose | Tools |
|---|---|---|
| **Unit** | <Pure logic in <service classes>, no framework context> | <test framework, mocking lib> |
| **Slice** | <Persistence or web layer in isolation> | <slice annotations or equivalents> |
| **Integration** | <Module wiring with real dependencies> | <containers, full-context bootstrap> |
| **E2E** | <Full system over HTTP / public API> | <containers + client> |

<One short paragraph: what question each layer answers. Why we use the
mix above instead of, say, only unit or only E2E.>

## "Done" per layer

- A **<service / use case>** is done when <criterion>.
- A **<repository / persistence>** is done when <criterion>.
- A **<controller / API endpoint>** is done when <criterion>.
- The **system** is done when <the E2E happy-path test passes>.

## Test Data & Fixtures

- <Schema reset strategy — truncate, transactional rollback, container per test>
- <Reusable builders or factories for core entities>
- <Statement on shared mutable state>

## CI Integration

- <Which test layers run on which trigger>
- <How long-running suites are kept under control>
- <Merge-blocking rule>
