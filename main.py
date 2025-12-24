import sys
import os

os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=1"

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Boombox")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
