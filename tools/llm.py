"""Thin wrapper around the `claude` CLI for one-shot prompts."""

from __future__ import annotations

import subprocess

DEFAULT_MODEL = "claude-sonnet-4-6"


def run_claude(prompt: str, model: str = DEFAULT_MODEL, timeout: float = 180.0) -> str:
    result = subprocess.run(
        ["claude", "--print", "--model", model],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed ({result.returncode}): {result.stderr.strip()}")
    return result.stdout


def render_prompt(template: str, **vars: str) -> str:
    out = template
    for k, v in vars.items():
        out = out.replace("{" + k + "}", v)
    return out
