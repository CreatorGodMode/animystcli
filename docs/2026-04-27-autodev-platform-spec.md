# Autodev Platform — Strategy & Build Spec

> **Status:** Strategy / build spec — not yet implemented. Captured 2026-04-27 after a Ralph Loop run that highlighted the structural gaps this platform would fill.
>
> **Working name:** `<project-name>` — placeholder. Founder picks the real name. Strong candidates: `Compose`, `Anvil`, `Forge` (taken internally — see `famished-agents`), `Lattice`, `Tract`.
>
> **License intent:** Apache 2.0. OSS core, with optional hosted runs as a future commercial layer.

---

## TL;DR

A small, composable runtime + policy layer for AI-driven code changes. **Not another AI coding tool** — it sits *underneath* whatever AI coding tool you already use (Claude Code, Cursor, Aider, your own scripts) and provides the missing primitives:

- **Specs** instead of free-form prompts (ticket → structured task tree)
- **Policies** as deterministic guardrails (diff-grep, schema rules, dep audits enforced before merge)
- **Verifiers** as composable units (typecheck, tests, schema probe, live smoke, regression hunter)
- **Gated landing** with tagged rollback baselines

The agent does the typing. This layer does the **specification, policy enforcement, verification, and merge gating**. Every existing AI coding tool gets safer and more accurate without being replaced.

---

## The problem

The current AI coding stack is asymmetric: world-class typing, primitive specification and verification.

**What we have today:**
- Excellent code generators (Claude, GPT-4, Cursor agents, Aider)
- Rich IDE integrations
- Some autonomous agents (Devin, Codex, Cursor background agents)

**What we don't have, in OSS, production-grade:**

1. **Spec discipline.** Prompts are free-form prose. A 200-line prompt embeds business logic, file paths, line numbers, constraints, conventions, and acceptance criteria — undifferentiated. There's no parseable contract between "what was asked" and "what was built." Diff review is the only verification.

2. **Policy as code.** "Don't break auth," "no new dependencies," "don't call `placeOrder` outside the existing call site" — these are sentences in prompts. Agents forget. Reviewers miss. Production breaks.

3. **Verification beyond unit tests.** `tsc + jest passing` ≠ feature works. Cross-cutting concerns (mock-mode parity, schema drift, regression in unrelated paths, live behavior) aren't tested by the suite that ships with the agent's task.

4. **Pause-and-ask.** Agents commit to their first interpretation of ambiguous tasks. No clean way to surface "I see two viable approaches, which do you want?" without breaking the autonomy contract.

5. **Rollback as second-class.** Merge happens; rollback is a manual scramble. There's no "tagged baseline + auto-revert on error budget breach" out of the box.

6. **Worker reconciliation.** Running multiple agents concurrently means manually managing worktrees, branches, tmux sessions, and merge conflicts. The closest OSS thing is Ralph (skill in this repo) which hardcodes one path, one branch, one tmux name.

7. **Tickets as second-class.** Prompts and tickets drift. The agent reads a markdown file; the team reads ClickUp/Linear. No round-trip.

The result: AI coding tools are *fast* but require *meticulous human gating* to be safe. The gating is the bottleneck. This platform attacks the gating.

---

## Why this isn't another AI coding tool

We don't compete with Claude Code, Cursor, Aider, Devin, or Replit Agent. We compose with them.

**Strict layering:**

```
┌─────────────────────────────────────────────────────────────┐
│ AI coding tools (Claude Code, Cursor, Aider, custom scripts)│  ← exists
└─────────────────────────────────────────────────────────────┘
                              ↓ uses
┌─────────────────────────────────────────────────────────────┐
│ Autodev runtime (this project)                              │  ← what we build
│   spec → execute → verify → review → land                   │
│   policy hooks · plugin verifiers · ticket round-trip       │
└─────────────────────────────────────────────────────────────┘
                              ↓ uses
┌─────────────────────────────────────────────────────────────┐
│ Git + CI + ticket systems + cloud (existing infra)          │  ← exists
└─────────────────────────────────────────────────────────────┘
```

