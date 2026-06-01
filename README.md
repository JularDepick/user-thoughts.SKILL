<div align="center">

# user-thoughts.SKILL

[![Version](https://img.shields.io/badge/Version-0.2.0-blue)](https://github.com/JularDepick/user-thoughts.SKILL/releases)
[![Copyright](https://img.shields.io/badge/Copyright-JularDepick-0066AA)](./COPYRIGHT)
[![License](https://img.shields.io/badge/License-MIT-yellow)](./LICENSE)
[![Standard](https://img.shields.io/badge/Standard-Agent--SKILL-red)](https://agentskills.io/)

[[English]](./README.md) [[简体中文]](./README_zh-CN.md)

An [Agent Skills](https://agentskills.io/) compliant skill that enables AI agents to automatically organize user input and maintain a **persistent, project-bound idea repository** (mdbase) — so decisions, preferences, and constraints survive across sessions and agent handoffs.

</div>

---

## Why This Skill?

When working with AI agents on a project, users express design decisions, requirements, preferences, and constraints throughout conversations. These details are easily lost — not just within a single session, but critically **across sessions and agent handoffs**.

### The Core Pain Point

Every new session or agent starts from zero. The original user's intent, accumulated decisions, and hard-won constraints evaporate the moment context shifts. The result:

- **Cross-session drift** — A new session re-derives requirements from scratch, often missing nuances the user already explained.
- **Agent handoff loss** — When switching agents or onboarding a collaborator, the successor has no access to the user's accumulated thinking. They guess, they ask again, they deviate.
- **Repeated friction** — Users must re-explain the same decisions and preferences across sessions, eroding trust and momentum.

user-thoughts.SKILL solves this by maintaining a **persistent, project-bound idea repository** that survives session boundaries and transfers cleanly between agents:

- **Capturing** user thoughts automatically during conversations
- **Organizing** them into a structured document library (mdbase) by dimension
- **Preserving** original user wording without simplification
- **Binding** the idea repository to the project lifecycle — not to any single session or agent

Any agent picking up the project reads `mdbase/` and immediately understands what the user wants, what they've decided, and what constraints apply — no re-derivation needed.

### Example: Without vs. With user-thoughts

**Scenario** — A user spends 3 sessions defining a web app's auth flow, UI style, and tech stack. Then they open a new session (or hand off to another agent) to implement the login page.

**Without user-thoughts:**

```
Session 1:  User: "Use OAuth2, not JWT. We got burned by token expiry last project."
Session 2:  User: "Dark theme first, light theme later. Rounded corners, 8px radius."
Session 3:  User: "Next.js + Prisma. No MongoDB — we need relational integrity."
...
Session 4:  [New session / different agent]
            Agent: "I'll set up a login page with JWT auth, sharp corners, and MongoDB."
            User: "Did you even listen to me?!" 😤
```

The new session starts from scratch. All prior decisions are gone.

**With user-thoughts:**

```
Session 1-3: user-thoughts silently records to .ustht/mdbase/
             ├── details/rules.md    → "No JWT. Use OAuth2. Prior project had token expiry issues."
             ├── details/ui/details.md → "Dark theme first. Rounded corners, 8px radius."
             └── details/dev-stack.md  → "Next.js + Prisma. No MongoDB — need relational integrity."

Session 4:   [New session / different agent]
             Agent reads mdbase/ → Already knows all constraints → Implements correctly.
             User: "Perfect." ✅
```

The idea repository bridges the gap. The new agent inherits the user's full decision history.

### Language Policy

- **SKILL source** (`SKILL.md`, `references/`, `assets/`) is written in Chinese and does not change with the user's language
- **Agent output adapts** to the user's language — command feedback, sortin summaries, mdbase displays, and prompts should all match the user's active language
- **User wording preserved** — raw records and mdbase entries keep the user's original language, never translated

---

## Installation

### Prerequisites

| Dependency | Required | Purpose |
|------------|----------|---------|
| `read` / `write` | Yes | Read/write files in `#ustht/` |
| `bash` | Yes | File operations (copy, create dirs) |
| SubAgent | No | Parallel mdbase maintenance |

### How to Install

Place the `user-thoughts/` directory in your agent's skills folder. The exact path depends on your agent:

| Agent | Skills Directory |
|-------|-----------------|
| VS Code / Copilot | `.agents/skills/user-thoughts/` |
| Claude Code | `.claude/skills/user-thoughts/` |
| OpenCode | `.opencode/skills/user-thoughts/` |
| Generic | Check your agent's documentation |

After installation, the agent discovers the skill automatically via the YAML frontmatter in `SKILL.md`.

---

## Quick Start

1. **Install** the skill (see above)
2. **Start talking** about your project — the skill activates automatically when you express project ideas
3. **Use commands** when needed:
   - `/ustht status` — check current state
   - `/ustht sortin` — organize thoughts into mdbase
   - `/ustht mdbase show` — view the idea repository

---

## How It Works

The skill uses **three-stage progressive disclosure** to minimize context overhead:

1. **Discovery** — Agent reads `name` and `description` from YAML frontmatter (~100 words, always in context). This is the triggering mechanism — the agent decides whether to consult the skill based on the description.
2. **Activation** — Agent loads `SKILL.md` body (core instructions, ~300 lines). Contains workflow, commands, operating modes, and key rules.
3. **Execution** — Agent loads `references/` files on demand. Only read when specific behaviors need detailed specs (e.g., `sortin.md` for maintenance algorithm, `commands.md` for regex matching).

This means the skill stays lightweight until depth is needed — a simple `/ustht status` only needs stage 2, while a complex `resort` may load stage 3.

### Workflow

```
User speaks → Agent identifies project thought → Writes to raw/ (instant plan)
         ↓
User runs /ustht sortin → Agent processes raw/ → Appends to mdbase/ by dimension
         ↓
User runs /ustht mdbase show → Agent displays organized idea repository
```

### Operating Modes

| Mode | Condition | Behavior |
|------|-----------|----------|
| **Instant Planning** | `SKILL_STATUS=on` + `INSTANT_STATUS=on` | Auto-captures user thoughts into raw/ |
| **Passive** | `SKILL_STATUS=on` + `INSTANT_STATUS=off` | Only responds to commands |
| **Suspended** | `SKILL_STATUS=off` | Write commands return errors; read-only commands still work |
| **Read-only** | Required tools missing | Only read commands available |

---

## Skill Structure

```
user-thoughts/
├── SKILL.md                    # Entry point (frontmatter + core instructions)
├── references/                 # Detailed specs (loaded on demand)
│   ├── commands.md             # Command regex & natural language mapping
│   ├── sortin.md               # Maintenance algorithm & dimension management
│   ├── edge-cases.md           # Boundary scenarios & interaction examples
│   └── safety.md               # Security boundaries & data integrity
├── scripts/                    # Python scripts for agent use (all support --help)
│   ├── common.py               # Shared utility functions (imported by other scripts)
│   ├── status.py               # Show current SKILL state
│   ├── init.py                 # Initialize .ustht/ directory
│   ├── show_raw.py             # View unprocessed raw files
│   ├── show_mdbase.py          # View mdbase index or dimensions
│   ├── sortin.py               # Execute soft maintenance
│   ├── write_raw.py            # Write entries to raw/
│   ├── toggle.py               # Toggle SKILL/INSTANT status
│   └── ignore_ops.py           # Ignore operations
└── assets/
    └── Runtime-Template/       # Template copied to workspace on first use
        ├── define.ini
        └── mdbase/
            ├── README.ai.md
            ├── backlog.md
            └── details/...
```

---

## Commands

```
# Status & Controls
/ustht init                                # Initialize workspace (.ustht/ and templates)
/ustht status                              # Full status overview
/ustht skill [on|off]                      # View/toggle skill
/ustht instant [on|off]                    # View/toggle instant planning

# Maintenance
/ustht sortin [--dry]                      # Soft maintenance (append new thoughts), --dry preview
/ustht resort [--dry]                      # Hard maintenance (reorganize all mdbase), --dry preview

# Ignore
/ustht ignore start|end                    # Begin/end ignore interval (context only)
/ustht ignore [--last]                     # Ignore last recorded thought
/ustht ignore show                         # View ignored records
... /ustht ignore                          # Suffix mode, ignore this message

# View & Export
/ustht raw                                 # View unprocessed raw records
/ustht mdbase show [--all|--dimension]     # View mdbase index or dimension
/ustht mdbase export [--all|--dimension]   # Export mdbase to #export/
/ustht import <path>                       # Scan .md files at path, merge into mdbase
```

Commands can also be triggered by natural language in **any language** — when the user's wording clearly maps to a single command, the agent executes the equivalent command directly. Examples:

- English: "show me the rules" → `/ustht mdbase show rules`
- Chinese: "整理一下想法" → `/ustht sortin`
- Japanese: "想法を整理して" → `/ustht sortin`
- Korean: "상태 보여줘" → `/ustht status`

The agent matches **intent**, not specific keywords. Detailed mapping rules are defined in [references/commands.md](references/commands.md).

---

## Runtime Structure

After first use, the skill creates `.ustht/` in your working directory:

```
<working-dir>/
└── .ustht/
    ├── define.ini             # State & macro constants
    ├── raw/                   # User raw thoughts (date-sharded)
    │   └── yyyy-mm-dd.md
    ├── ignored/               # Ignored thoughts
    │   └── yyyy-mm-dd.md
    ├── export/                # Exported mdbase content
    └── mdbase/                # Organized idea repository
        ├── README.ai.md       # Index & overview
        ├── backlog.md         # Todo items
        └── details/           # Dimension-organized files
            ├── rules.md       # Project rules
            ├── plans.md       # Project plans
            ├── dev-stack.md   # Tech stack
            ├── general.md     # General (catch-all)
            ├── ui/
            │   ├── outline.md
            │   └── details.md
            └── ...            # Extensible
```

---

## Development

This repository contains the skill source (`user-thoughts/`) and its documentation.

```
user-thoughts.SKILL/
├── user-thoughts/          # Skill body (installed to agent's skills directory)
│   ├── SKILL.md            # Entry point with YAML frontmatter + core instructions
│   ├── references/         # Detailed specs loaded on demand
│   ├── scripts/            # Python scripts for agent use
│   └── assets/             # Runtime template copied to workspace on first use
├── README.md               # English documentation
├── README_zh-CN.md         # Chinese documentation
├── LICENSE                 # MIT license
└── COPYRIGHT               # Copyright notice
```

**SKILL source language**: The skill body (`SKILL.md`, `references/`, `assets/`) is written in Chinese. Agent output automatically adapts to the user's language.

**Contributing**: Issues and pull requests are welcome. Please ensure any changes maintain compatibility with the [Agent Skills](https://agentskills.io/) specification.

---

## Changelog

See [GitHub Releases](https://github.com/JularDepick/user-thoughts.SKILL/releases) for version history.

---

## License

[MIT](./LICENSE) — Copyright (c) 2026 JularDepick
