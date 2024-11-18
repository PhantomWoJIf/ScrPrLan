import sys
import asyncio
import aiohttp
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QProgressBar, QLabel, QTableWidget,
    QTableWidgetItem, QHBoxLayout
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QHeaderView

class DataLoader(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    async def fetch_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://jsonplaceholder.typicode.com/posts") as response:
                return await response.json()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        data = loop.run_until_complete(self.fetch_data())
        for i in range(1, 11):
            self.progress.emit(i * 10)
            self.msleep(200)
        self.finished.emit(data)

class DataSaver(QThread):
    finished = pyqtSignal()

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.db_path = 'posts.db'

    def run(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title TEXT,
                body TEXT
            )
        ''')
        cursor.executemany('''
            INSERT OR REPLACE INTO posts (id, user_id, title, body) VALUES (?, ?, ?, ?)
        ''', [(post['id'], post['userId'], post['title'], post['body']) for post in self.data])
        conn.commit()
        conn.close()
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("asyn")
        self.setGeometry(100, 100, 800, 600)

        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Статус: Ожидание действий...")
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["ID", "User ID", "Title", "Body"])

        self.load_button = QPushButton("Загрузить данные")
        self.load_button.clicked.connect(self.load_data)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.progress_bar)

        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.table_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.progress_bar.setFixedHeight(self.load_button.sizeHint().height())

        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # User ID
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Title
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Body (растягивается)

        self.is_loading = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_for_updates)
        self.timer.start(30000)

    def load_data(self):
        if self.is_loading:
            return

        self.is_loading = True
        self.progress_bar.setValue(0)
        self.status_label.setText("Статус: Загрузка...")

        self.data_loader = DataLoader()
        self.data_loader.progress.connect(self.update_progress)
        self.data_loader.finished.connect(self.save_data)
        self.data_loader.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def save_data(self, data):
        self.progress_bar.setValue(50)
        self.status_label.setText("Статус: Сохранение...")

        self.data_saver = DataSaver(data)
        self.data_saver.finished.connect(self.finish_loading)
        self.data_saver.start()

    def finish_loading(self):
        self.progress_bar.setValue(100)
        self.status_label.setText("Статус: Данные успешно сохранены")
        self.is_loading = False
        self.display_data()

    def display_data(self):
        conn = sqlite3.connect('posts.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, title, body FROM posts")
        rows = cursor.fetchall()
        conn.close()

        self.table_widget.setRowCount(len(rows))
        for row_index, row_data in enumerate(rows):
            for col_index, col_data in enumerate(row_data):
                self.table_widget.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))

    def check_for_updates(self):
        if not self.is_loading:
            self.load_data()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