The runtime exposes a CLI and SDK. AI coding tools call into it. Existing infra is unchanged.

**Coexistence proof points:**

- A Claude Code skill that wraps the CLI — Claude Code becomes a richer "spec → land" experience without giving up its other capabilities.
- A Cursor agent that delegates verification to the runtime.
- Aider users running `autodev verify` after their session.
- A pure CLI for users who want no IDE involvement.
- A GitHub Action that runs verification + policy on every PR, regardless of how the PR was authored (human or agent).

If a competing AI coding platform launches tomorrow, this still has value — because the gating problem is universal and orthogonal to who's typing.

---

## Core thesis (the non-negotiables)

These are the principles that distinguish this from "yet another AI tool."

### 1. Specs are artifacts, not prompts

A `task-spec.yaml` is a parseable contract:

```yaml
id: tier1-fix-transformmenu
title: Fix transformMenu to read data.menu first
ticket: clickup://86e13u7dk
files_allowed:
  - services/backend.ts
  - __tests__/backend.test.ts
files_forbidden:
  - app/(auth)/**
  - .env*
constraints:
  - no_new_dependencies
  - no_schema_changes
acceptance:
  - test: backend.test.ts:transformMenu reads data.menu
    must_pass: true
  - tsc_clean: true
verification:
  - typecheck
  - unit_tests
  - regression_hunter
```

The runtime parses this and produces the agent prompt. The agent's task scope is bounded mechanically. Diff that touches `app/(auth)/*` is **rejected by the runtime**, not by reviewer judgment.

Specs round-trip with tickets. `autodev spec from clickup://<id>` reads the ticket and writes a spec. `autodev spec sync` writes status back. Tickets become the source of truth for "what was asked"; specs become the source of truth for "what was built and verified."

### 2. Policies are deterministic, not stochastic

Every policy is code, not a sentence:

```python
# policies/no_real_place_order.py
def check(diff: Diff) -> PolicyResult:
    new_calls = diff.new_call_sites('placeOrder')
    allowed = {'app/(main)/checkout.tsx:handlePlaceOrder'}
    if new_calls - allowed:
        return PolicyResult.fail(
            f"new placeOrder() calls outside allowed sites: {new_calls - allowed}",
            evidence=diff.show_calls(new_calls - allowed),
        )
    return PolicyResult.pass_()
```

Policies live in `policies/` directories. The runtime applies them as PreToolUse hooks (block before commit) and PR check (block before merge). They're trivially testable.

A team's policy library is its safety culture, encoded.

### 3. Verifiers compose

Verification isn't "did tests pass." It's a composable graph:

```
typecheck         (always)
  ↓
unit_tests        (always)
  ↓
dep_audit         (rejects new package.json deps unless flagged)
  ↓
schema_probe      (hits dev backend, validates response shapes against types)
  ↓
mock_parity       (runs mock + live test suites, diffs behavior)
  ↓
regression_hunter (LLM agent: reviews diff for cross-cutting concerns)
  ↓
live_smoke        (Playwright/Browserbase: drives UI, asserts golden path)
```

Each verifier is a plugin. Users compose their verification graph in `.autodev/verify.yaml`. Failure of any verifier blocks `land`.

This is the layer that would have caught the `USE_MOCK_DATA` bug we missed in the Ralph run — `mock_parity` verifier runs the test suite in both modes and diffs.

### 4. Pause and ask, don't commit and pray

Executors return structured outcomes:

```typescript
type TaskResult =
  | { status: 'done'; commits: string[]; verifiers: VerifierResult[] }
  | { status: 'blocked'; question: string; evidence: string[]; options?: string[] }
  | { status: 'failed'; reason: string; reverted: boolean };
```

`blocked` is first-class. The runtime queues blocked tasks; coordinator (or human) drains the queue. No more "agent guessed wrong because the prompt was ambiguous."

### 5. Rollback is first-class

Every land is gated:

```bash
autodev land <pr-id> \
  --baseline tag/v1.2.3 \
  --watch error-budget=1% \
  --watch p99-latency-delta=+50ms \
  --watch sentry-issues=+5 \
  --revert-on-breach
```

