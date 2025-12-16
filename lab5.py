# main_window.py

import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *

from lab2 import ImageIterator


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.iterator = None
        self.current_index = 0
        self.total_images = 0
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Просмотр датасета - Lab 5")
        self.setGeometry(100, 100, 900, 650)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Панель управления
        control_panel = QHBoxLayout()

        self.btn_open = QPushButton("📂 Открыть аннотацию")
        self.btn_open.clicked.connect(self.load_annotation)
        control_panel.addWidget(self.btn_open)

        self.btn_prev = QPushButton("◀ Назад")
        self.btn_prev.clicked.connect(self.prev_image)
        self.btn_prev.setEnabled(False)
        control_panel.addWidget(self.btn_prev)

        self.btn_next = QPushButton("Вперед ▶")
        self.btn_next.clicked.connect(self.next_image)
        self.btn_next.setEnabled(False)
        control_panel.addWidget(self.btn_next)

        main_layout.addLayout(control_panel)

        # Статус
        self.status_label = QLabel("Готов к работе")
        main_layout.addWidget(self.status_label)

        # Область изображения
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(800, 500)
        self.image_label.setStyleSheet("border: 2px solid gray; background: #f0f0f0")
        main_layout.addWidget(self.image_label)

        # Инфо
        self.info_label = QLabel()
        main_layout.addWidget(self.info_label)

    def load_annotation(self):
        """Загрузка файла аннотации"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл аннотации",
            os.getcwd(),
            "CSV файлы (*.csv);;Все файлы (*.*)"
        )

        if file_path:
            try:
                self.iterator = ImageIterator(file_path)
                self.total_images = len(self.iterator.data)
                self.current_index = 0

                self.btn_prev.setEnabled(True)
                self.btn_next.setEnabled(True)
                self.status_label.setText(f"Загружено изображений: {self.total_images}")

                self.show_current_image()

            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки:\n{str(e)}")

    def show_current_image(self):
        """Показать текущее изображение"""
        if self.iterator and self.iterator.data:
            try:
                # Получаем текущее изображение
                if 0 <= self.current_index < len(self.iterator.data):
                    row = self.iterator.data[self.current_index]
                    img_path = row[0]  # absolute_path

                    self.info_label.setText(
                        f"Изображение {self.current_index + 1}/{self.total_images}: "
                        f"{os.path.basename(img_path)}"
                    )

                    if os.path.exists(img_path):
                        pixmap = QPixmap(img_path)

                        if not pixmap.isNull():
                            # Масштабирование с сохранением пропорций
                            scaled = pixmap.scaled(
                                self.image_label.width() - 20,
                                self.image_label.height() - 20,
                                Qt.KeepAspectRatio,
                                Qt.SmoothTransformation
                            )
                            self.image_label.setPixmap(scaled)
                        else:
                            self.image_label.setText("Не удалось загрузить изображение")
                    else:
                        self.image_label.setText(f"Файл не найден:\n{img_path}")

            except Exception as e:
                self.image_label.setText(f"Ошибка: {str(e)}")

    def next_image(self):
        """Следующее изображение"""
        if self.iterator and self.current_index < self.total_images - 1:
            self.current_index += 1
            self.iterator.index = self.current_index
            self.show_current_image()

    def prev_image(self):
        """Предыдущее изображение"""
        if self.iterator and self.current_index > 0:
            self.current_index -= 1
            self.iterator.index = self.current_index
            self.show_current_image()


def main():
    app = QApplication(sys.argv)
    window = ImageViewer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()