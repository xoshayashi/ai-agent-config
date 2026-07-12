# Milestone Reviews — milestone-review skill itself

- milestone: route_review v3 dispatch hardening (timeout / isolation / doctor / exit-4) | host: claude-code | end state: reviewed
  routes: codex=ok (28.0s, full diff review), claude=ok (256.3s, dispatched with --host codex to live-reproduce the incident route) | digest route: no
  conclusion: the 2026-07 incident ("claude route timed out at 180s, failed over to antigravity") was a timeout sized below real review latency, plus three latent dispatch bugs (codex hard-fails outside git repos without --skip-git-repo-check; agy's internal 5m print wait desynced from --timeout; prompt-in-argv exposure/length ceiling). v3 fixes all four and adds a measured --doctor preflight.
  verified: all 4 checks applied. Reviewer claims checked against the file: adopted codex findings (exit 4 for failover success; strict-gate scans every attempt's stdout incl. partial timeout output) and claude findings (--doctor rejects review-shaping flags; doctor challenge-response on probe answers; --strict-gate auto-appends the [BLOCKING] instruction; agy --print-timeout gets a 30s margin). Rejected against primary evidence: "empty stdout passes the gate" (run_reviewer already degrades rc=0+empty stdout to error, covered by test) and "degraded runs never print attempts" (output is emitted before the return 1 path). Tiebreaker on the exit-code dispute (codex wanted exit 1 on any degraded attempt): the skill's own record contract distinguishes degraded from failed, so a dedicated exit 4 was chosen over 1.
  next: none for the skill; repo commit left to the owner (working tree has unrelated dirty files from other tasks).

## Evidence (2026-07-12 bench, macOS, all CLIs live)

| Check | Result |
|---|---|
| Unit suite (tests/test_route_review.py) | 40/40 ok |
| `claude -p` trivial round trip | plain 4.5s / isolated 4.2s / isolated+stdin 3.0s |
| `codex exec` outside git repo, no flag | rc=1 in 0.1s ("Not inside a trusted directory") — latent route-killer, now fixed |
| `codex exec --skip-git-repo-check` argv / stdin | ok 6.6s / ok 3.9s |
| `agy -p` trivial | ok 40.6–41.4s; accepts `--print-timeout 600s` |
| Incident reproduction: claude route, 1035-line diff prompt, host=codex | **ok in 256.3s** — would have timed out at the old 180s default; passes under the new 600s default |
| codex route, same diff, host=claude-code | ok in 28.0s, returned actionable [BLOCKING] findings |
| `--doctor --host codex` (incident pool) | rc=0; claude ok 2.5s, antigravity ok 40.7s |
| `--doctor --host claude-code` | rc=0; codex ok 3.7s, antigravity ok 39.6s |
| Live failover (dead codex simulated, host=claude-code) | rc=4, stderr `attempts: codex=error, antigravity=ok` |
| Live `--strict-gate` clean review (claude route) | rc=0 with auto-appended gate instruction |
