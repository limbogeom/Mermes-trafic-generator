import asyncio
import random


from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QLabel, QSlider, QDialog,
    QFormLayout, QSpinBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer

from core.tcp_client import tcp_client
from core.udp_client import udp_client
from core.http_client import http_client
from core.tls_client import tls_client
from core.websocket_client import websocket_client
from gui.charts import LiveChart
from profiles.profiles import PROFILES, DYNAMIC_PROFILES, load_user_profiles, save_user_profiles



# ==================== Діалог для створення/редагування профілю ====================
class ProfileDialog(QDialog):
    def __init__(self, type_="static", data=None):
        super().__init__()
        self.setWindowTitle(f"{'Edit' if data else 'Add'} {type_.capitalize()} Profile")
        self.type_ = type_
        layout = QFormLayout()

        self.name_input = QLineEdit(data.get("name") if data else "")
        self.protocol_input = QLineEdit(data.get("protocol") if data else "")
        self.target_input = QLineEdit(data.get("target") if data else "")
        self.port_input = QLineEdit(str(data.get("port", 0)) if data else "0")

        layout.addRow("Name:", self.name_input)
        layout.addRow("Protocol:", self.protocol_input)
        layout.addRow("Target:", self.target_input)
        layout.addRow("Port:", self.port_input)

        if type_ == "static":
            self.rate_input = QLineEdit(str(data.get("rate", "")) if data else "")
            self.clients_input = QLineEdit(str(data.get("clients", "")) if data else "")
            layout.addRow("Rate:", self.rate_input)
            layout.addRow("Clients:", self.clients_input)
        else:
            self.rate_min = QSpinBox(); self.rate_min.setRange(1, 10000)
            self.rate_max = QSpinBox(); self.rate_max.setRange(1, 10000)
            self.clients_min = QSpinBox(); self.clients_min.setRange(1, 1000)
            self.clients_max = QSpinBox(); self.clients_max.setRange(1, 1000)
            self.interval = QSpinBox(); self.interval.setRange(1, 60)

            if data:
                self.rate_min.setValue(data["rate_coef"][0])
                self.rate_max.setValue(data["rate_coef"][1])
                self.clients_min.setValue(data["clients_coef"][0])
                self.clients_max.setValue(data["clients_coef"][1])
                self.interval.setValue(data.get("update_interval", 5))

            layout.addRow("Rate Min:", self.rate_min)
            layout.addRow("Rate Max:", self.rate_max)
            layout.addRow("Clients Min:", self.clients_min)
            layout.addRow("Clients Max:", self.clients_max)
            layout.addRow("Update Interval (s):", self.interval)

        self.btn = QPushButton("OK")
        self.btn.clicked.connect(self.accept)
        layout.addRow(self.btn)
        self.setLayout(layout)

    def get_data(self):
        if self.type_ == "static":
            return {
                "name": self.name_input.text(),
                "protocol": self.protocol_input.text(),
                "target": self.target_input.text(),
                "port": int(self.port_input.text()),
                "rate": int(self.rate_input.text()),
                "clients": int(self.clients_input.text())
            }
        else:
            return {
                "name": self.name_input.text(),
                "protocol": self.protocol_input.text(),
                "target": self.target_input.text(),
                "port": int(self.port_input.text()),
                "rate_coef": (self.rate_min.value(), self.rate_max.value()),
                "clients_coef": (self.clients_min.value(), self.clients_max.value()),
                "update_interval": self.interval.value()
            }