The platform installs the watcher (default 1 hour observation window, configurable). On breach, auto-revert + alert. Rollback isn't a manual scramble; it's a contract attached to the merge.

### 6. Coordinator > worker

The smartest model plans + reviews. Cheaper models execute mechanical tasks. The coordinator holds architecture context; workers get task-scoped context.

```
coordinator (Claude Opus / GPT-4 / DeepSeek-R1)
  ├→ planner: ticket → spec tree
  ├→ dispatcher: spec → executor pool
  ├→ reconciler: merges executor outputs
  ├→ reviewer: cross-cutting risk annotation
  └→ lander: gated merge
              ↓
            executor pool (Haiku / Sonnet / Llama-3 / local)
              ├→ executor-1: task A
              ├→ executor-2: task B
              └→ executor-N: task N
```

Smartest-where-it-matters allocation cuts cost without sacrificing correctness.

### 7. Memory is a first-class output

Every run writes back: which policies fired, which verifiers caught real bugs, which task specs needed revision, what the team learned. Future runs read this memory. Specs improve over time without manual tuning.

---

## Architecture

### Directory layout (in a consuming repo)

```
.autodev/
  config.yaml              # runtime settings, plugin selection
  verify.yaml              # verifier graph
  policies/
    no_new_deps.py
    no_real_place_order.py
    no_auth_edits.py
    schema_consistency.py
  specs/
    <run-id>/
      plan.yaml
      tasks/
        001-fix-transformmenu.yaml
        002-fix-getselectedpaymentmethod.yaml
        ...
  runs/
    <run-id>/
      state.json           # task-by-task state
      executors/
        001/log.txt
      verifier-results/
      policy-results/
      review.md
      baseline.tag
.claude/                   # if using Claude Code
  skills/
    autodev/               # ships as plugin
      plan.md
      execute.md
      verify.md
      review.md
      land.md
  hooks/
    pre-edit.sh            # invokes policy checks
    post-commit.sh         # invokes verifier
  agents/
    autodev-executor.md    # subagent definition
    autodev-reviewer.md
```

### Components

**Runtime (Rust or Go, single binary)**
- `autodev plan --from <ticket-uri>` → spec tree
- `autodev execute <spec> [--worktree <path>] [--agent <name>]` → executor invocation
- `autodev verify <branch> [--graph verify.yaml]` → run verifier graph
- `autodev review <branch>` → annotated diff
- `autodev land <pr> [--watch ...]` → gated merge
- `autodev fan-out <plan> --workers N` → parallel executor pool
- `autodev policy check <diff>` → run policy library

Rust/Go choice: single binary, fast startup, zero runtime deps. Critical for hook performance — a `PreToolUse` hook that takes 500ms breaks the IDE feel.

**Policy library (Python plugin system)**
- Each policy is a Python file with a `check(diff: Diff) -> PolicyResult` function
- `Diff` is a rich AST + text view of the change
- Policies are testable, versionable, shareable
- Community-contributed policy packs (e.g., `autodev-policies-django`, `autodev-policies-react`)

**Verifier plugins (any language, JSON-RPC over stdio)**
- Standard interface: read spec + diff from stdin, emit verifier result on stdout
- Plugins ship as Docker images or local binaries
- Composable in `verify.yaml`

**Agent adapters**
- `agent-claude-code/` — invokes Claude Code subagents via the Agent SDK
- `agent-cursor/` — drives Cursor background agents
- `agent-aider/` — wraps Aider sessions
- `agent-anthropic-sdk/` — direct Anthropic API for headless execution
- `agent-openai/`, `agent-ollama/`, etc.

Each adapter handles: spec → prompt translation, output parsing, error mapping.

**Ticket adapters (MCP servers)**
- `mcp-github-issues`
- `mcp-clickup` (already exists in the broader Claude ecosystem)
- `mcp-linear`
- `mcp-jira`

The runtime calls MCP servers for ticket round-trip.

---

## Policy DSL

Policies are Python because: introspection-friendly, easy to test, every backend dev reads it. We're not inventing a new DSL.

