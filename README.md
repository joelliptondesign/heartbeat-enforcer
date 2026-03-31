# Heartbeat Enforcer

Deterministic validation for structured change logs produced during AI-assisted coding.

AI coding tools are changing how code gets written.

We already have strong systems for tracking code itself, like Git. But we don’t have an equivalent way to track the reasoning behind AI-generated changes.

Heartbeat Enforcer acts as Git for AI reasoning.

It enforces structured explanations for every AI-generated change — what changed, what was done, and why — so the reasoning stays with the code instead of getting lost in chat history.

## The Problem

AI coding tools can change a lot of code quickly. The code changes usually survive in the repository, but the explanation for those changes often does not.

That explanation tends to live in chat history, temporary prompts, or a developer's memory. A diff shows what changed. It usually does not explain why the change was made, what the tool was trying to do, or whether every changed file was actually accounted for.

That becomes a practical problem when you want to review work later, reproduce a run, or hand the repository to someone who was not present for the original chat.

## Common Approaches (And Their Limits)

Saving prompts helps, but prompts are not the same thing as the final implemented change. They also are not reliably stored next to the code.

Relying on git diffs helps, but diffs only show edits. They do not require a clear explanation of intent, and they do not enforce that every changed file was described.

Relying on commit messages helps, but commit messages are optional, inconsistent, and often too short to explain the real reason behind a change. They also are not tied to a structured schema the way validation can be.

## The Solution — Heartbeat Enforcer

Heartbeat Enforcer validates a JSONL heartbeat file that records change events. In a workflow using this tool, each run is expected to append one structured event describing the work that was just done.

Each event must describe:

- what changed: `files`
- what was done: `action`
- why it was done: `reason`

Validation fails when the record is malformed, incomplete, refers back to outside context, or does not match the expected file coverage.

## Key Benefits

- Deterministic enforcement
- Full change coverage when used with `--changed-files`
- Self-contained reasoning in the repository
- No dependence on chat history
- Works with any AI coding tool that can append a JSONL record

## Planned vs Autonomous Actions

Each operation is labeled as either `planned` or `autonomous`.

- Planned: directly requested by the user
- Autonomous: added by the AI to support or complete the task

This makes it immediately visible when the AI goes beyond the original request.

Instead of guessing why something was added, you get a clear, structured explanation of both the change and the reasoning behind it.

This helps surface unexpected behavior early and reduces surprise changes in the codebase.

## Example

Changed files:

```text
app.py
auth.py
config.py
```

Corresponding heartbeat event:

```json
{
  "timestamp": "2026-03-31T09:00:00Z",
  "event_type": "change_ops",
  "actor": "system-agent",
  "payload": {
    "summary": "Initial project setup with auth and config modules",
    "operations": [
      {
        "mode": "autonomous",
        "files": ["app.py", "auth.py", "config.py"],
        "action": "created",
        "reason": "Established base project structure with configuration and authentication modules"
      }
    ]
  }
}
```

This example is taken directly from `sample_repo/telemetry/executor_heartbeat.jsonl`.

## How It Works

1. Optionally capture the current heartbeat line count as a baseline.
2. Run your AI coding tool.
3. Append one new JSON event to the heartbeat file.
4. Validate the heartbeat file, optionally checking changed-file coverage too.

There are two validation modes:

- Baseline mode: requires exactly one new line since the saved baseline, then validates only that new last event.
- Tail mode: validates only the last event in the file, with no baseline requirement.

## Zero-Friction Integration

Heartbeat Enforcer is designed to be automatic in practice.

You do not manually write heartbeat events.

Instead, you instruct your AI coding tool to append them as part of every run.

Common patterns:

- Add a one-line instruction to your prompt:

  After completing the task, append a heartbeat event to telemetry/executor_heartbeat.jsonl.

- Use a saved snippet or slash command:

  /run-with-heartbeat

- Configure your agent once (recommended):

  Every code change must append a valid heartbeat event.

After this, heartbeat logging becomes part of the execution itself, not an extra step.

The responsibility for structured explanation moves from the human to the AI.

## Installation

Heartbeat Enforcer has no runtime dependencies beyond Python.

- Python requirement: `>=3.6`
- Console script: `heartbeat`

Install it from the repository root:

```bash
pip install -e .
```

## Usage

Capture a baseline line count:

```bash
heartbeat baseline examples/valid_heartbeat.jsonl
```

Validate in baseline mode:

```bash
heartbeat validate --heartbeat examples/valid_heartbeat.jsonl --baseline 0 --changed-files examples/changed_files.txt
```

Validate in tail mode:

```bash
heartbeat validate --heartbeat examples/valid_heartbeat.jsonl --changed-files examples/changed_files.txt
```

Actual CLI behavior:

- `heartbeat baseline <path>` prints the number of lines in the file. If the file does not exist, it prints `0`.
- `heartbeat validate --heartbeat <path> [--baseline N] [--changed-files path]` prints JSON.
- PASS output is exactly:

```json
{"status": "PASS"}
```

- FAIL output has this shape:

```json
{"status": "FAIL", "failure_reasons": ["..."]}
```

- The validate command exits with status code `0` on PASS and `1` on FAIL.

## Heartbeat Schema

Each JSONL line must be a single event with these required fields:

```json
{
  "timestamp": "...",
  "event_type": "change_ops",
  "actor": "non-empty string",
  "payload": {
    "summary": "string",
    "operations": [
      {
        "mode": "planned or autonomous",
        "files": ["non-empty string"],
        "action": "non-empty string",
        "reason": "non-empty string"
      }
    ]
  }
}
```

Validator-backed rules:

- `event_type` must be exactly `"change_ops"`.
- `actor` must be a non-empty string.
- `payload.summary` must exist.
- `payload.operations` must be a non-empty list.
- Each operation `mode` must be `"planned"` or `"autonomous"`.
- Each operation `files` value must be a non-empty list of non-empty strings.
- Duplicate file paths inside a single operation are rejected.
- `action` must be a non-empty string.
- `reason` must be a non-empty string.

## What It Enforces

- Structure: required fields and allowed operation values
- Completeness: every operation must include files, action, and reason
- Self-containment: summaries and reasons cannot rely on phrases like `as discussed`, `see above`, or `per earlier`
- Coverage: when `--changed-files` is supplied, the combined `files` across all operations must match that file list exactly

It also rejects malformed JSON input and empty heartbeat files.

## What It Does Not Do

- It does not judge whether the code change is correct.
- It does not use AI.
- It does not modify code.

## Who This Is For

- Developers using Codex, Claude, or similar AI coding tools
- Teams that need traceability for AI-assisted changes
- Anyone who wants a reproducible, self-contained change history in the repository

Heartbeat Enforcer does one narrow job: it makes sure the last recorded change is described in a structured, reviewable, test-backed way. If you want change history that survives beyond chat, this gives you a concrete enforcement point.
