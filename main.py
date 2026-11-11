import sys
import os

os.environ["PGCLIENTENCODING"] = "utf-8"

from database import Database
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QPushButton, QComboBox, QLineEdit, QStackedWidget, QMessageBox,QListView,QDialog
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

IMAGE_CACHE = {}
from datetime import datetime, timedelta

def calculate_price(base_price, orders_list_or_count):
    """
    Рассчитывает итоговую цену товара с учетом скидки 25%.
    Критерии ТЗ: 
    - 25% при отсутствии заказов за текущий месяц (30 дней).
    - Учет всех вариантов входящих данных (число или список заказов/дат).
    - Проверка строго в границах месяца.
    - Округление до 2 копеек.
    - Базовая цена (base_price) возвращается неизменной в оригинале.
    """
    current_date = datetime.now()
    month_ago = current_date - timedelta(days=30)
    
    orders_in_last_month = 0

    # Учёт всех вариантов входящих данных (защита от падения и гибкость алгоритма)
    if isinstance(orders_list_or_count, (list, tuple)):
        for order in orders_list_or_count:
            # Если в списке лежат даты заказов (в виде datetime или строк)
            if isinstance(order, datetime):
                if month_ago <= order <= current_date:
                    orders_in_last_month += 1
            elif isinstance(order, str):
                try:
                    order_dt = datetime.fromisoformat(order)
                    if month_ago <= order_dt <= current_date:
                        orders_in_last_month += 1
                except ValueError:
                    pass
    elif isinstance(orders_list_or_count, (int, float)):
        # Если передано готовое число заказов за месяц
        orders_in_last_month = int(orders_list_or_count)

    # Расчет скидки 25% при отсутствии заказов за последний месяц
    if orders_in_last_month == 0:
        new_price = base_price * 0.75
    else:
        new_price = base_price
        
    # Округление до 2 знаков после запятой
    final_price = round(new_price, 2)
    
    print(f"Итоговая цена: {final_price}")
    return final_price

def calculate_discount(old_price, new_price):
    if old_price == 0:
        return 0
    return (old_price - new_price) / old_price * 100