# ==================== Діалог для керування профілями ====================
class ProfilesManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Profiles")
        self.setMinimumSize(400, 100)

        self.static_profiles, self.dynamic_profiles = load_user_profiles()

        layout = QVBoxLayout()
        self.profile_combo = QComboBox()
        layout.addWidget(QLabel("Select Profile:"))
        layout.addWidget(self.profile_combo)

        btn_layout = QHBoxLayout()
        self.add_static_btn = QPushButton("Add Static")
        self.add_dynamic_btn = QPushButton("Add Dynamic")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        btn_layout.addWidget(self.add_static_btn)
        btn_layout.addWidget(self.add_dynamic_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.refresh_profiles()

        self.add_static_btn.clicked.connect(lambda: self.add_profile("static"))
        self.add_dynamic_btn.clicked.connect(lambda: self.add_profile("dynamic"))
        self.edit_btn.clicked.connect(self.edit_profile)
        self.delete_btn.clicked.connect(self.delete_profile)

    def refresh_profiles(self):
        self.profile_combo.clear()
        self.profile_combo.addItems(list(self.static_profiles.keys()) + list(self.dynamic_profiles.keys()))

    def save_profiles(self):
        save_user_profiles(self.static_profiles, self.dynamic_profiles)

    def add_profile(self, type_):
        dlg = ProfileDialog(type_)
        if dlg.exec():
            data = dlg.get_data()
            if type_ == "static":
                self.static_profiles[data["name"]] = data
            else:
                self.dynamic_profiles[data["name"]] = data
            self.save_profiles()
            self.refresh_profiles()

    def edit_profile(self):
        name = self.profile_combo.currentText()
        if name in self.static_profiles:
            dlg = ProfileDialog("static", self.static_profiles[name])
            if dlg.exec():
                data = dlg.get_data()
                if data["name"] != name:
                    self.static_profiles.pop(name)
                self.static_profiles[data["name"]] = data
                self.save_profiles()
                self.refresh_profiles()
        elif name in self.dynamic_profiles:
            dlg = ProfileDialog("dynamic", self.dynamic_profiles[name])
            if dlg.exec():
                data = dlg.get_data()
                if data["name"] != name:
                    self.dynamic_profiles.pop(name)
                self.dynamic_profiles[data["name"]] = data
                self.save_profiles()
                self.refresh_profiles()

    def delete_profile(self):
        name = self.profile_combo.currentText()
        if name in self.static_profiles:
            self.static_profiles.pop(name)
        elif name in self.dynamic_profiles:
            self.dynamic_profiles.pop(name)
        self.save_profiles()
        self.refresh_profiles()


# ==================== ASYNC WORKER ====================
class TrafficWorker(QThread):
    log = Signal(str)
    def __init__(self):
        super().__init__()
        self.loop = None
        self.task = None

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start_traffic(self, coros):
        async def runner():
            await asyncio.gather(*coros, return_exceptions=True)
        self.task = asyncio.run_coroutine_threadsafe(runner(), self.loop)

    def stop_traffic(self):
        if self.task:
            self.task.cancel()
            self.task = None
            self.log.emit("Traffic stopped")


# ==================== MAIN WINDOW ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mermes")
        self.setMinimumSize(480, 400)

        self.worker = TrafficWorker()
        self.worker.start()

        self.dynamic_timer = QTimer()
        self.dynamic_timer.timeout.connect(self.update_dynamic_profile)
        self.current_dynamic_interval = None

        self.user_static_profiles, self.user_dynamic_profiles = load_user_profiles()
        self.current_profile_name = None
        self.active_dynamic = False  # чи динамічний профіль активний

        self.init_ui()

    def init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        # ---- Profile Combobox ----
        self.profile = QComboBox()
        self.refresh_profiles()
        self.profile.currentTextChanged.connect(self.apply_profile)
        layout.addWidget(QLabel("Profile"))
        layout.addWidget(self.profile)

        profile_manager_btn = QPushButton("Manage Profiles")
        profile_manager_btn.clicked.connect(self.open_profile_manager)
        layout.addWidget(profile_manager_btn)

        # ---- Protocol / Target / Port / Rate / Clients ----
        self.protocol = QComboBox()
        self.protocol.addItems(["TCP", "UDP", "HTTP", "TLS", "WebSocket"])
        self.target = QLineEdit("127.0.0.1")
        self.port = QLineEdit("9000")
        self.rate = QLineEdit("5")
        self.clients_label = QLabel("Clients: 1")
        self.clients = QSlider(Qt.Horizontal)
        self.clients.setRange(1, 500)
        self.clients.setValue(1)
        self.clients.valueChanged.connect(lambda v: self.clients_label.setText(f"Clients: {v}"))

        layout.addWidget(QLabel("Protocol"))
        layout.addWidget(self.protocol)
        layout.addWidget(QLabel("Target / URL"))
        layout.addWidget(self.target)
        layout.addWidget(QLabel("Port (ignore for HTTP/WS)"))
        layout.addWidget(self.port)
        layout.addWidget(QLabel("Rate per client (req/sec)"))
        layout.addWidget(self.rate)
        layout.addWidget(self.clients_label)
        layout.addWidget(self.clients)

        # ---- Traffic Chart ----
        self.chart = LiveChart()
        layout.addWidget(QLabel("Traffic (req/sec)"))
        layout.addWidget(self.chart)

        # ---- Traffic Buttons ----
        traffic_btns = QHBoxLayout()
        start_btn = QPushButton("START")
        stop_btn = QPushButton("STOP")
        start_btn.clicked.connect(self.start)
        stop_btn.clicked.connect(self.stop)
        traffic_btns.addWidget(start_btn)
        traffic_btns.addWidget(stop_btn)
        layout.addLayout(traffic_btns)

        central.setLayout(layout)
        self.setCentralWidget(central)

        # Fusion чорна тема
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel, QLineEdit, QComboBox, QPushButton { color: white; }
        """)

    def refresh_profiles(self):
        self.profile.clear()
        self.profile.addItem("Custom")
        all_profiles = list(PROFILES.keys()) + list(DYNAMIC_PROFILES.keys()) \
                       + list(self.user_static_profiles.keys()) + list(self.user_dynamic_profiles.keys())
        self.profile.addItems(all_profiles)

    def open_profile_manager(self):
        dlg = ProfilesManagerDialog(self)
        dlg.exec()
        self.user_static_profiles, self.user_dynamic_profiles = load_user_profiles()
        self.refresh_profiles()

    def apply_profile(self, name):
        """Оновлює GUI, не запускає динамічний таймер"""
        self.current_profile_name = name
        self.active_dynamic = False  # поки не натиснуто START

        if name == "Custom":
            self.rate.setReadOnly(False)
            self.clients.setEnabled(True)
            return

        # Статичний профіль
        if name in self.user_static_profiles or name in PROFILES:
            prof = self.user_static_profiles.get(name, PROFILES.get(name))
            self.rate.setReadOnly(False)
            self.clients.setEnabled(True)

        # Динамічний профіль
        elif name in self.user_dynamic_profiles or name in DYNAMIC_PROFILES:
            base = self.user_dynamic_profiles.get(name, DYNAMIC_PROFILES.get(name))
            prof = self.generate_dynamic(base)
            self.rate.setReadOnly(True)
            self.clients.setEnabled(False)

        else:
            return

        self.protocol.setCurrentText(prof["protocol"])
        self.target.setText(prof["target"])
        self.port.setText(str(prof.get("port", "")))
        self.update_gui_from_profile(prof)

    def generate_dynamic(self, base):
        return {
            "protocol": base["protocol"],
            "target": base["target"],
            "port": base["port"],
            "rate": random.randint(*base["rate_coef"]),
            "clients": random.randint(*base["clients_coef"])
        }

    def update_dynamic_profile(self):
        if not self.active_dynamic:
            return

        name = self.current_profile_name
        base = self.user_dynamic_profiles.get(name, DYNAMIC_PROFILES.get(name))
        if not base:
            return

        prof = self.generate_dynamic(base)
        self.update_gui_from_profile(prof)

    def update_gui_from_profile(self, prof):
        self.rate.setText(str(prof.get("rate", 5)))
        self.clients.setValue(prof.get("clients", 1))

    def start(self):
        proto = self.protocol.currentText()
        target = self.target.text()
        try:
            rate = float(self.rate.text())
        except ValueError:
            rate = 1
        clients = self.clients.value()
        port = int(self.port.text()) if self.port.text().isdigit() else 0

        coros = []
        for _ in range(clients):
            if proto == "TCP":
                coros.append(tcp_client(target, port, b"PING\n", rate, 999999))
            elif proto == "UDP":
                coros.append(udp_client(target, port, b"HELLO", rate, 999999))
            elif proto == "HTTP":
                coros.append(http_client(target, rate, 999999))
            elif proto == "TLS":
                coros.append(tls_client(target, port, b"PING\n", rate, 999999))
            elif proto == "WebSocket":
                coros.append(websocket_client(target, "HELLO", rate, 999999))

        self.chart.start()
        self.worker.start_traffic(coros)

        # Запуск динамічного профілю тільки після START
        name = self.current_profile_name
        if name in self.user_dynamic_profiles or name in DYNAMIC_PROFILES:
            base = self.user_dynamic_profiles.get(name, DYNAMIC_PROFILES.get(name))
            self.dynamic_timer.start(base.get("update_interval", 5) * 1000)
            self.current_dynamic_interval = base.get("update_interval", 5) * 1000
            self.active_dynamic = True

    def stop(self):
        self.worker.stop_traffic()
        self.chart.stop()
        self.dynamic_timer.stop()
        self.active_dynamic = False

    def closeEvent(self, event):
        self.stop()
        if self.worker.loop and self.worker.loop.is_running():
            self.worker.loop.call_soon_threadsafe(self.worker.loop.stop)
            self.worker.quit()
            self.worker.wait()
        event.accept()
