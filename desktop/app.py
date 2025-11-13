from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict

from PySide6 import QtCore, QtWidgets

from ui.main_window import UltimateMainWindow

CONFIG_PATH = Path(__file__).resolve().parent.parent / "bot" / "config.yml"
LICENSE_API = "http://127.0.0.1:8000"


def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    import yaml

    with CONFIG_PATH.open("r", encoding="utf-8") as fp:
        return yaml.safe_load(fp)


def save_config(data: Dict[str, Any]):
    import yaml

    with CONFIG_PATH.open("w", encoding="utf-8") as fp:
        yaml.safe_dump(data, fp)


class DesktopController(QtCore.QObject):
    log_received = QtCore.Signal(str)
    status_changed = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.session = None

    async def ensure_session(self):
        if self.session is None:
            import aiohttp

            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session:
            await self.session.close()

    async def validate_license(self, key: str):
        session = await self.ensure_session()
        payload = {"key": key, "guild_id": "desktop", "machine_fingerprint": "desktop"}
        async with session.post(f"{LICENSE_API}/licenses/validate", json=payload) as resp:
            return await resp.json()

    async def fetch_licenses(self, token: str):
        session = await self.ensure_session()
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get(f"{LICENSE_API}/licenses", headers=headers) as resp:
            return await resp.json()

    async def create_license(self, token: str, payload: Dict[str, Any]):
        session = await self.ensure_session()
        headers = {"Authorization": f"Bearer {token}"}
        async with session.post(f"{LICENSE_API}/licenses", headers=headers, json=payload) as resp:
            return await resp.json()


class UltimateApplication(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setStyle("Fusion")
        self.setAttribute(QtCore.Qt.AA_DontCreateNativeWidgetSiblings)
        self.controller = DesktopController()
        self.main_window = UltimateMainWindow(controller=self.controller, config_loader=load_config, config_saver=save_config)
        self.main_window.show()


def main():
    app = UltimateApplication([])
    app.exec()


if __name__ == "__main__":
    main()
