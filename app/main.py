import sys
from PySide6 import QtWidgets

from app.db.session import init_db
from app.gui.main_window import MainWindow


def main():
    init_db()
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
