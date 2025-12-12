# main_window_v1.py
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from lab2 import ImageIterator

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.iterator = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Просмотр изображений")
        self.setGeometry(100, 100, 800, 600)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_open = QPushButton("Открыть CSV")
        self.btn_open.clicked.connect(self.open_csv)
        btn_layout.addWidget(self.btn_open)
        
        self.btn_next = QPushButton("Следующее →")
        self.btn_next.clicked.connect(self.show_next)
        self.btn_next.setEnabled(False)
        btn_layout.addWidget(self.btn_next)
        
        layout.addLayout(btn_layout)
        
        # Изображение
        self.image_label = QLabel("Выберите файл аннотации")
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        
    def open_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите CSV", "", "CSV (*.csv)"
        )
        
        if file_path:
            try:
                self.iterator = ImageIterator(file_path)
                self.btn_next.setEnabled(True)
                self.show_next()
            except:
                QMessageBox.critical(self, "Ошибка", "Неверный CSV файл")
    
    def show_next(self):
        if self.iterator:
            try:
                info = next(self.iterator)
                img_path = info['absolute_path']
                
                if os.path.exists(img_path):
                    pixmap = QPixmap(img_path)
                    if not pixmap.isNull():
                        # Масштабирование с пропорциями
                        scaled = pixmap.scaled(750, 550, Qt.KeepAspectRatio)
                        self.image_label.setPixmap(scaled)
                        self.setWindowTitle(f"Изображение: {os.path.basename(img_path)}")
                    else:
                        self.image_label.setText("Ошибка загрузки")
                else:
                    self.image_label.setText("Файл не найден")
                    
            except StopIteration:
                self.image_label.setText("Конец датасета")
                self.btn_next.setEnabled(False)

def main():
    app = QApplication(sys.argv)
    window = ImageViewer()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()