```python
# policies/no_new_deps.py
from autodev import Policy, Diff, PolicyResult

class NoNewDepsPolicy(Policy):
    name = "no_new_deps"
    description = "Block changes that add new entries to package.json dependencies"

    def check(self, diff: Diff) -> PolicyResult:
        changes = diff.json_changes('package.json', path='dependencies')
        added = changes.added_keys()
        if added:
            return PolicyResult.fail(
                f"new dependencies added: {added}",
                evidence=diff.show('package.json'),
                fix_hint="if intentional, add `--allow-new-deps` to the spec or remove the import",
            )
        return PolicyResult.pass_()
```

```python
# policies/no_real_place_order.py
from autodev import Policy, Diff, PolicyResult

class NoRealPlaceOrderPolicy(Policy):
    name = "no_real_place_order"
    description = "Block new placeOrder() call sites outside the allowed list"

    allowed_sites = {
        'app/(main)/checkout.tsx:handlePlaceOrder',
    }

    def check(self, diff: Diff) -> PolicyResult:
        new_calls = diff.new_call_sites('placeOrder')
        bad = new_calls - self.allowed_sites
        if bad:
            return PolicyResult.fail(
                f"new placeOrder() calls outside allowed sites: {bad}",
                evidence=diff.show_calls(bad),
                severity='blocker',
            )
        return PolicyResult.pass_()
```

Policies are unit-testable:

```python
def test_no_new_deps_catches_added():
    diff = Diff.from_string('''
    --- package.json
    +++ package.json
    @@ ...
    +    "lodash": "^4.17.21",
    ''')
    result = NoNewDepsPolicy().check(diff)
    assert result.failed
    assert "lodash" in result.message
```

The community can ship policy packs:

- `autodev-policies-react` — accessibility, hooks rules, no-direct-DOM
- `autodev-policies-rails` — N+1 detection, no-master-key-in-diff
- `autodev-policies-aws` — no-broad-iam, no-public-s3
- `autodev-policies-pii` — block changes to fields tagged @pii without security review

This is the moat. The agent layer commoditizes; the policy library compounds.

---

## Verifier examples

**`mock_parity` verifier (the bug we missed in our Ralph run):**

```yaml
# .autodev/verifiers/mock_parity.yaml
name: mock_parity
description: Run test suite in mock and live modes; fail if behavior diverges in changed files

steps:
  - run: USE_MOCK_DATA=true npx jest --json -- ${changed_test_files}
    capture: mock_results
  - run: USE_MOCK_DATA=false npx jest --json -- ${changed_test_files}
    capture: live_results
  - compare: { left: mock_results, right: live_results, on: [outcome, errors] }
    fail_if: divergence
```

**`schema_probe` verifier:**

```yaml
name: schema_probe
description: Hit dev backend, validate response shapes against types/

steps:
  - run: autodev-schema-probe \
           --backend ${DEV_BACKEND_URL} \
           --types types/ \
           --auth-token ${DEV_AUTH_TOKEN}
    fail_if: drift_detected
```

**`regression_hunter` verifier (LLM-powered):**

```yaml
name: regression_hunter
description: LLM reviews diff for cross-cutting concerns the implementer might've missed

steps:
  - run: autodev-llm-review \
           --diff ${DIFF} \
           --context "files-touched, recent-incidents, common-pitfalls.md" \
           --model claude-haiku-4-5 \
           --output structured
    fail_if: severity >= warning
```

The LLM verifier runs against a focused, cross-cutting question — not "review the code" (too vague) but "what could break in production that this PR doesn't test for?" That's a tractable question.

---

## Spec format

