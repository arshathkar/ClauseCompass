#!/usr/bin/env python3
"""Probe configured LLM model IDs and verify they respond.

Usage:
    python scripts/doctor.py          # Uses .env settings
    python scripts/doctor.py --fake   # Validates config schema only (for CI)
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))


async def probe_model(
    base_url: str,
    api_key: str,
    model: str,
    timeout: float = 15.0,
) -> tuple[str, bool, str]:
    """Send a 1-token probe to a model and return (model, success, message)."""
    try:
        import httpx
    except ImportError:
        return model, False, "httpx not installed"

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say OK"}],
        "max_tokens": 5,
        "temperature": 0,
    }

    url = base_url.rstrip("/") + "/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            start = time.monotonic()
            resp = await client.post(url, json=payload, headers=headers)
            elapsed = (time.monotonic() - start) * 1000

            if resp.status_code == 200:
                return model, True, f"OK ({elapsed:.0f}ms)"
            elif resp.status_code == 404:
                return model, False, f"404 — model not found (retired or misspelt?)"
            elif resp.status_code == 429:
                return model, True, f"Rate limited (model exists, quota exhausted)"
            else:
                return model, False, f"HTTP {resp.status_code}: {resp.text[:100]}"
    except httpx.TimeoutException:
        return model, False, f"Timeout after {timeout}s"
    except Exception as e:
        return model, False, f"Error: {e}"


async def main() -> int:
    """Probe all configured models."""
    fake_mode = "--fake" in sys.argv

    # Load env
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

    llm_mode = os.environ.get("LLM_MODE", "replay")
    base_url = os.environ.get("LLM_BASE_URL", "")
    api_key = os.environ.get("LLM_API_KEY", "")
    model_fast = os.environ.get("LLM_MODEL_FAST", "")
    model_analysis = os.environ.get("LLM_MODEL_ANALYSIS", "")
    secondary = os.environ.get("LLM_SECONDARY_MODELS", "")
    fallback_url = os.environ.get("LLM_FALLBACK_BASE_URL", "")
    fallback_key = os.environ.get("LLM_FALLBACK_API_KEY", "")
    fallback_model = os.environ.get("LLM_FALLBACK_MODEL", "")

    print("ClauseCompass — Model Doctor")
    print("=" * 40)
    print(f"Mode: {llm_mode}")
    print()

    if fake_mode or llm_mode in ("fake", "replay"):
        print("Running in config-validation mode (no live probes).\n")
        errors = []
        if not model_fast:
            errors.append("LLM_MODEL_FAST is not set")
        if not model_analysis:
            errors.append("LLM_MODEL_ANALYSIS is not set")
        if llm_mode == "live" and not api_key:
            errors.append("LLM_API_KEY is required for live mode")

        if errors:
            for e in errors:
                print(f"  ✗ {e}")
            return 1
        else:
            print(f"  ✓ Fast model: {model_fast}")
            print(f"  ✓ Analysis model: {model_analysis}")
            if secondary:
                print(f"  ✓ Secondary: {secondary}")
            if fallback_model:
                print(f"  ✓ Fallback: {fallback_model}")
            print("\nOK: Config is valid.")
            return 0

    # Live probing
    if not api_key:
        print("ERROR: LLM_API_KEY is required for live probing.")
        print("Set LLM_MODE=replay for config-only checks.")
        return 1

    models_to_probe: list[tuple[str, str, str]] = []

    if model_fast:
        models_to_probe.append((base_url, api_key, model_fast))
    if model_analysis and model_analysis != model_fast:
        models_to_probe.append((base_url, api_key, model_analysis))
    if secondary:
        for m in secondary.split(","):
            m = m.strip()
            if m:
                models_to_probe.append((base_url, api_key, m))
    if fallback_model and fallback_url:
        key = fallback_key or api_key
        models_to_probe.append((fallback_url, key, fallback_model))

    print(f"Probing {len(models_to_probe)} model(s)...\n")

    results = await asyncio.gather(
        *[probe_model(url, key, model) for url, key, model in models_to_probe]
    )

    failures = 0
    for model, success, message in results:
        status = "✓" if success else "✗"
        print(f"  {status} {model}: {message}")
        if not success:
            failures += 1

    print()
    if failures:
        print(f"FAIL: {failures} model(s) failed probing.")
        print("Check model IDs and update .env if needed.")
        print("Record changes in docs/model-log.md.")
        return 1
    else:
        print("OK: All models responded.")
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
