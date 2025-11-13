from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict

from PySide6 import QtCore, QtGui, QtWidgets


GLASS_STYLE = """
QWidget {
    background-color: rgba(22, 22, 26, 160);
    color: #F5F5F5;
    font-family: 'SF Pro Display';
}
QLabel#titleLabel {
    font-size: 28px;
    font-weight: 600;
}
QPushButton {
    background-color: rgba(255, 255, 255, 20);
    border-radius: 12px;
    padding: 10px 16px;
    color: #ffffff;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 40);
}
QLineEdit, QTextEdit {
    background-color: rgba(255, 255, 255, 15);
    border-radius: 12px;
    padding: 8px;
    border: 1px solid rgba(255, 255, 255, 30);
}
QTabWidget::pane {
    border: 0px;
}
QTabBar::tab {
    background: rgba(255, 255, 255, 15);
    border-radius: 12px;
    margin: 4px;
    padding: 10px 18px;
}
QTabBar::tab:selected {
    background: rgba(255, 255, 255, 35);
}
"""


class AsyncWorker(QtCore.QObject):
    finished = QtCore.Signal(object)

    def __init__(self, coroutine):
        super().__init__()
        self.coroutine = coroutine

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.coroutine)
        loop.close()
        self.finished.emit(result)


class UltimateMainWindow(QtWidgets.QMainWindow):
    def __init__(self, controller, config_loader: Callable[[], Dict[str, Any]], config_saver: Callable[[Dict[str, Any]], None]):
        super().__init__()
        self.controller = controller
        self.config_loader = config_loader
        self.config_saver = config_saver

        self.setWindowTitle("Ultimate Discord Bot Controller")
        self.setMinimumSize(1100, 720)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.container = QtWidgets.QWidget()
        self.setCentralWidget(self.container)
        self.container.setStyleSheet(GLASS_STYLE)

        layout = QtWidgets.QVBoxLayout(self.container)
        self.title_label = QtWidgets.QLabel("Ultimate Dashboard")
        self.title_label.setObjectName("titleLabel")
        layout.addWidget(self.title_label)

        self.tabs = QtWidgets.QTabWidget()
        layout.addWidget(self.tabs)

        self.dashboard_tab = QtWidgets.QWidget()
        self.logs_tab = QtWidgets.QWidget()
        self.config_tab = QtWidgets.QWidget()
        self.license_tab = QtWidgets.QWidget()

        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.logs_tab, "Logs")
        self.tabs.addTab(self.config_tab, "Configuration")
        self.tabs.addTab(self.license_tab, "Licences")

        self._setup_dashboard()
        self._setup_logs()
        self._setup_config()
        self._setup_license()

    def _setup_dashboard(self):
        layout = QtWidgets.QVBoxLayout(self.dashboard_tab)
        status_card = self._create_card("Statut du bot", "Opérationnel")
        layout.addWidget(status_card)
        buttons_layout = QtWidgets.QHBoxLayout()
        restart_button = QtWidgets.QPushButton("Redémarrer le bot")
        restart_button.clicked.connect(self.restart_bot)
        buttons_layout.addWidget(restart_button)
        layout.addLayout(buttons_layout)
        layout.addStretch(1)

    def _setup_logs(self):
        layout = QtWidgets.QVBoxLayout(self.logs_tab)
        self.logs_output = QtWidgets.QTextEdit()
        self.logs_output.setReadOnly(True)
        layout.addWidget(self.logs_output)

    def _setup_config(self):
        layout = QtWidgets.QVBoxLayout(self.config_tab)
        self.config_editor = QtWidgets.QTextEdit()
        self.config_editor.setPlaceholderText("Modifier la configuration YAML du bot")
        config_data = self.config_loader()
        if config_data:
            import yaml

            self.config_editor.setPlainText(yaml.safe_dump(config_data, sort_keys=False, allow_unicode=True))
        save_button = QtWidgets.QPushButton("Enregistrer")
        save_button.clicked.connect(self.save_config)
        layout.addWidget(self.config_editor)
        layout.addWidget(save_button)

    def _setup_license(self):
        layout = QtWidgets.QVBoxLayout(self.license_tab)
        self.license_key_input = QtWidgets.QLineEdit()
        self.license_key_input.setPlaceholderText("Clé de licence")
        validate_button = QtWidgets.QPushButton("Valider la clé")
        validate_button.clicked.connect(self.validate_license)
        self.license_results = QtWidgets.QTextEdit()
        self.license_results.setReadOnly(True)
        layout.addWidget(self.license_key_input)
        layout.addWidget(validate_button)
        layout.addWidget(self.license_results)

    def _create_card(self, title: str, value: str) -> QtWidgets.QWidget:
        widget = QtWidgets.QFrame()
        widget.setFrameShape(QtWidgets.QFrame.StyledPanel)
        layout = QtWidgets.QVBoxLayout(widget)
        layout.addWidget(QtWidgets.QLabel(title))
        value_label = QtWidgets.QLabel(value)
        value_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(value_label)
        return widget

    def restart_bot(self):
        self.logs_output.append("[ACTION] Demande de redémarrage envoyée.")

    def save_config(self):
        import yaml

        try:
            data = yaml.safe_load(self.config_editor.toPlainText())
            self.config_saver(data)
            self.logs_output.append("[CONFIG] Configuration enregistrée.")
        except yaml.YAMLError as exc:
            self.logs_output.append(f"Erreur YAML: {exc}")

    def validate_license(self):
        key = self.license_key_input.text()
        coroutine = self.controller.validate_license(key)
        self._run_async(coroutine, self.display_license_result)

    def display_license_result(self, result):
        self.license_results.setPlainText(str(result))

    def _run_async(self, coroutine, callback):
        thread = QtCore.QThread()
        worker = AsyncWorker(coroutine)
        worker.moveToThread(thread)
        worker.finished.connect(callback)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.started.connect(worker.run)
        thread.start()
