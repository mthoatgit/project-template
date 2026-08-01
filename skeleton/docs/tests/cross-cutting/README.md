# Cross-cutting tests

Tests for NFRs (security, performance, audit) and system-wide concerns that do not belong to a single Epic. Follows the same three-mode discipline as Epic-owned tests — one file per test, filename `TEST-<NNNN>-<slug>.md`, global counter (same pool as Epic-owned tests; no separate namespace). The test file's `**Epic:**` header field carries the value `none` to signal cross-cutting scope.

Empty until a first cross-cutting test is filed.