```yaml
# specs/<run-id>/tasks/001-fix-transformmenu.yaml
schema_version: "1"
id: tier1-fix-transformmenu
title: Fix transformMenu to read data.menu first
parent_run: tier1-pre-v1.0-2026-04-27

ticket:
  source: clickup
  id: 86e13u7dk
  url: https://app.clickup.com/t/86e13u7dk

context:
  why: |
    services/backend.ts:104 reads data.categories ?? data, but the real
    /restaurants/:id/menu API returns { menu: [...] }. Live menus render empty.
  evidence:
    - file: services/backend.ts
      lines: [104]
      finding: "data.categories ?? data — wrong"
    - api_response_shape: '{ "menu": [...] }'
      source: dev-restaurants.famishedlabs.com

scope:
  files_allowed:
    - services/backend.ts
    - __tests__/backend.test.ts
  files_forbidden:
    - .env*
    - app/(auth)/**

constraints:
  - id: no_new_dependencies
  - id: no_schema_changes
  - id: additive_only

acceptance:
  - description: transformMenu prefers data.menu
    test:
      file: __tests__/backend.test.ts
      name: transformMenu reads { menu } shape
  - description: existing fallbacks preserved
    test:
      file: __tests__/backend.test.ts
      name: transformMenu falls back to categories then data

verification:
  graph: default-typescript
  extra:
    - schema_probe

estimate:
  loc: 5-15
  time: 10m

rollback:
  baseline_tag_required: true
```

The runtime consumes this. The executor agent gets a *generated prompt*, not the YAML directly. Generation is deterministic, debuggable, version-controlled.

---

## Plugin architecture

The platform is a kernel. Everything else is plugins.

**Kernel responsibilities:**
- Spec parsing + validation
- Run-state machine (pending → executing → verifying → reviewing → landed | blocked | failed)
- Worktree + branch management
- Plugin discovery + invocation
- Hook orchestration
- Memory persistence

**Plugin types:**
- `agent` — wraps a coding agent (Claude Code, Cursor, Aider, raw LLM SDK)
- `verifier` — runs a verification step
- `policy` — applies a policy check
- `ticket` — round-trips with a ticket system (via MCP)
- `runner` — executes builds/tests (npm, pytest, go test, custom)
- `notifier` — surfaces blocked tasks (Slack, GitHub comment, email, console)

Plugin manifest:

```toml
# autodev-plugin.toml
name = "regression-hunter"
type = "verifier"
version = "0.3.1"
entrypoint = "./bin/regression-hunter"
config_schema = "./config-schema.json"
requires_runtime_version = ">=0.1.0"
```

`autodev plugin install <name>` from a registry. Plugins ship as binaries or container images.

---

## OSS strategy & positioning

### Coexistence matrix

| Tool | Relationship | What we add |
|------|-------------|-------------|
| Claude Code | First-class skill + agents | Spec discipline, policy enforcement, verifier graph, multi-worker dispatch |
| Cursor | Background agent integration | Same |
| Aider | CLI wrap | Same |
| Devin / Codex | Optional executor adapter | Spec input, verification, policy gating |
| GitHub Copilot Workspace | PR-time integration | Verifier + policy as PR check |
| Replit Agent | Adapter | Same |
| Continue / Cline | Skill + verifier integration | Same |

We don't replace any of these. Every one of them gets safer, more accurate, and more team-friendly.

### Why OSS

1. **The policy library compounds.** The value is in the breadth of policies and verifiers. That's only built by a community. Closed-source can't compete with `autodev-policies-rails` having 200 contributors.

2. **Trust through inspectability.** Teams won't bet production safety on a closed-source policy engine. The whole point is determinism — that needs to be auditable.

3. **No vendor lock-in.** The runtime works against any agent, any LLM, any ticket system. That's only credible if it's OSS.

4. **Distribution.** Open-source CI tools spread laterally through engineering teams faster than SaaS. Once one engineer adds it to their PR pipeline, the team adopts.

### Optional commercial layer (later)

After v1.0 OSS launch, optional managed offering:

- **Hosted runs** — `autodev land --hosted` runs verifier graph in a hosted preview env (saves teams from running their own verifier infra)
- **Team policy registry** — private policy/verifier packs for orgs
- **Compliance bundles** — SOC2, HIPAA, PCI-DSS policy packs with attestation
- **Incident dashboards** — error-budget watchers across all landings, MTTR tracking

OSS core stays OSS. Commercial layer is purely "we host this for you."

### Comparison positioning

