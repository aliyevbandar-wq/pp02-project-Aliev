import os
import psycopg2
from psycopg2 import pool

# Принудительно заставляем Windows использовать UTF-8 для переменных окружения PostgreSQL
os.environ["PGCLIENTENCODING"] = "utf-8"


class Database:

    def __init__(self):
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1,
                5,
                dbname="toy_world_db",  # Имя базы данных
                user="postgres",  # Имя пользователя
                password="12345",  # Ваш пароль
                host="localhost",
                port="5432",
            )
            print("Пул соединений базы данных 'Мир игрушек' успешно создан.")
        except psycopg2.Error as e:
            print(f"Ошибка БД: {e}")
            self.connection_pool = None

    def get_connection(self):
        """Получает и возвращает свободное соединение из пула."""
        if self.connection_pool is None:
            return None
        return self.connection_pool.getconn()

    def release_connection(self, conn):
        """Возвращает использованное соединение обратно в пул."""
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)

    def get_products(self):
        """Метод получает список всех товаров из таблицы products."""
        conn = self.get_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM public.products;")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при выполнении запроса продуктов: {e}")
            return []
        finally:
            if "cursor" in locals():
                cursor.close()
            self.release_connection(conn)

    def get_categories(self):
        """Задание 1.1: Получает список уникальных категорий товаров."""
        conn = self.get_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM public.products;")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении категорий: {e}")
            return []
        finally:
            if "cursor" in locals():
                cursor.close()
            self.release_connection(conn)

    def check_user_login(self, login_text):
        """Проверяет существование логина в таблице public.users и возвращает данные пользователя"""
        conn = self.get_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            # Обновленный SQL-запрос под новые требования задания 5.1
            query = """
                SELECT user_id, login, role_id, last_name, first_name, middle_name 
                FROM public.users 
                WHERE login = %s;
            """
            cursor.execute(query, (login_text,))
            user_data = cursor.fetchone()
            
            if user_data:
                # Распаковываем полученные данные
                user_id, login, role_id, last_name, first_name, middle_name = user_data
                
                # Корректно склеиваем Фамилию, Имя и Отчество в одну строку
                fio_parts = [last_name, first_name, middle_name]
                full_name = " ".join([part for part in fio_parts if part])
                
                # Возвращаем кортеж с данными для авторизации (id, login, role_id, full_name)
                return (user_id, login, role_id, full_name)
                
            return None
        except Exception as e:
            print(f"[БД | ОШИБКА] Не удалось проверить логин: {e}")
            return None
        finally:
            if "cursor" in locals():
                cursor.close()
            self.release_connection(conn)

    def close_all(self):
        """Закрывает все соединения в пуле перед завершением программы."""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("Пул соединений закрыт.")


# Блок тестирования файла
if __name__ == "__main__":
    db = Database()
    print("Список игрушек:", db.get_products())
    print("Список категорий:", db.get_categories())
    print("Тест авторизации admin_toy:", db.check_user_login("admin_toy"))
    db.close_all()
