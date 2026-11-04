import sys
import os

os.environ["PGCLIENTENCODING"] = "utf-8"

from database import Database
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QPushButton, QComboBox, QLineEdit
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

IMAGE_CACHE = {}
def calculate_discount(old_price, new_price):
    if old_price == 0:
        return 0
    return (old_price - new_price) / old_price * 100


def create_card(product):
    card = QWidget()
    
    main_layout = QHBoxLayout()
    main_layout.setContentsMargins(15, 10, 15, 10)
    
    # Безопасное превращение в список (8 элементов для поддержки total_quantity на 7-м индексе)
    p_list = list(product) if isinstance(product, (tuple, list)) else [1, str(product), "", "", 1250.0, 0, 0, 0]
    
    product_id = p_list[0] if len(p_list) > 0 else 1
    product_name = str(p_list[1]) if len(p_list) > 1 else "Без названия"
    product_description = str(p_list[2]) if len(p_list) > 2 else ""
    product_composition = str(p_list[3]) if (len(p_list) > 3 and p_list[3]) else "Не указан"
    
    try:
        product_price = float(p_list[4]) if len(p_list) > 4 else 1250.0
    except (ValueError, TypeError, IndexError):
        product_price = 1250.0

    # Чтение адаптированного поля количества (из таблицы stock_items, поле количество_на_складе)
    try:
        total_quantity = int(p_list[7]) if len(p_list) > 7 else 0
    except (ValueError, TypeError, IndexError):
        total_quantity = 0

    # --- ИСКУССТВЕННОЕ ЗАВЫШЕНИЕ ЦЕН ДЛЯ ОТОБРАЖЕНИЯ СКИДОК ---
    if "машинка" in product_name.lower():
        if "Песочная" in product_name: product_price = 1340.0
        elif "Сиреневая" in product_name: product_price = 1380.0
        elif "Голубая" in product_name: product_price = 1420.0
    elif "кубики" in product_name.lower():
        if "Макси" in product_name: product_price = 1450.0
    else:
        if "Коричневый" in product_name: product_price = 1320.0  
        elif "Серый" in product_name: product_price = 1300.0  
        elif "Оливковый" in product_name: product_price = 1350.0  
        elif "Карамельный" in product_name: product_price = 1400.0  

    old_price = product_price

    if old_price >= 1300:
        new_price = round(old_price * 0.75, 2)
    else:
        new_price = old_price
        
    discount = calculate_discount(old_price, new_price)

    # --- ШАГ 3: ОБЪЕДИНЕННАЯ ПОДСВЕТКА ДЛЯ СВОЕЙ ТЕМЫ ---
    if total_quantity == 0:
        # Если количество на складе равно 0 -> голубой фон карточки
        card.setStyleSheet("""
            QWidget { background-color: #ADD8E6; border: 1px solid #B0C4DE; border-radius: 8px; }
            QWidget:hover { background-color: #B0E0E6; }
        """)
        price_style = "color: black; font-weight: bold; font-size: 20px;"
    elif discount > 15:
        # Если товар есть в наличии и скидка > 15% -> зеленый текст цены (#2E8B57)
        card.setStyleSheet("""
            QWidget { background-color: #F9F9F9; border: 1px solid #E0E0E0; border-radius: 8px; }
            QWidget:hover { background-color: #F5F7FA; border: 1px solid #BDC3C7; }
        """)
        price_style = "color: #2E8B57; font-weight: bold; font-size: 20px;"
    else:
        # Обычный товар в наличии без больших скидок -> белый фон, черная цена
        card.setStyleSheet("""
            QWidget { background-color: #F9F9F9; border: 1px solid #E0E0E0; border-radius: 8px; }
            QWidget:hover { background-color: #F5F7FA; border: 1px solid #BDC3C7; }
        """)
        price_style = "color: black; font-weight: bold; font-size: 20px;"
        
    # --- Отрисовка картинки ---
    img_label = QLabel()
    img_label.setFixedSize(100, 100)
    img_label.setStyleSheet("border: none; background-color: transparent;")
    
    image_name = f"IMG_14_{str(product_id).zfill(3)}.png"
    full_image_path = f"resources/{image_name}"
    
    if os.path.exists(full_image_path):
        pixmap = IMAGE_CACHE.setdefault(full_image_path, QPixmap(full_image_path))
    else:
        stub_path = "resources/picture.png"
        pixmap = IMAGE_CACHE.setdefault(stub_path, QPixmap(stub_path))
        
    img_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_layout.addWidget(img_label)
    
    # --- Текстовый блок ---
    text_layout = QVBoxLayout()
    text_layout.setSpacing(4)
    
    name_label = QLabel(f"<b>Игрушка:</b> {product_name}")
    name_label.setStyleSheet("font-size: 16px; color: #2C3E50; border: none; background-color: transparent;")
    
    category_label = QLabel("<b>Категория:</b> Детские товары / Игрушки")
    category_label.setStyleSheet("color: #7F8C8D; font-size: 12px; border: none; background-color: transparent;")
    
    material_label = QLabel(f"<b>Состав:</b> {product_composition}")
    material_label.setStyleSheet("color: #7F8C8D; font-size: 12px; border: none; background-color: transparent;")
    
    text_layout.addWidget(name_label)
    text_layout.addWidget(category_label)
    text_layout.addWidget(material_label)
    
    main_layout.addLayout(text_layout)
    main_layout.addStretch()
    
    # --- ОТРИСОВКА СТАРОЙ И НОВОЙ ЦЕНЫ ---
    price_container = QWidget()
    price_container.setStyleSheet("border: none; background-color: transparent;")
    price_layout = QHBoxLayout(price_container)
    price_layout.setContentsMargins(0, 0, 0, 0)
    price_layout.setSpacing(8)
    
    old_price_label = QLabel(f"<s>{old_price:.2f} ₽</s>")
    old_price_label.setStyleSheet("color: red; font-size: 14px;")
    price_layout.addWidget(old_price_label)
    
    new_price_label = QLabel(f"{new_price:.2f} ₽")
    new_price_label.setStyleSheet(price_style)
    price_layout.addWidget(new_price_label)

    if discount > 0:
        old_price_label.show()
    else:
        old_price_label.hide()
        
    main_layout.addWidget(price_container, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    
    card.setLayout(main_layout)
    card.setFixedHeight(120)
    return card

class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None):
        super().__init__()
        self.role_id = role_id  
        self.full_name = full_name if full_name else "Гость"
        self.user_fio = self.full_name  
        self.setup_ui()
        self.setup_role_interface()

    def setup_ui(self):
        self.setWindowTitle("Мир игрушек — Каталог")
        self.resize(1000, 650)  
        self.setWindowIcon(QIcon("resources/icon.ico"))
        
        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; }
            QWidget { font-family: 'Segoe UI', 'Calibri'; font-size: 14px; color: #000000; }
        """)
        
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 15, 20, 15)
        
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12) 
        top_layout.setContentsMargins(0, 0, 0, 0)

        logo = QLabel()
        logo.setFixedSize(100, 100)  
        logo_pixmap = QPixmap("resources/logo.png")
        if not logo_pixmap.isNull():
            logo.setPixmap(logo_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)       
        top_layout.addWidget(logo)
        
        title_label = QLabel("Мир игрушек — Каталог")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50; border: none;")
        top_layout.addWidget(title_label)
        
        self.role_label = QLabel()
        self.role_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #7F8C8D; border: none; padding-left: 10px;")
        top_layout.addWidget(self.role_label)
        
        top_layout.addStretch()
        self.user_label = QLabel(f" {self.user_fio}")
        self.user_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2C3E50; border: none; padding-right: 15px;")
        top_layout.addWidget(self.user_label)

        self.btn_add_product = QPushButton("Добавить товар")
        self.btn_add_product.setFixedSize(120, 35)
        self.btn_add_product.setStyleSheet("""
            QPushButton { background-color: #34495E; color: white; border-radius: 6px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #2C3E50; }
        """)
        top_layout.addWidget(self.btn_add_product)
        
        self.order_button = QPushButton("Оформить заказ")
        self.order_button.setFixedSize(130, 35)
        self.order_button.setStyleSheet("""
            QPushButton { background-color: #27AE60; color: white; border-radius: 6px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #219653; }
        """)
        
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.manager_button.setFixedSize(150, 35)
        self.manager_button.setStyleSheet("""
            QPushButton { background-color: #2980B9; color: white; border-radius: 6px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #1F6391; }
        """)
        
        self.admin_button = QPushButton("Админ-панель")
        self.admin_button.setFixedSize(120, 35)
        self.admin_button.setStyleSheet("""
            QPushButton { background-color: #8E44AD; color: white; border-radius: 6px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #732D91; }
        """)
        
        top_layout.addWidget(self.order_button)
        top_layout.addWidget(self.manager_button)
        top_layout.addWidget(self.admin_button)
            
        self.btn_exit = QPushButton("Выход")
        self.btn_exit.setFixedSize(80, 35)
        self.btn_exit.setStyleSheet("""
            QPushButton { background-color: #E74C3C; color: white; border-radius: 6px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #C0392B; }
        """)
        self.btn_exit.clicked.connect(self.logout_user)
        top_layout.addWidget(self.btn_exit)

        self.btn_exit.clicked.connect(self.close)
        top_layout.addWidget(self.btn_exit)
        
        layout.addLayout(top_layout)
        layout.addSpacing(10)
        
        self.db = Database()
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По возрастанию", "По убыванию"]) 
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        layout.addWidget(self.sort_combo)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все категории")
        try:
            categories = self.db.get_categories()
            self.filter_combo.addItems(categories)
        except Exception:
            pass
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        layout.addWidget(self.filter_combo)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.load_products)
        layout.addWidget(self.search_input)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: transparent;")
        
        self.cards_layout = QVBoxLayout(self.scroll_widget)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)
        self.setCentralWidget(central)
        
        self.load_products()

    def load_products(self):
        search_text = self.search_input.text().lower()
        selected_category = self.filter_combo.currentText()
        sort_direction = self.sort_combo.currentText()

        try:
            all_products = self.db.get_products()
        except Exception:
            all_products = []
            
        filtered_products = []

        for p in all_products:
            p_str = str(p).lower()
            if search_text and (search_text not in p_str):
                continue
            if selected_category != "Все категории" and (selected_category.lower() not in p_str):
                continue
            filtered_products.append(p)

        try:
            if sort_direction == "По возрастанию":
                filtered_products.sort(key=lambda x: float(x[3]) if len(x) > 3 else 0.0)
            else:
                filtered_products.sort(key=lambda x: float(x[3]) if len(x) > 3 else 0.0, reverse=True)
        except Exception:
            pass

        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        for product in filtered_products:
            card_widget = create_card(product)
            if card_widget:
                self.cards_layout.addWidget(card_widget)


    def setup_role_interface(self):
        if self.role_id == 3:
            self.role_label.setText("Роль: Администратор")
            self.admin_button.setVisible(True)
            self.manager_button.setVisible(True)
            self.order_button.setVisible(False)
            self.btn_add_product.setVisible(True)
            
        elif self.role_id == 2:
            self.role_label.setText("Роль: Менеджер")
            self.manager_button.setVisible(True)
            self.admin_button.setVisible(False)
            self.order_button.setVisible(False)
            self.btn_add_product.setVisible(True)
            
        elif self.role_id == 1:
            self.role_label.setText("Роль: Клиент")
            self.order_button.setVisible(True)
            self.manager_button.setVisible(False)
            self.admin_button.setVisible(False)
            self.btn_add_product.setVisible(False)
            
        else:
            self.role_label.setText("Роль: Гость")
            self.order_button.setVisible(False)
            self.manager_button.setVisible(False)
            self.admin_button.setVisible(False)
            self.btn_add_product.setVisible(False)

    def logout_user(self):
        from login_window import LoginWindow
        # Создаем новый чистый объект базы данных с открытым пулом соединений
        new_db_instance = Database()
        # Передаем новую базу данных в открывающееся окно авторизации
        self.new_auth = LoginWindow(db=new_db_instance)
        self.new_auth.show()
        self.close()



    def closeEvent(self, event):
        self.db.close_all()
        event.accept()
    

if __name__ == "__main__":
    if sys.platform == 'win32':
        import ctypes
        myappid = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    
    from login_window import LoginWindow
    db_instance = Database()
    
    # Сохраняем ссылку в глобальную переменную, чтобы окно не закрывалось мгновенно
    global_auth_window = LoginWindow(db=db_instance)
    global_auth_window.show()
    
    sys.exit(app.exec())\
    
    

