from PySide6 import QtCore, QtGui, QtWidgets


class ComparisonView(QtWidgets.QWidget):
    compare_signal = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.left_label = QtWidgets.QLabel()
        self.left_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.right_label = QtWidgets.QLabel()
        self.right_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.left_rating = QtWidgets.QLabel()
        self.left_rating.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.right_rating = QtWidgets.QLabel()
        self.right_rating.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.left_image = QtWidgets.QLabel()
        self.left_image.setFixedSize(300, 400)
        self.left_image.setScaledContents(True)
        self.right_image = QtWidgets.QLabel()
        self.right_image.setFixedSize(300, 400)
        self.right_image.setScaledContents(True)

        self.left_button = QtWidgets.QPushButton("⬅ Левая лучше")
        self.draw_button = QtWidgets.QPushButton("⚖ Равны")
        self.right_button = QtWidgets.QPushButton("Правая лучше ➡")

        self.left_button.clicked.connect(lambda: self.compare_signal.emit(-1))
        self.draw_button.clicked.connect(lambda: self.compare_signal.emit(0))
        self.right_button.clicked.connect(lambda: self.compare_signal.emit(1))

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.left_label, 0, 0)
        layout.addWidget(self.right_label, 0, 2)
        layout.addWidget(self.left_rating, 1, 0)
        layout.addWidget(self.right_rating, 1, 2)
        layout.addWidget(self.left_image, 2, 0)
        layout.addWidget(self.right_image, 2, 2)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.left_button)
        button_layout.addWidget(self.draw_button)
        button_layout.addWidget(self.right_button)
        layout.addLayout(button_layout, 3, 0, 1, 3)

        layout.setColumnStretch(1, 1)

    def set_game_data(self, left_game, right_game, left_score: float, right_score: float):
        self.left_label.setText(left_game.name)
        self.right_label.setText(right_game.name)
        self.left_rating.setText(f"Рейтинг: {left_score:.1f}")
        self.right_rating.setText(f"Рейтинг: {right_score:.1f}")
        self._set_image(self.left_image, left_game.image_path)
        self._set_image(self.right_image, right_game.image_path)

    def _set_image(self, label: QtWidgets.QLabel, path: str | None):
        if not path:
            label.setPixmap(QtGui.QPixmap())
            return
        pixmap = QtGui.QPixmap(path)
        if pixmap.isNull():
            label.setPixmap(QtGui.QPixmap())
            return
        label.setPixmap(pixmap)