| Capability | Devin | Cursor Agents | Aider | Claude Code | **Autodev** |
|------------|-------|---------------|-------|-------------|-------------|
| Code generation | ✅ | ✅ | ✅ | ✅ | ❌ (delegates) |
| Spec discipline | ❌ | ❌ | ❌ | ❌ | ✅ |
| Policy as code | ❌ | ❌ | ❌ | partial (hooks) | ✅ |
| Verifier graph | ❌ | ❌ | ❌ | ❌ | ✅ |
| Pause-and-ask | ❌ | ❌ | ❌ | partial | ✅ |
| Multi-worker | partial | ❌ | ❌ | partial | ✅ |
| Rollback gating | ❌ | ❌ | ❌ | ❌ | ✅ |
| OSS | ❌ | ❌ | ✅ | partial | ✅ |
| Agent-agnostic | ❌ | ❌ | ❌ | ❌ | ✅ |
| Ticket round-trip | partial | ❌ | ❌ | ❌ | ✅ |

The "agent-agnostic" row is the wedge. Every other row in our column maps to a recurring pain point in the others.

---

## Roadmap

### v0 — single-team usable (target: 6 weeks)

**Scope:**
- `autodev plan` (manual YAML, no ticket integration yet)
- `autodev execute` with one agent adapter (Claude Code via Agent SDK)
- `autodev verify` with: typecheck, unit-test, dep-audit, mock-parity verifiers
- `autodev land` with simple gated merge (no rollback yet)
- 5 built-in policies: no-new-deps, no-real-place-order, no-auth-edits, no-schema-changes, additive-only
- Spec format v1
- Single CLI binary (Go), runs on macOS + Linux
- Documentation site

**Success criteria:**
- One team (us) uses it for one full sprint of real work, replaces Ralph
- Catches one real bug that would've shipped otherwise (validates the thesis)
- Used by 10 external GitHub stargazers within 4 weeks of launch

### v1 — community-friendly (target: +12 weeks)

- Plugin system live (verifier + policy plugins)
- Ticket adapters: GitHub Issues, Linear, ClickUp
- Agent adapters: Aider, raw OpenAI/Anthropic SDK, Ollama
- `pause-and-ask` flow with notification plugins (Slack, GitHub PR comment)
- Multi-worker dispatcher with conflict reconciliation
- `regression_hunter` and `schema_probe` verifiers
- Cookbook: 20 real-world spec/policy/verifier examples

**Success criteria:**
- 1k stargazers, 50 active community contributors
- 5+ third-party plugins
- Used in production by 3+ teams beyond founders

### v2 — production-grade (target: +24 weeks)

- Rollback gating with watchers (error-budget, latency, Sentry, custom)
- Live-smoke verifier with Playwright + Browserbase
- Memory layer that learns spec patterns
- IDE integrations (VS Code, JetBrains, Zed)
- Cursor / Continue / Cline first-class adapters
- GitHub App for PR-time policy + verifier checks
- Hosted runs (commercial offering)

**Success criteria:**
- 10k stars, 500 contributors
- Profitable hosted offering (50+ paying teams)
- Adopted by at least one well-known OSS project as their merge gate

### v3 — platform (target: 12+ months out)

- Cross-repo refactors (multi-repo specs, atomic landing across repos)
- Compliance bundles (SOC2, HIPAA, PCI-DSS attested policy packs)
- Distributed worker pools (run executors in cloud sandbox: Vercel Sandbox, Modal, etc.)
- Incident dashboards + MTTR analytics
- Standards body work: spec format becomes a vendor-neutral interchange format

---

## Concrete v0 build order

Week 1–2:
- Repo scaffold (Go binary, project layout, CI)
- Spec format v1 + YAML parser + validator
- Run-state machine + worktree management
- Single agent adapter: Claude Code via Agent SDK

Week 3:
- Verifier interface (plugin-style, even if all built-in for v0)
- Built-in verifiers: typecheck, unit_tests, dep_audit
- `autodev verify` end-to-end

Week 4:
- Policy interface + 5 built-in policies
- `autodev policy check` end-to-end
- PreToolUse hook script that calls policy check

Week 5:
- `autodev plan` (YAML-first, no ticket integration)
- `autodev execute` end-to-end
- `autodev land` with simple merge gating

