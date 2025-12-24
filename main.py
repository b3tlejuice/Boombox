import sys
import os
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MediaFlow")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
