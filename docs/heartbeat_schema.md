# Heartbeat Schema

Each line in the heartbeat file must be one complete JSON object. The validator checks the most recent line in tail mode.

## Required Top-Level Fields

- `timestamp`: string
- `event_type`: must be `"change_ops"`
- `actor`: non-empty string
- `payload`: object

## Required Payload Fields

- `summary`: string
- `operations`: non-empty array

## Required Operation Fields

Each item in `payload.operations` must include:

- `mode`: `"planned"` or `"autonomous"`
- `files`: non-empty array of non-empty strings
- `action`: non-empty string
- `reason`: non-empty string

## File Coverage Requirement

When validation is run with `--changed-files`, the combined `files` values across all operations must match the contents of that changed-files list exactly. Missing files cause failure. Extra files also cause failure.

## Valid JSONL Example

This event matches the validator schema and passes when used with a `changed_files.txt` file containing:

```text
app.py
auth.py
config.py
```

```json
{"timestamp":"2026-04-01T12:00:00Z","event_type":"change_ops","actor":"codex","payload":{"summary":"Added authentication wiring for the application entrypoint and configuration.","operations":[{"mode":"autonomous","files":["auth.py"],"action":"created","reason":"Implemented the authentication module required by the requested feature."},{"mode":"planned","files":["app.py","config.py"],"action":"updated","reason":"Integrated the authentication module into startup and configuration so the changed files are fully covered."}]}}
```