Week 6:
- Mock-parity verifier
- Documentation site (mkdocs or similar)
- README + quickstart + examples
- v0 launch

**Self-dogfooding:** Use it on FamAI-Native and famished-backend from week 4 onward. Every sprint we run replaces a Ralph invocation.

---

## Risks & open questions

### Risks

1. **The "yet another tool" problem.** Engineers are saturated on AI tooling. The wedge has to be obvious in 30 seconds. Mitigation: lead with a single concrete demo (the mock-mode bug we missed → caught by mock-parity verifier).

2. **Policy library cold-start.** A platform without a rich policy library is just a CLI. Need 50+ high-quality policies before launch. Mitigation: hand-write 30, partner with 5 OSS projects to write 20 more in exchange for early adoption.

3. **Plugin protocol churn.** Plugin interfaces are notoriously hard to get right early. Mitigation: dogfood internally with a frozen interface for v0; don't open the plugin protocol externally until v1.

4. **Maintenance burden of the runtime.** A Go/Rust binary on macOS + Linux with hooks into 10 different AI agents — that's a lot of integration surface. Mitigation: ship adapters as separate binaries with their own release cadence.

5. **Devin / commercial autonomy tools moving down-stack.** They might launch their own verification layer. Mitigation: OSS + agent-agnosticism is the moat; even Devin's customers want pluggable policies.

### Open questions

1. **Worktree vs sandbox.** Local worktrees (Ralph-style) or cloud sandboxes (Vercel Sandbox / Modal / Daytona)? Local is faster to start, sandbox is safer + more reproducible. Probably both, opt-in via spec.

2. **Coordinator location.** Does the coordinator run in the user's IDE (Claude Code), in a CLI, or as a daemon? Different ergonomics. Likely all three with a shared protocol.

3. **Memory format.** Plain JSON, sqlite, or git-tracked YAML? Sqlite for speed, YAML for diffability. Probably both: hot state in sqlite, summarized history in git-tracked YAML.

4. **LLM lock-in for the LLM-powered verifiers (`regression_hunter`).** Bake in Claude or stay model-agnostic? Stay agnostic, support routing via Vercel AI Gateway or LiteLLM.

5. **Pricing for hosted commercial layer.** Per-run, per-seat, per-team? Probably per-team with a generous free tier (100 runs/month). Per-run rewards heavy usage with high cost; per-seat doesn't reward integration depth.

6. **Naming.** `autodev` is descriptive but boring. Real names worth considering: `Compose`, `Anvil`, `Lattice`, `Tract`, `Threshold`. Founder picks before v0 launch.

---

## What this looks like next to current Ralph

```
# Today (Ralph):
/ralph                          # one tmux session, one branch, one prompt file
                                # no spec discipline, no policy enforcement,
                                # only unit-test verification, no rollback

# v0 of this platform:
autodev plan --from clickup://86e13u75g    # tickets → spec tree
autodev fan-out plan.yaml --workers 4      # parallel executors via Claude Code
autodev verify --graph default              # typecheck + tests + mock-parity + dep-audit
autodev review run/2026-04-27-tier1        # risk-annotated diff
autodev land run/2026-04-27-tier1 \         # gated merge with rollback contract
  --watch error-budget=1% --revert-on-breach
```

Same outcome, mechanically safer, with caught bugs that Ralph missed.

The Ralph skill becomes a degenerate special case of `autodev fan-out --workers=1 --policy=none --verify=basic`. We deprecate it gracefully.

---

## Closing — strategic shape

The AI coding boom over the next 18 months will produce dozens of agents and tools. Most will compete for the "best typer" position. **The compounding asset is the layer underneath them: spec format, policy library, verifier graph, ticket round-trip.**

If we ship the boring layer well, we become the substrate every AI coding tool integrates against — not the product, but the protocol. That's a more durable position than any single agent can hold.

The opportunity is now: no one has filled this slot in OSS, the closed-source players (Devin, Cursor) are too vertically integrated to commit to agent-agnosticism, and the demand is obvious to any team that's tried shipping AI-generated PRs to production.

This is a 12-month window. After that, someone fills it.
