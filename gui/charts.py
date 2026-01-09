from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from stats import GLOBAL_STATS

class LiveChart(QWidget):
    def __init__(self):
        super().__init__()

        self.figure = Figure(facecolor="#1C1C1C")  # фон всієї фігури чорний
        self.ax = self.figure.add_subplot(111, facecolor="#1C1C1C")  # фон осі чорний
        self.canvas = FigureCanvasQTAgg(self.figure)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.data = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chart)

        # Налаштування стилів осі
        self.ax.tick_params(colors="white")      # колір поділок
        self.ax.yaxis.label.set_color("white")   # підпис осі Y
        self.ax.xaxis.label.set_color("white")   # підпис осі X
        self.ax.title.set_color("white")  
        for spine in self.ax.spines.values():
            spine.set_edgecolor("white")       # заголовок

    def update_chart(self):
        value = GLOBAL_STATS.pull()
        self.data.append(value)

        if len(self.data) > 60:
            self.data.pop(0)

        self.ax.clear()
        self.ax.set_facecolor("#1C1C1C")
        self.ax.plot(self.data, color="red")    # червона лінія
        self.ax.set_title("Requests / sec", color="white")
        self.ax.tick_params(colors="white")

        for spine in self.ax.spines.values():
            spine.set_edgecolor("white")
        self.canvas.draw()

    def start(self):
        self.data.clear()
        self.ax.clear()
        self.ax.set_facecolor("white")
        self.timer.start(1000)

    def stop(self):
        self.timer.stop()
