"""Small developer command helper for Pantheon Age.

This script intentionally uses only the Python standard library. It is not a
build system; it is a thin, discoverable wrapper around commands that already
exist in the project docs.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv" / "bin" / "python"
UVICORN = ROOT / ".venv" / "bin" / "uvicorn"


PY_COMPILE_TARGETS = (
    "phase1_cli/*.py",
    "phase2_api/*.py",
    "phase2_api/routes/*.py",
    "phase2_api/services/*.py",
    "phase3_persistence/*.py",
    "agentic_runtime/*.py",
    "llm_runtime/*.py",
    "rag/*.py",
    "scripts/*.py",
    "tests/*.py",
)


OFFLINE_TEST_ENV = {
    "PANTHEON_RUN_LIVE_LLM_TESTS": "0",
    "PANTHEON_USE_AGENTIC_LLM": "0",
    "PANTHEON_USE_LLM": "0",
    "PANTHEON_EMBEDDING_PROVIDER": "local",
    "PANTHEON_CANON_RETRIEVAL": "keyword",
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Pantheon Age developer helper.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("doctor", help="Print local setup status without reading secrets.")
    subcommands.add_parser("compile", help="Compile Python modules.")
    subcommands.add_parser("test", help="Run offline Python test suite.")
    subcommands.add_parser("check", help="Run compile and offline tests.")
    subcommands.add_parser("cli", help="Start the Python CLI.")
    subcommands.add_parser("api", help="Start the FastAPI server.")
    subcommands.add_parser("agentic-smoke", help="Run local Agentic Runtime smoke test.")
    subcommands.add_parser("final-demo", help="Run local final demo smoke route.")
    subcommands.add_parser("web-install", help="Install web dependencies.")
    subcommands.add_parser("web-dev", help="Start Vite dev server.")
    subcommands.add_parser("web-build", help="Build the web client.")
    subcommands.add_parser("web-smoke", help="Run web API smoke check. API must be running.")

    args = parser.parse_args(argv)
    if args.command == "doctor":
        return doctor()
    if args.command == "compile":
        return run_py_compile()
    if args.command == "test":
        return run_tests()
    if args.command == "check":
        return run_check()
    if args.command == "cli":
        return run([str(PYTHON), "-m", "phase1_cli.main"])
    if args.command == "api":
        return run([str(UVICORN), "phase2_api.main:app"])
    if args.command == "agentic-smoke":
        env = dict(OFFLINE_TEST_ENV)
        env["PANTHEON_PLAY_PROFILE"] = "local"
        return run([str(PYTHON), "-m", "agentic_runtime.smoke_test"], extra_env=env)
    if args.command == "final-demo":
        env = dict(OFFLINE_TEST_ENV)
        env["PANTHEON_PLAY_PROFILE"] = "local"
        return run([str(PYTHON), "-m", "agentic_runtime.final_demo"], extra_env=env)
    if args.command == "web-install":
        return run(["npm", "install"], cwd=ROOT / "web_ui")
    if args.command == "web-dev":
        return run(["npm", "run", "dev"], cwd=ROOT / "web_ui")
    if args.command == "web-build":
        return run(["npm", "run", "build"], cwd=ROOT / "web_ui")
    if args.command == "web-smoke":
        return run(["npm", "run", "smoke:api"], cwd=ROOT / "web_ui")
    return 2


def doctor():
    print("Pantheon Age dev doctor")
    print(f"Project root: {ROOT}")
    print(f"Python helper: {PYTHON} ({'ok' if PYTHON.exists() else 'missing'})")
    print(f"Uvicorn helper: {UVICORN} ({'ok' if UVICORN.exists() else 'missing'})")
    print(f".env present: {'yes' if (ROOT / '.env').exists() else 'no'}")
    print(f".env.example present: {'yes' if (ROOT / '.env.example').exists() else 'no'}")
    print(f"npm available: {'yes' if shutil.which('npm') else 'no'}")
    print(f"web package: {'ok' if (ROOT / 'web_ui' / 'package.json').exists() else 'missing'}")
    print()
    print("Common commands:")
    print("  ./.venv/bin/python scripts/dev.py check")
    print("  ./.venv/bin/python scripts/dev.py cli")
    print("  ./.venv/bin/python scripts/dev.py api")
    print("  ./.venv/bin/python scripts/dev.py final-demo")
    print("  ./.venv/bin/python scripts/dev.py web-dev")
    return 0


def run_py_compile():
    return run([str(PYTHON), "-m", "py_compile", *expanded_py_compile_targets()])


def run_tests():
    return run([str(PYTHON), "-m", "unittest", "discover", "-s", "tests"], extra_env=OFFLINE_TEST_ENV)


def run_check():
    compile_code = run_py_compile()
    if compile_code != 0:
        return compile_code
    return run_tests()


def run(command, cwd=ROOT, extra_env=None):
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    process = subprocess.run(command, cwd=cwd, env=env, check=False)
    return process.returncode


def expanded_py_compile_targets():
    files = []
    for pattern in PY_COMPILE_TARGETS:
        files.extend(str(path.relative_to(ROOT)) for path in sorted(ROOT.glob(pattern)))
    return files


if __name__ == "__main__":
    raise SystemExit(main())
