
import mysql.connector
from mysql.connector import Error
from db_config import DB_PASSWORD

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=DB_PASSWORD,
        database="photocenter_db"
    )

    cursor = connection.cursor()

    print("================================")
    print("       ФОТОЦЕНТР")
    print("================================")

    while True:
        print("\nГЛАВНОЕ МЕНЮ")
        print("1. Список клиентов")
        print("8. Добавить нового клиента")
        print("2. Список сотрудников")
        print("3. Список услуг")
        print("9. Добавить новую услугу")
        print("4. Список заказов")
        print("5. Состав заказов")
        print("6. Полный отчет по заказам")
        print("7. Общая выручка")
        print("10. Создать новый заказ")
        print("0. Выход")

        choice = input("\nВыберите пункт меню: ")

        if choice == "1":
            cursor.execute("SELECT * FROM clients")
            print("\nСПИСОК КЛИЕНТОВ:")
            for row in cursor.fetchall():
                print(row)

        elif choice == "2":
            cursor.execute("SELECT * FROM employees")
            print("\nСПИСОК СОТРУДНИКОВ:")
            for row in cursor.fetchall():
                print(row)

        elif choice == "3":
            cursor.execute("SELECT * FROM services")
            print("\nСПИСОК УСЛУГ:")
            for row in cursor.fetchall():
                print(row)

        elif choice == "4":
            cursor.execute("SELECT * FROM orders")
            print("\nСПИСОК ЗАКАЗОВ:")
            for row in cursor.fetchall():
                print(row)

        elif choice == "5":
            cursor.execute("SELECT * FROM order_details")
            print("\nСОСТАВ ЗАКАЗОВ:")
            for row in cursor.fetchall():
                print(row)

        elif choice == "6":
            cursor.execute("""
                SELECT
                    o.order_id,
                    c.first_name,
                    c.last_name,
                    s.name,
                    od.quantity,
                    od.price,
                    od.quantity * od.price
                FROM orders o
                JOIN clients c ON o.client_id = c.client_id
                JOIN order_details od
                    ON o.order_id = od.order_id
                JOIN services s
                    ON od.service_id = s.service_id
                ORDER BY o.order_id
            """)

            print("\nПОЛНЫЙ ОТЧЕТ ПО ЗАКАЗАМ:")
            for row in cursor.fetchall():
                print(row)

        elif choice == "7":
            cursor.execute("""
                SELECT COALESCE(SUM(quantity * price), 0)
                FROM order_details
            """)
            total = cursor.fetchone()[0]

            print("\nОБЩАЯ ВЫРУЧКА ФОТОЦЕНТРА:")
            print(total, "руб.")

        elif choice == "8":
            print("\nДОБАВЛЕНИЕ НОВОГО КЛИЕНТА")

            first_name = input("Введите имя: ")
            last_name = input("Введите фамилию: ")
            phone = input("Введите телефон: ")
            email = input("Введите email: ")

            cursor.execute("""
                INSERT INTO clients
                (first_name, last_name, phone, email)
                VALUES (%s, %s, %s, %s)
            """, (first_name, last_name, phone, email))

            connection.commit()

            print("\nКлиент успешно добавлен!")

        elif choice == "9":
            print("\nДОБАВЛЕНИЕ НОВОЙ УСЛУГИ")

            name = input("Введите название услуги: ")
            description = input("Введите описание услуги: ")
            price = float(input("Введите стоимость услуги: "))

            cursor.execute("""
                INSERT INTO services (name, description, price)
                VALUES (%s, %s, %s)
            """, (name, description, price))

            connection.commit()

            print("\nУслуга успешно добавлена!")

        elif choice == "10":
            print("\nСОЗДАНИЕ НОВОГО ЗАКАЗА")

            try:
                print("\nКЛИЕНТЫ:")
                cursor.execute("""
                    SELECT client_id, first_name, last_name
                    FROM clients
                """)
                for row in cursor.fetchall():
                    print(row)

                client_id = int(input("Введите ID клиента: "))

                print("\nСОТРУДНИКИ:")
                cursor.execute("""
                    SELECT employee_id, first_name, last_name
                    FROM employees
                """)
                for row in cursor.fetchall():
                    print(row)

                employee_id = int(input("Введите ID сотрудника: "))

                print("\nУСЛУГИ:")
                cursor.execute("""
                    SELECT service_id, name, price
                    FROM services
                """)
                for row in cursor.fetchall():
                    print(row)

                service_id = int(input("Введите ID услуги: "))
                quantity = int(input("Введите количество: "))

                if quantity <= 0:
                    print("Количество должно быть больше нуля.")
                    continue

                cursor.execute("""
                    SELECT price FROM services
                    WHERE service_id = %s
                """, (service_id,))

                result = cursor.fetchone()

                if result is None:
                    print("Услуга не найдена!")
                    continue

                price = result[0]
                total = price * quantity

                cursor.execute("""
                    INSERT INTO orders
                    (client_id, employee_id, total_amount)
                    VALUES (%s, %s, %s)
                """, (client_id, employee_id, total))

                order_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO order_details
                    (order_id, service_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, service_id, quantity, price))

                connection.commit()

                print("\nЗАКАЗ УСПЕШНО СОЗДАН!")
                print("Номер заказа:", order_id)
                print("Стоимость:", total, "руб.")

            except ValueError:
                connection.rollback()
                print("Ошибка: введите целое число.")

            except Error as error:
                connection.rollback()
                print("Ошибка создания заказа:", error)

        elif choice == "0":
            print("\nРабота программы завершена!")
            break

        else:
            print("\nНеверный пункт меню!")

    cursor.close()
    connection.close()

except Error as error:
    print("Ошибка подключения:", error)
