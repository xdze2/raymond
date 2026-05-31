"""LLM dispatcher: route prompts to a provider+model picked from wiki config.

Model strings are `"<provider>:<model>"`, e.g. `"claude:claude-sonnet-4-6"` or
`"mistral:mistral-small-latest"`. `run_llm("...", model="claude:...")` returns
the raw response string.

`run_claude` is kept as a thin alias for backwards compatibility with the
existing test suite (which patches `dev_server.run_claude`).
"""

from __future__ import annotations

import subprocess

DEFAULT_MODEL = "claude:claude-sonnet-4-6"


def render_prompt(template: str, **vars: str) -> str:
    out = template
    for k, v in vars.items():
        out = out.replace("{" + k + "}", v)
    return out


def _run_claude(model: str, prompt: str, timeout: float = 180.0) -> str:
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


def _run_mistral(model: str, prompt: str) -> str:
    # Imported lazily so `import llm` doesn't require MISTRAL_API_KEY.
    from mistral import mistral_complete

    messages = [{"role": "user", "content": prompt}]
    return mistral_complete(model, messages)


def run_llm(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Dispatch `prompt` to the provider encoded in `model` ("<provider>:<name>")."""
    if ":" not in model:
        raise ValueError(f"model must be '<provider>:<name>', got {model!r}")
    provider, name = model.split(":", 1)
    if provider == "claude":
        return _run_claude(name, prompt)
    if provider == "mistral":
        return _run_mistral(name, prompt)
    raise ValueError(f"unknown provider {provider!r} in model {model!r}")


def run_claude(prompt: str, model: str = "claude-sonnet-4-6", timeout: float = 180.0) -> str:
    """Back-compat alias. Prefer `run_llm("claude:<model>", ...)` in new code."""
    return _run_claude(model, prompt, timeout=timeout)
