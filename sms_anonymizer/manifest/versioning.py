import json
import os

_INITIAL_VERSION = "1.0.0"


def _parse(version: str) -> tuple[int, int, int]:
    major, minor, patch = (int(p) for p in version.split("."))
    return major, minor, patch


def _bump_patch(version: str) -> str:
    major, minor, patch = _parse(version)
    return f"{major}.{minor}.{patch + 1}"


def next_corpus_version(state_path: str, output_hash: str) -> str:
    """SemVer that only advances when the output actually changed: same
    hash as last run keeps the same version, a different hash bumps the
    patch number. First-ever run starts at 1.0.0."""
    if os.path.exists(state_path):
        with open(state_path, encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {"version": _INITIAL_VERSION, "output_hash": None}

    if state["output_hash"] == output_hash:
        version = state["version"]
    elif state["output_hash"] is None:
        version = _INITIAL_VERSION
    else:
        version = _bump_patch(state["version"])

    state["version"] = version
    state["output_hash"] = output_hash

    parent = os.path.dirname(state_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    return version
