from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(command: list[str]):
    print(f"[install] $ {' '.join(command)}")
    subprocess.check_call(command)


def install_backend():
    env = ROOT / "venv_backend"
    if not env.exists():
        run([sys.executable, "-m", "venv", str(env)])
    pip = env / ("Scripts" if platform.system() == "Windows" else "bin") / "pip"
    run([str(pip), "install", "-r", str(ROOT / "backend" / "requirements.txt")])


def install_bot():
    env = ROOT / "venv_bot"
    if not env.exists():
        run([sys.executable, "-m", "venv", str(env)])
    pip = env / ("Scripts" if platform.system() == "Windows" else "bin") / "pip"
    run([str(pip), "install", "-r", str(ROOT / "bot" / "requirements.txt")])


def install_desktop():
    env = ROOT / "venv_desktop"
    if not env.exists():
        run([sys.executable, "-m", "venv", str(env)])
    pip = env / ("Scripts" if platform.system() == "Windows" else "bin") / "pip"
    run([str(pip), "install", "-r", str(ROOT / "desktop" / "requirements.txt")])


def main():
    install_backend()
    install_bot()
    install_desktop()
    print("Installation complète. Configurer config.yml à partir de bot/config_example.yml")


if __name__ == "__main__":
    main()
