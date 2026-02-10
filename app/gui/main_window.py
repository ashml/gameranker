from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
from sqlalchemy import select, func

from app.core.importer import DocxImporter
from app.core.pair_selector import PairSelector
from app.core.rating import RatingEngine
from app.db.models import Comparison, Game
from app.db.session import SessionLocal
from app.gui.comparison_view import ComparisonView
from app.services.exporter import Exporter


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Ranker")
        self.session = SessionLocal()
        self.rating_engine = RatingEngine()
        self.pair_selector = PairSelector()
        self.importer = DocxImporter()
        self.exporter = Exporter(self.rating_engine)

        self.view = ComparisonView()
        self.setCentralWidget(self.view)
        self.view.compare_signal.connect(self.handle_comparison)

        self._create_menu()
        self._setup_shortcuts()
        self._load_next_pair()
        self._update_status()

    def closeEvent(self, event):
        self.session.close()
        super().closeEvent(event)

    def _create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("Файл")

        import_action = QtGui.QAction("📂 Импорт .docx", self)
        import_action.triggered.connect(self.import_docx)
        file_menu.addAction(import_action)

        export_txt_action = QtGui.QAction("📤 Экспорт .txt", self)
        export_txt_action.triggered.connect(lambda: self.export_results("txt"))
        file_menu.addAction(export_txt_action)

        export_docx_action = QtGui.QAction("📤 Экспорт .docx", self)
        export_docx_action.triggered.connect(lambda: self.export_results("docx"))
        file_menu.addAction(export_docx_action)

        list_action = QtGui.QAction("📊 Список игр", self)
        list_action.triggered.connect(self.show_games_list)
        file_menu.addAction(list_action)

        reset_action = QtGui.QAction("🔄 Сброс рейтингов", self)
        reset_action.triggered.connect(self.reset_ratings)
        file_menu.addAction(reset_action)

    def _setup_shortcuts(self):
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Left), self, activated=lambda: self.handle_comparison(-1))
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Up), self, activated=lambda: self.handle_comparison(0))
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Right), self, activated=lambda: self.handle_comparison(1))

    def _load_next_pair(self):
        pair = self.pair_selector.select_pair(self.session)
        if not pair:
            self.view.left_label.setText("Добавьте игры через импорт .docx")
            self.view.right_label.setText("")
            self.view.left_rating.setText("")
            self.view.right_rating.setText("")
            self.view.left_image.setPixmap(QtGui.QPixmap())
            self.view.right_image.setPixmap(QtGui.QPixmap())
            return
        self.left_game, self.right_game = pair
        left_rating = self.rating_engine.env.Rating(self.left_game.rating, self.left_game.uncertainty)
        right_rating = self.rating_engine.env.Rating(self.right_game.rating, self.right_game.uncertainty)
        left_score = self.rating_engine.to_display_score(left_rating)
        right_score = self.rating_engine.to_display_score(right_rating)
        self.view.set_game_data(self.left_game, self.right_game, left_score, right_score)

    def handle_comparison(self, result: int):
        if not hasattr(self, "left_game"):
            return
        left_rating = self.rating_engine.env.Rating(self.left_game.rating, self.left_game.uncertainty)
        right_rating = self.rating_engine.env.Rating(self.right_game.rating, self.right_game.uncertainty)
        new_left, new_right = self.rating_engine.update(left_rating, right_rating, result)
        self.left_game.rating = new_left.mu
        self.left_game.uncertainty = new_left.sigma
        self.right_game.rating = new_right.mu
        self.right_game.uncertainty = new_right.sigma
        comparison = Comparison(game_left_id=self.left_game.id, game_right_id=self.right_game.id, result=result)
        self.session.add(comparison)
        self.session.commit()
        self._load_next_pair()
        self._update_status()

    def import_docx(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Импорт .docx", "", "Docx Files (*.docx)")
        if not file_path:
            return
        added = self.importer.import_file(self.session, Path(file_path))
        QtWidgets.QMessageBox.information(self, "Импорт", f"Добавлено игр: {added}")
        self._load_next_pair()
        self._update_status()

    def export_results(self, fmt: str):
        filters = "Text Files (*.txt)" if fmt == "txt" else "Docx Files (*.docx)"
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Экспорт", "", filters)
        if not file_path:
            return
        sort_by, ok = QtWidgets.QInputDialog.getItem(self, "Сортировка", "Сортировать по:", ["rating", "alpha"], 0, False)
        if not ok:
            return
        if fmt == "txt":
            self.exporter.export_txt(self.session, Path(file_path), sort_by=sort_by)
        else:
            self.exporter.export_docx(self.session, Path(file_path), sort_by=sort_by)
        QtWidgets.QMessageBox.information(self, "Экспорт", "Экспорт завершён")

    def show_games_list(self):
        games = self.session.execute(select(Game)).scalars().all()
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Список игр")
        layout = QtWidgets.QVBoxLayout(dialog)
        table = QtWidgets.QTableWidget(len(games), 3)
        table.setHorizontalHeaderLabels(["Название", "Рейтинг", "Неопределённость"])
        for row, game in enumerate(sorted(games, key=lambda g: g.name.lower())):
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(game.name))
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{game.rating:.2f}"))
            table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{game.uncertainty:.2f}"))
        table.resizeColumnsToContents()
        layout.addWidget(table)
        close_button = QtWidgets.QPushButton("Закрыть")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec()

    def reset_ratings(self):
        confirm = QtWidgets.QMessageBox.question(self, "Сброс", "Сбросить все рейтинги?")
        if confirm != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        games = self.session.execute(select(Game)).scalars().all()
        for game in games:
            game.rating = self.rating_engine.config.mu
            game.uncertainty = self.rating_engine.config.sigma
        self.session.execute(Comparison.__table__.delete())
        self.session.commit()
        self._load_next_pair()
        self._update_status()

    def _update_status(self):
        total_games = self.session.execute(select(func.count(Game.id))).scalar() or 0
        total_comparisons = self.session.execute(select(func.count(Comparison.id))).scalar() or 0
        self.statusBar().showMessage(f"Игр: {total_games} | Сравнений: {total_comparisons}")
