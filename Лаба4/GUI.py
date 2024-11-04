import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout,
    QWidget, QPushButton, QLineEdit, QMessageBox, QFormLayout, QDialog, QHBoxLayout, QHeaderView
)
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtCore import Qt

class AddRecordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Record")
        self.setGeometry(200, 200, 300, 150)
        self.setStyleSheet("background-color: #f5f5f5;")

        layout = QFormLayout()

        self.user_id_input = QLineEdit()
        layout.addRow("User ID:", self.user_id_input)

        self.title_input = QLineEdit()
        layout.addRow("Title:", self.title_input)

        self.body_input = QLineEdit()
        layout.addRow("Body:", self.body_input)

        self.save_button = QPushButton("Сохранить")
        self.save_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.save_button.clicked.connect(self.accept)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def get_data(self):
        return (
            self.user_id_input.text(),
            self.title_input.text(),
            self.body_input.text()
        )

    def set_data(self, user_id, title, body):
        self.user_id_input.setText(user_id)
        self.title_input.setText(title)
        self.body_input.setText(body)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Posts Database")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #e9ecef;")

        self.initUI()
        self.createConnection()
        self.loadData()

    def initUI(self):
        layout = QVBoxLayout()

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Поиск по названию")
        self.search_field.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")
        layout.addWidget(self.search_field)

        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Добавить")
        self.add_button.setStyleSheet("background-color: #007BFF; color: white; border-radius: 5px;")
        self.add_button.clicked.connect(self.addRecord)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Редактировать")
        self.edit_button.setStyleSheet("background-color: #28A745; color: white; border-radius: 5px;")
        self.edit_button.clicked.connect(self.editRecord)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.setStyleSheet("background-color: #DC3545; color: white; border-radius: 5px;")
        self.delete_button.clicked.connect(self.deleteRecord)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        self.table_view = QTableView()
        self.table_view.setStyleSheet("background-color: white; border-radius: 5px;")
        layout.addWidget(self.table_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def createConnection(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("posts.db")
        if not self.db.open():
            print("Невозможно открыть БД")
            sys.exit(1)

    def loadData(self):
        self.model = QSqlTableModel(self)
        self.model.setTable("posts")
        self.model.select()
        self.model.setHeaderData(0, Qt.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Horizontal, "User ID")
        self.model.setHeaderData(2, Qt.Horizontal, "Title")
        self.model.setHeaderData(3, Qt.Horizontal, "Body")
        self.table_view.setModel(self.model)

        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def filterData(self):
        filter_text = self.search_field.text()
        self.model.setFilter(f"title LIKE '%{filter_text}%'")
        self.model.select()

    def addRecord(self):
        dialog = AddRecordDialog()
        if dialog.exec_() == QDialog.Accepted:
            user_id, title, body = dialog.get_data()
            if user_id and title and body:
                query = QSqlQuery()
                query.prepare("INSERT INTO posts (user_id, title, body) VALUES (?, ?, ?)")
                query.addBindValue(user_id)
                query.addBindValue(title)
                query.addBindValue(body)
                if query.exec_():
                    self.loadData()
                else:
                    QMessageBox.warning(self, "Error", "Не удалось добавить новую запись")

    def editRecord(self):
        selected_row = self.table_view.currentIndex().row()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Выберите строку для редактирования")
            return

        user_id = str(self.model.index(selected_row, 1).data())
        title = self.model.index(selected_row, 2).data()
        body = self.model.index(selected_row, 3).data()

        dialog = AddRecordDialog()
        dialog.set_data(user_id, title, body)
        
        if dialog.exec_() == QDialog.Accepted:
            user_id, title, body = dialog.get_data()
            id_to_update = self.model.index(selected_row, 0).data()
            query = QSqlQuery()
            query.prepare("UPDATE posts SET user_id = ?, title = ?, body = ? WHERE id = ?")
            query.addBindValue(user_id)
            query.addBindValue(title)
            query.addBindValue(body)
            query.addBindValue(id_to_update)
            if query.exec_():
                self.loadData()
            else:
                QMessageBox.warning(self, "Error", "Не удалось обновить")

    def deleteRecord(self):
        selected_row = self.table_view.currentIndex().row()
        if selected_row < 0: 
            QMessageBox.warning(self, "Error", "Выберите строку для удаления")
            return

        reply = QMessageBox.question(self, 'Confirm Delete',
                                     "Вы уверены, что хотите удалить эту запись?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            id_to_delete = self.model.index(selected_row, 0).data()
            query = QSqlQuery()
            query.prepare("DELETE FROM posts WHERE id = ?")
            query.addBindValue(id_to_delete)
            if query.exec_():
                self.loadData()
            else:
                QMessageBox.warning(self, "Error", "Не удалось удалить")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
