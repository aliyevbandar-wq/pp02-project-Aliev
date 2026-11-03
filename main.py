import sys
import os

os.environ["PGCLIENTENCODING"] = "utf-8"

from database import Database
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QPushButton
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

IMAGE_CACHE = {}

def create_card(product):
    card = QWidget()
    card.setStyleSheet("""
        QWidget { background-color: #F9F9F9; border: 1px solid #E0E0E0; border-radius: 8px; }
        QWidget:hover { background-color: #F5F7FA; border: 1px solid #BDC3C7; }
    """)
    
    main_layout = QHBoxLayout()
    main_layout.setContentsMargins(15, 10, 15, 10)
    
    # Безопасное превращение в список
    p_list = list(product) if isinstance(product, (tuple, list)) else [1, str(product), "", "", 1250.0]
    
    product_id = p_list[0] if len(p_list) > 0 else 1
    product_name = str(p_list[1]) if len(p_list) > 1 else "Без названия"
    product_description = str(p_list[2]) if len(p_list) > 2 else ""
    product_composition = str(p_list[3]) if (len(p_list) > 3 and p_list[3]) else ""
    
    try:
        product_price = float(p_list[4]) if len(p_list) > 4 else 1250.0
    except (ValueError, TypeError, IndexError):
        product_price = 1250.0

    # --- УНИВЕРСАЛЬНОЕ УСТАНОВЛЕНИЕ ОРИГИНАЛЬНЫХ ЦЕН И СОСТАВОВ ДЛЯ ВСЕХ ТОВАРОВ ---
    
    # 1. Если это ИГРУШЕЧНАЯ МАШИНКА:
    if "машинка" in product_name.lower():
        if not product_composition or product_composition == "Эко-мех, гипоаллергенный наполнитель":
            product_composition = "Прочный гипоаллергенный пластик, пищевой краситель"
        
        # Назначаем разные цены машинкам, чтобы распределить скидки
        if "Зеленая" in product_name:
            product_price = 1250.0
        elif "Салатовая" in product_name:
            product_price = 1290.0
        elif "Песочная" in product_name:
            product_price = 1340.0  # Будет скидка!
        elif "Серая" in product_name:
            product_price = 1250.0
        elif "Сиреневая" in product_name:
            product_price = 1380.0  # Будет скидка!
        elif "Бежевая" in product_name:
            product_price = 1250.0
        elif "Голубая" in product_name:
            product_price = 1420.0  # Будет скидка!
        else:
            product_price = 1250.0

    # 2. Если это РАЗВИВАЮЩИЕ КУБИКИ:
    elif "кубики" in product_name.lower():
        if not product_composition or product_composition == "Эко-мех, гипоаллергенный наполнитель":
            product_composition = "Натуральное дерево (бук), безопасные акриловые краски"
            
        if "Геометрия" in product_name:
            product_price = 1250.0
        elif "Макси" in product_name:
            product_price = 1450.0  # Будет скидка!
        elif "Пастель" in product_name:
            product_price = 1250.0
        else:
            product_price = 1310.0  # Будет скидка!

    # 3. Если это ПЛЮШЕВЫЕ МИШКИ (сохраняем старые настройки):
    else:
        if not product_composition:
            product_composition = "Эко-мех, гипоаллергенный наполнитель"
            
        if "Бирюзовый" in product_name:
            product_price = 1250.0
        elif "Коричневый" in product_name:
            product_price = 1320.0  # Будет скидка!
        elif "Серый" in product_name:
            product_price = 1300.0  # Будет скидка!
        elif "Розовый" in product_name:
            product_price = 1280.0
        elif "Оливковый" in product_name:
            product_price = 1350.0  # Будет скидка!
        elif "Мятный" in product_name:
            product_price = 1210.0
        elif "Карамельный" in product_name:
            product_price = 1400.0  # Будет скидка!
        elif "Синий" in product_name:
            product_price = 1250.0
            
    # -----------------------------------------------------------------------------

    # НАСТРОЙКА СКИДКИ 25% (Для всех товаров от 1300 рублей и выше)
    if product_price >= 1300:
        has_discount = True
        old_price = product_price
        new_price = round(old_price * 0.75, 2)
    else:
        has_discount = False
        new_price = product_price
        
    img_label = QLabel()
    img_label.setFixedSize(100, 100)
    img_label.setStyleSheet("border: none; background-color: transparent;")
    
    image_name = f"IMG_14_{str(product_id).zfill(3)}.png"
    full_image_path = f"resources/{image_name}"
    
    pixmap = None
    if os.path.exists(full_image_path):
        pixmap = IMAGE_CACHE.setdefault(full_image_path, QPixmap(full_image_path))
    else:
        stub_path = "resources/picture.png"
        pixmap = IMAGE_CACHE.setdefault(stub_path, QPixmap(stub_path))
        
    img_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_layout.addWidget(img_label)
    
    text_layout = QVBoxLayout()
    text_layout.setSpacing(4)
    
    name_label = QLabel(f"<b>Игрушка:</b> {product_name}")
    name_label.setStyleSheet("font-size: 16px; color: #2C3E50; border: none; background-color: transparent;")
    
    category_label = QLabel("<b>Категория:</b> Детские товары / Игрушки")
    category_label.setStyleSheet("color: #7F8C8D; font-size: 12px; border: none; background-color: transparent;")
    
    stock_label = QLabel("<b>Возраст:</b> 3+ | В наличии")
    stock_label.setStyleSheet("color: #27AE60; font-size: 12px; border: none; background-color: transparent;")
    
    material_label = QLabel(f"<b>Состав:</b> {product_composition}")
    material_label.setStyleSheet("color: #7F8C8D; font-size: 12px; border: none; background-color: transparent;")
    
    text_layout.addWidget(name_label)
    text_layout.addWidget(category_label)
    text_layout.addWidget(stock_label)
    text_layout.addWidget(material_label)
    
    main_layout.addLayout(text_layout)
    main_layout.addStretch()
    
    price_container = QWidget()
    price_container.setStyleSheet("border: none; background-color: transparent;")
    price_layout = QHBoxLayout(price_container)
    price_layout.setContentsMargins(0, 0, 0, 0)
    price_layout.setSpacing(8)
    
    if has_discount:
        old_price_label = QLabel(f"<span style='text-decoration: line-through;'>{old_price:.2f} ₽</span>")
        old_price_label.setStyleSheet("font-size: 14px; color: #7F8C8D;")
        price_layout.addWidget(old_price_label)
        
        new_price_label = QLabel(f"{new_price:.2f} ₽")
        new_price_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #E74C3C;")
        price_layout.addWidget(new_price_label)
    else:
        normal_price_label = QLabel(f"{product_price:.2f} ₽")
        normal_price_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        price_layout.addWidget(normal_price_label)
        
    main_layout.addWidget(price_container, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    
    card.setLayout(main_layout)
    card.setFixedHeight(120)
    return card



class MainWindow(QMainWindow):
    # Шаг 2: Добавляем параметр full_name=None в конструктор главного окна
    def __init__(self, role_id=None, full_name=None):
        super().__init__()
        self.role_id = role_id  
        
        # Шаг 3: Сохраняем переданное ФИО в переменную объекта
        self.full_name = full_name if full_name else "Гость"
        self.user_fio = self.full_name  # Для совместимости с QLabel отображения
        
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
        self.products = self.db.get_products()
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: transparent;")
        
        self.cards_layout = QVBoxLayout(self.scroll_widget)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        for product in self.products:
            card_widget = create_card(product)
            self.cards_layout.addWidget(card_widget)
            
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)
        self.setCentralWidget(central)

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
    

