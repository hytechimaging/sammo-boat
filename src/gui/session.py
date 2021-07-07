from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QMessageBox


class SammoActionSession:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        self.action = QAction("Sammo", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        QMessageBox.information(None, "Minimal plugin",
                                "Do something Fred here")
