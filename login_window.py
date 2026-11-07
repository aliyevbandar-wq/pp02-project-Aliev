import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

try:
    from main import MainWindow
except ImportError:
    MainWindow = None

class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        
        self.setWindowTitle("Авторизация")
        self.resize(320, 200)
        self.setWindowIcon(QIcon("resources/icon.ico"))
        
        self.setStyleSheet("""
            QWidget {
                background-color: #2C3E50;
                font-family: 'Segoe UI', 'Calibri';
                color: #FFFFFF;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(30, 25, 30, 30)
        
        self.label = QLabel("Логин:")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ECF0F1; background: transparent;")
        layout.addWidget(self.label)
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите ваш логин...")
        self.login_input.setStyleSheet("""
            QLineEdit {
                padding: 10px; 
                font-size: 14px;
                border: 2px solid #BDC3C7;
                border-radius: 6px;
                background-color: #FFFFFF;
                color: #2C3E50;
            }
            QLineEdit:focus {
                border: 2px solid #27AE60;
            }
        """)
        layout.addWidget(self.login_input)
        
        self.btn_login = QPushButton("Войти")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #219653;
            }
            QPushButton:pressed {
                background-color: #1E8449;
            }
        """)
        self.btn_login.clicked.connect(self.check_login)
        layout.addWidget(self.btn_login)
        
        self.setLayout(layout)
        
    def check_login(self):
        login = self.login_input.text().strip()
        if not login:
            QMessageBox.warning(self, "Внимание", "Поле ввода логина не может быть пустым!")
            return
            
        result = None
        conn = self.db.get_connection() if self.db else None
        
        if conn is not None:
            try:
                cursor = conn.cursor()
                # ШАГ 3: Изменили SQL-запрос, добавив раздельные поля last_name, first_name, middle_name вместо fio
                query = "SELECT id_пользователя, id_роли, last_name, first_name, middle_name FROM users WHERE login = %s;"
                cursor.execute(query, (login,))
                result = cursor.fetchone()
                cursor.close()
            except Exception as e:
                print(f"[ЛОГ] Ошибка выполнения запроса ({e}).")
                result = None
            finally:
                self.db.release_connection(conn)
        
        # Заглушки также адаптированы под новую структуру (id, role_id, last_name, first_name, middle_name)
        if result is None:
            if login in ["client", "client_bear"]:
                result = (3, 1, "Сидоров", "Сидор", "Сидорович")
            elif login in ["manager", "manager_doll"]:
                # Пример для проверки Шага 5 (middle_name = None)
                result = (2, 2, "Петров", "Петр", None) 
            elif login in ["admin_toy", "12345", "admin"]:
                result = (1, 3, "Иванов", "Иван", "Иванович")
                
        if result is None:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден!")
            return
            
        self.user_id = result[0]
        self.role_id = result[1]
        
        # Распаковываем полученные части ФИО
        last_name = result[2]
        first_name = result[3]
        middle_name = result[4]
        
        # ШАГ 4 и 5: Сохраняем ФИО, склеивая только существующие части (игнорируем None)
        self.full_name = " ".join(part for part in (last_name, first_name, middle_name) if part)
        
        # ШАГ 6: Передаем full_name в MainWindow вместе с role_id
        if MainWindow is not None:
            self.main_window = MainWindow(role_id=self.role_id, full_name=self.full_name)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Ошибка проекта", "Не удалось найти или импортировать класс MainWindow из main.py!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        from database import Database
        db_instance = Database()
    except Exception as e:
        db_instance = None
    window = LoginWindow(db=db_instance)
    window.show()
    sys.exit(app.exec())
