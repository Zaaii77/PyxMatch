import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QRect, QTimer
from screeninfo import get_monitors

class ScreenNumberWindow(QMainWindow):
    def __init__(self, screen_number, screen_geometry):
        super().__init__()
        self.setWindowTitle(f"Écran {screen_number}")

        # Créer un QLabel pour afficher le numéro de l'écran
        label = QLabel(f"Écran {screen_number}")
        label.setAlignment(Qt.AlignCenter)

        # Utiliser un layout pour positionner le QLabel
        layout = QVBoxLayout()
        layout.addWidget(label)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        # Utiliser le QWidget comme widget central de la fenêtre
        self.setCentralWidget(central_widget)

        # Définir la taille de la fenêtre
        window_width = 200
        window_height = 100

        # Calculer la position pour centrer la fenêtre sur l'écran
        x = screen_geometry.x() + (screen_geometry.width() - window_width) // 2
        y = screen_geometry.y() + (screen_geometry.height() - window_height) // 2

        # Positionner et dimensionner la fenêtre
        self.setGeometry(x, y, window_width, window_height)

        # Créer un timer pour fermer la fenêtre après 3 secondes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_window)
        self.timer.start(3000)  # 3000 ms = 3 secondes

    def close_window(self):
        self.timer.stop()
        self.close()

def main():
    app = QApplication(sys.argv)

    monitors = get_monitors()
    windows = []
    for i, monitor in enumerate(monitors):
        screen_geometry = QRect(monitor.x, monitor.y, monitor.width, monitor.height)
        window = ScreenNumberWindow(i + 1, screen_geometry)
        windows.append(window)  # Gardez une référence pour éviter que les fenêtres ne soient pas fermées prématurément
        window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