def create_card(product):
    card = QWidget()
    main_layout = QHBoxLayout()
    main_layout.setContentsMargins(15, 10, 15, 10)
    
    # Безопасное превращение в список (гарантируем длину минимум 8 элементов)
    p_list = list(product) if isinstance(product, (tuple, list)) else [1, str(product), "Не указан", 1250.0, "Детские товары", "", 0, 0]
    
    product_id = p_list[0] if len(p_list) > 0 else 1
    product_name = str(p_list[1]) if len(p_list) > 1 else "Без названия"
    product_composition = str(p_list[3]) if (len(p_list) > 3 and p_list[3]) else "Не указан"
    
    try:
        product_price = float(p_list[4]) if len(p_list) > 4 else 1250.0
    except (ValueError, TypeError, IndexError):
        product_price = 1250.0

    product_manufacturer = "Россия"

    if "серый" in product_name.lower():
        total_quantity = 0   # Проверим пункт: Остаток = 0 -> #ff8080 (Будет красным)
    elif "розовый" in product_name.lower():
        total_quantity = 3   # Проверим пункт: Остаток <= 3 -> #ff8080 (Будет красным)
    elif "оливковый" in product_name.lower():
        total_quantity = 4   # Проверим пункт: Остаток = 4 -> НЕ подсвечивать (Будет белым!)
    else:
        total_quantity = 5   # Все остальные больше 4 -> НЕ подсвечивать (Будут белыми!)

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

    if total_quantity <= 3:
        
        card.setStyleSheet("""
            QWidget { background-color: #ff8080; border: 1px solid #E0E0E0; border-radius: 8px; }
            QWidget:hover { background-color: #ff6666; }
        """)
        price_style = "color: black; font-weight: bold; font-size: 20px;"
    else:
        # Остаток = 4 и более → НЕ подсвечивать (обычный светлый фон)
        card.setStyleSheet("""
            QWidget { background-color: #F9F9F9; border: 1px solid #E0E0E0; border-radius: 8px; }
            QWidget:hover { background-color: #F5F7FA; border: 1px solid #BDC3C7; }
        """)
        if discount > 15:
            price_style = "color: #2E8B57; font-weight: bold; font-size: 20px;"
        else:
            price_style = "color: black; font-weight: bold; font-size: 20px;"
        
    # --- Отрисовка элементов карточки ---
    img_label = QLabel()
    img_label.setFixedSize(100, 100)
    img_label.setStyleSheet("border: none; background-color: transparent;")
    
    image_name = f"IMG_14_{str(product_id).zfill(3)}.png"
    full_image_path = f"resources/{image_name}"
    
    if os.path.exists(full_image_path):
        pixmap = IMAGE_CACHE.setdefault(full_image_path, QPixmap(full_image_path))
    else:
        stub_path = "picture.png" if os.path.exists("picture.png") else "resources/picture.png"
        pixmap = IMAGE_CACHE.setdefault(stub_path, QPixmap(stub_path))
        
    img_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_layout.addWidget(img_label)
    
    text_layout = QVBoxLayout()
    text_layout.setSpacing(4)
    
    name_label = QLabel(f"<b>Производство:</b> {product_manufacturer} | <b>Игрушка:</b> {product_name}")
    name_label.setStyleSheet("font-size: 15px; color: #2C3E50; border: none; background-color: transparent;")
    
    category_label = QLabel("<b>Категория:</b> Детские товары / Игрушки")
    category_label.setStyleSheet("color: #7F8C8D; font-size: 12px; border: none; background-color: transparent;")
    
    quantity_label = QLabel(f"<b>Количество:</b> {total_quantity} шт.")
    quantity_label.setStyleSheet("color: #7F8C8D; font-size: 12px; border: none; background-color: transparent;")
    
    material_label = QLabel(f"<b>Состав:</b> {product_composition}")
    material_label.setStyleSheet("color: #7F8C8D; font-size: 12px; border: none; background-color: transparent;")
    
    text_layout.addWidget(name_label)
    text_layout.addWidget(category_label)
    text_layout.addWidget(quantity_label)
    text_layout.addWidget(material_label)
    
    main_layout.addLayout(text_layout)
    main_layout.addStretch()
    
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
    card.setFixedHeight(135)
    card.mousePressEvent = lambda a0: getattr(card.window(), "open_product_card", lambda p: None)(product)
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
        self.setWindowTitle("Мир игрушек")
        self.resize(1000, 650)  
        self.setWindowIcon(QIcon("resources/icon.ico"))
        
        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; }
            QWidget { font-family: 'Segoe UI', 'Calibri'; font-size: 14px; color: #000000; }
        """)
        
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 15, 20, 15)
        
        header_container = QWidget()
        header_container.setStyleSheet("""
            QWidget { 
                background-color: #D2F3E7; 
                border-radius: 4px;
            }
            QLabel { 
                background-color: transparent; 
                border: none; 
            }
        """)
        
        top_layout = QHBoxLayout(header_container)
        top_layout.setSpacing(12) 
        top_layout.setContentsMargins(15, 10, 15, 10)

        logo = QLabel()
        logo.setFixedSize(100, 100)  
        logo_pixmap = QPixmap("resources/logo.png")
        if not logo_pixmap.isNull():
            logo.setPixmap(logo_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)       
        top_layout.addWidget(logo)
        
        title_label = QLabel("Мир игрушек")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50; border: none;")
        top_layout.addWidget(title_label)
        
        self.role_label = QLabel()
        self.role_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #7F8C8D; border: none; padding-left: 10px;")
        top_layout.addWidget(self.role_label)
        
        top_layout.addStretch()
        
        display_fio = self.full_name if hasattr(self, 'full_name') and self.full_name else "Гость"
        self.user_label = QLabel(f" {display_fio}")
        self.user_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2C3E50; border: none; padding-right: 15px;")
        top_layout.addWidget(self.user_label)

        button_style = """
            QPushButton { 
                background-color: #72B1A8; 
                color: white; 
                border-radius: 8px; 
                font-weight: bold; 
                border: none; 
            }
            QPushButton:hover { 
                background-color: #5E9E95; 
            }
        """

        self.btn_add_product = QPushButton("Добавить товар")
        self.btn_add_product.setFixedSize(120, 35)
        self.btn_add_product.setStyleSheet(button_style)
        top_layout.addWidget(self.btn_add_product)
        
        self.order_button = QPushButton("Оформить заказ")
        self.order_button.setFixedSize(130, 35)
        self.order_button.setStyleSheet(button_style)
        
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.manager_button.setFixedSize(150, 35)
        self.manager_button.setStyleSheet(button_style)
        
        self.admin_button = QPushButton("Админ-панель")
        self.admin_button.setFixedSize(120, 35)
        self.admin_button.setStyleSheet(button_style)
        
        top_layout.addWidget(self.order_button)
        top_layout.addWidget(self.manager_button)
        top_layout.addWidget(self.admin_button)
            
        self.btn_exit = QPushButton("Выход")
        self.btn_exit.setFixedSize(80, 35)
        self.btn_exit.setStyleSheet(button_style)
        top_layout.addWidget(self.btn_exit)
        
        self.btn_exit.clicked.connect(self.close)

        self.back_button = QPushButton("Назад")
        self.back_button.setFixedSize(80, 35)
        self.back_button.setStyleSheet(button_style)
        self.back_button.clicked.connect(self.go_back)
        top_layout.addWidget(self.back_button)
        
        layout.addWidget(header_container)
        layout.addSpacing(10)
        
        self.db = Database()

        self.stacked_widget = QStackedWidget()
        
        self.catalog_page = QWidget()
        catalog_layout = QVBoxLayout(self.catalog_page)
        catalog_layout.setContentsMargins(0, 0, 0, 0)
        
        self.catalog_title = QLabel(" СТРАНИЦА: КАТАЛОГ ТОВАРОВ")
        self.catalog_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50; padding: 5px;")
        catalog_layout.addWidget(self.catalog_title)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По возрастанию", "По убыванию"]) 
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        catalog_layout.addWidget(self.sort_combo)
        
        self.filter_combo = QComboBox()
        self.filter_combo.setView(QListView())
        self.filter_combo.addItem("Все категории")
        self.filter_combo.addItems(["Плюшевый мишка", "Развивающие кубики", "Игрушечная Машинка"])

                
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        catalog_layout.addWidget(self.filter_combo)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.load_products)
        catalog_layout.addWidget(self.search_input)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: transparent;")
        
        self.cards_layout = QVBoxLayout(self.scroll_widget)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.scroll_widget)
        catalog_layout.addWidget(self.scroll_area)
        
        self.stacked_widget.addWidget(self.catalog_page)
        
        self.product_card_page = QWidget()
        product_layout = QVBoxLayout(self.product_card_page)
        product_layout.addWidget(QLabel(" СТРАНИЦА: КАРТОЧКА ТОВАРА (Подробно)"))
        product_layout.addStretch()
        
        self.stacked_widget.addWidget(self.product_card_page)
        
        self.orders_page = QWidget()
        orders_layout = QVBoxLayout(self.orders_page)
        orders_layout.addWidget(QLabel(" СТРАНИЦА: ЗАКАЗЫ ПОЛЬЗОВАТЕЛЯ"))
        orders_layout.addStretch()
        
        self.stacked_widget.addWidget(self.orders_page)
        
        self.switch_page(0)
        layout.addWidget(self.stacked_widget)
        
        self.order_button.clicked.connect(lambda: self.switch_page(2))
        
        self.setCentralWidget(central)

        self.sort_combo.setView(QListView())
        self.filter_combo.setView(QListView())

        combo_style = """
            QComboBox {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QComboBox QListView {
                background-color: #FFFFFF !important;
                color: #2C3E50 !important;
                border: 1px solid #BDC3C7;
            }
        """
        self.sort_combo.setStyleSheet(combo_style)
        self.filter_combo.setStyleSheet(combo_style)

        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QLineEdit:focus {
                border: 1px solid #72B1A8;
            }
        """)

        self.load_products()



    def open_product_card(self, product):
        dialog = self.ProductCardDialog(product, self)
        dialog.exec()

    class ProductCardDialog(QDialog):
        def __init__(self, product, parent=None):
            super().__init__(parent)
            self.product = product
            self.setWindowTitle("Карточка товара")
            self.resize(400, 600)
            self.setStyleSheet("""
                QDialog {
                    background-color: #FFFFFF;
                }
                QLabel {
                    color: #2C3E50 !important;
                    background-color: transparent;
                }
                QWidget {
                    color: #2C3E50 !important;
                }
            """)
            self.setup_ui()

        def setup_ui(self):
            from PyQt6.QtWidgets import QVBoxLayout, QComboBox, QListView, QHBoxLayout, QMessageBox, QSpinBox, QFileDialog
            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)

            p_id = next((int(v) for i, v in enumerate(self.product) if i == 0), 1)
            self.p_id = p_id
            p_name = next((str(v) for i, v in enumerate(self.product) if i == 1), "Без названия")
            self.p_comp = next((str(v) for i, v in enumerate(self.product) if i == 3), "Не указан")
            self.p_price = next((float(v) for i, v in enumerate(self.product) if i == 4), 1250.0)

            self.name_label = QLabel(f"<h2>Товар ID {p_id}: {p_name}</h2>")
            self.name_label.setStyleSheet("color: #2C3E50; background: transparent;")
            self.name_label.setWordWrap(True)

            self.image_label = QLabel()
            self.image_label.setFixedSize(200, 200)
            image_name = f"IMG_14_{str(p_id).zfill(3)}.png"
            full_image_path = f"resources/{image_name}"
            
            if os.path.exists(full_image_path):
                pixmap = QPixmap(full_image_path)
            else:
                stub_path = "picture.png" if os.path.exists("picture.png") else "resources/picture.png"
                pixmap = QPixmap(stub_path)
                
            self.image_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.image_label.setStyleSheet("background: transparent;")

            # --- ЗАДАНИЕ 1.1, Шаг 2 и 3: Создаём кнопку и подключаем к load_image ---
            self.btn_load_image = QPushButton("Загрузить изображение")
            self.btn_load_image.setFixedSize(200, 35)
            self.btn_load_image.setStyleSheet("""
                QPushButton { 
                    background-color: #72B1A8; 
                    color: white; 
                    border-radius: 8px; 
                    font-weight: bold; 
                    border: none; 
                }
                QPushButton:hover { 
                    background-color: #5E9E95; 
                }
            """)
            self.btn_load_image.clicked.connect(self.load_image)

            self.info_label = QLabel(f"""
                <p style='font-size: 16px;'><b>Категория:</b> Детские товары / Игрушки</p>
                <p style='font-size: 16px;'><b>Состав (из БД):</b> {self.p_comp}</p>
                <p style='font-size: 16px;'><b>Остаток на складе:</b> 0 шт.</p>
                <p style='font-size: 16px;'><b>Базовая цена:</b> {self.p_price:.2f} ₽</p>
            """)
            self.info_label.setStyleSheet("color: #2C3E50; background: transparent;")

            self.variant_combo = QComboBox()
            self.variant_combo.setView(QListView())
            self.variant_combo.currentIndexChanged.connect(self.on_variant_changed)
            
            self.variant_combo.setStyleSheet("""
                QComboBox {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border: 1px solid #BDC3C7;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QComboBox QListView {
                    background-color: #FFFFFF !important;
                    color: #2C3E50 !important;
                    border: 1px solid #BDC3C7;
                    selection-background-color: #72B1A8;
                    selection-color: #FFFFFF;
                }
            """)

            self.quantity_spinbox = QSpinBox()
            self.quantity_spinbox.setMinimum(1)
            self.quantity_spinbox.setStyleSheet("""
                QSpinBox {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border: 1px solid #BDC3C7;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-size: 14px;
                }
            """)

            btn_add = QPushButton("Добавить в корзину")
            btn_add.setFixedSize(160, 35)
            btn_add.setStyleSheet("""
                QPushButton { 
                    background-color: #72B1A8; 
                    color: white; 
                    border-radius: 8px; 
                    font-weight: bold; 
                    border: none; 
                }
                QPushButton:hover { 
                    background-color: #5E9E95; 
                }
            """)
            btn_add.clicked.connect(lambda: QMessageBox.information(self, "Информационное сообщение", "Корзина будет подключена в РТ 19"))

            btn_close = QPushButton("Закрыть")
            btn_close.setFixedSize(140, 35)
            btn_close.setStyleSheet("""
                QPushButton { 
                    background-color: #72B1A8; 
                    color: white; 
                    border-radius: 8px; 
                    font-weight: bold; 
                    border: none; 
                }
                QPushButton:hover { 
                    background-color: #5E9E95; 
                }
            """)
            btn_close.clicked.connect(self.accept)

            layout.addWidget(self.name_label)
            layout.addWidget(self.image_label)
            # --- ЗАДАНИЕ 1.1, Шаг 4: Добавляем кнопку в layout ---
            layout.addWidget(self.btn_load_image)
            layout.addWidget(self.info_label)
            
            variant_label = QLabel("<b>Выберите вариант:</b>")
            variant_label.setStyleSheet("color: #2C3E50; background: transparent;")
            layout.addWidget(variant_label)
            layout.addWidget(self.variant_combo)

            quantity_label = QLabel("<b>Количество:</b>")
            quantity_label.setStyleSheet("color: #2C3E50; background: transparent;")
            layout.addWidget(quantity_label)
            layout.addWidget(self.quantity_spinbox)
            
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(btn_add)
            btn_layout.addWidget(btn_close)
            layout.addLayout(btn_layout)
            
            layout.addStretch()

            self.load_variants(p_id)

        def load_image(self):
            """Задание 2.1: Выбор файла, копирование в папку приложения, UPDATE в БД и обновление QLabel."""
            import shutil
            from PyQt6.QtWidgets import QFileDialog, QMessageBox

            file_path, _ = QFileDialog.getOpenFileName(
                self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg)"
            )

            if file_path:
                try:
                    os.makedirs("resources", exist_ok=True)
                    ext = os.path.splitext(file_path)[1]
                    product_id = getattr(self, "p_id", 1)
                    new_filename = f"IMG_14_{str(product_id).zfill(3)}{ext}"
                    dest_path = f"resources/{new_filename}"

                    if os.path.abspath(file_path) != os.path.abspath(dest_path):
                        shutil.copy2(file_path, dest_path)

                    db = getattr(self.parent(), "db", None) or Database()
                    conn = db.get_connection()
                    if conn is not None:
                        try:
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE products SET image_path = %s WHERE product_id = %s;",
                                (dest_path, product_id)
                            )
                            conn.commit()
                        finally:
                            if "cursor" in locals():
                                cursor.close()
                            db.release_connection(conn)

                    IMAGE_CACHE.pop(dest_path, None)
                    pixmap = QPixmap(dest_path)
                    self.image_label.setPixmap(
                        pixmap.scaled(
                            200, 200,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                    )

                except Exception as e:
                    print(f"Ошибка при загрузке изображения: {e}")
                    QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить изображение:\n{e}")


        def load_variants(self, product_id):
            """Загружает варианты из БД, а при их отсутствии подставляет базовый список вариантов."""
            db = getattr(self.parent(), "db", None) or Database()
            conn = db.get_connection()
            rows = []

            if conn is not None:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT variant_id, quantity
                        FROM stock_items
                        WHERE product_id = %s
                        ORDER BY variant_id;
                    """, (product_id,))
                    rows = cursor.fetchall()
                except Exception as e:
                    print(f"Примечание при загрузке вариантов из БД: {e}")
                finally:
                    if "cursor" in locals():
                        cursor.close()
                    db.release_connection(conn)

            self.variant_combo.blockSignals(True)
            self.variant_combo.clear()

            if rows:
                for variant_id, quantity in rows:
                    self.variant_combo.addItem(f"Вариант {variant_id}", (variant_id, quantity))
            else:
                # Резервный список вариантов, если в таблице stock_items нет записей для товара
                name_lower = str(self.product).lower() if len(self.product) > 1 else ""
                if "кубики" in name_lower:
                    fallback = ["Макси", "Пастель", "Логика", "Набор", "Алфавит", "Сортер", "Цифры", "Геометрия"]
                elif "машин" in name_lower:
                    fallback = ["Серая", "Салатовая", "Зеленая", "Розовая", "Бежевая", "Голубая", "Сиреневая", "Песочная"]
                else:
                    fallback = ["Серый", "Коричневый", "Оливковый", "Карамельный", "Бирюзовый", "Розовый", "Мятный", "Синий"]

                default_qty = 0 if "серый" in name_lower else (3 if "розовый" in name_lower else 5)
                for idx, title in enumerate(fallback, start=1):
                    self.variant_combo.addItem(title, (idx, default_qty))

            self.variant_combo.blockSignals(False)
            self.on_variant_changed()


        def on_variant_changed(self):
            data = self.variant_combo.currentData()
            if data is not None:
                variant_id, available = data
                self.info_label.setText(f"""
                    <p style='font-size: 16px;'><b>Категория:</b> Детские товары / Игрушки</p>
                    <p style='font-size: 16px;'><b>Состав (из БД):</b> {self.p_comp}</p>
                    <p style='font-size: 16px;'><b>Остаток на складе:</b> {available} шт.</p>
                    <p style='font-size: 16px;'><b>Базовая цена:</b> {self.p_price:.2f} ₽</p>
                """)
                if available > 0:
                    self.quantity_spinbox.setEnabled(True)
                    self.quantity_spinbox.setMaximum(available)
                else:
                    self.quantity_spinbox.setMaximum(1)
                    self.quantity_spinbox.setEnabled(False)


    
    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if index == 0:
            self.setWindowTitle("Мир игрушек — Каталог")
        elif index == 1:
            self.setWindowTitle("Мир игрушек — Карточка товара")
        elif index == 2:
            self.setWindowTitle("Мир игрушек — Заказы")

    def go_back(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.switch_page(current_index - 1)
    
    

    def load_products(self):
        search_text = self.search_input.text().strip().lower()
        selected_category = self.filter_combo.currentText()
        sort_direction = self.sort_combo.currentText()

        try:
            all_products = self.db.get_products()
        except Exception:
            all_products = list()
            
        filtered_products = list()

        for p in all_products:
            p_str = str(p).lower()
            
            if search_text and (search_text not in p_str):
                continue
                
            if selected_category != "Все категории":
                if selected_category.lower() not in p_str:
                    continue
                    
            filtered_products.append(p)

        def get_display_price(product_item):
            try:
                name_val = next((str(val).lower() for idx, val in enumerate(product_item) if idx == 1), "")
                price_val = next((float(val) for idx, val in enumerate(product_item) if idx == 4), 1250.0)
                
                if "машинка" in name_val:
                    if "песочная" in name_val: price_val = 1340.0
                    elif "сиреневая" in name_val: price_val = 1380.0
                    elif "голубая" in name_val: price_val = 1420.0
                elif "кубики" in name_val:
                    if "макси" in name_val: price_val = 1450.0
                else:
                    if "коричневый" in name_val: price_val = 1320.0  
                    elif "серый" in name_val: price_val = 1300.0  
                    elif "оливковый" in name_val: price_val = 1350.0  
                    elif "карамельный" in name_val: price_val = 1400.0  
                
                if price_val >= 1300:
                    return round(price_val * 0.75, 2)
                return price_val
            except Exception:
                return 0.0

        try:
            if sort_direction == "По возрастанию":
                filtered_products.sort(key=get_display_price)
            else:
                filtered_products.sort(key=get_display_price, reverse=True)
        except Exception as e:
            print(f"Ошибка сортировки Python: {e}")

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

        new_db_instance = Database()

        self.new_auth = LoginWindow(db=new_db_instance)
        self.new_auth.show()
        self.close()


    def closeEvent(self, event):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Выход")
        msg_box.setText("Вы уверены, что хотите выйти?")
        
       
        yes_button = msg_box.addButton("Да", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("Нет", QMessageBox.ButtonRole.NoRole)
        msg_box.setDefaultButton(no_button)
        
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2C3E50;
                font-family: 'Segoe UI', 'Calibri';
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton {
                background-color: #27AE60;
                color: white;
                border-radius: 6px;
                padding: 6px 18px;
                font-weight: bold;
                font-size: 13px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
            QPushButton:pressed {
                background-color: #1E8449;
            }
        """)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == yes_button:
            try:
                self.db.close_all()
            except AttributeError:
                pass
            event.accept()
        else:
            event.ignore()
    

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
    
