import sqlite3

# 连接到数据库或创建一个新的数据库
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# 创建图书、用户和预订表
cursor.execute('''CREATE TABLE IF NOT EXISTS Books (
                    BookID TEXT PRIMARY KEY,
                    Title TEXT,
                    Author TEXT,
                    ISBN TEXT,
                    Status TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                    UserID TEXT PRIMARY KEY,
                    Name TEXT,
                    Email TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Reservations (
                    ReservationID TEXT PRIMARY KEY,
                    BookID TEXT,
                    UserID TEXT,
                    ReservationDate TEXT
                )''')


# 提供与用户进行交互的菜单
while True:
    print("\n图书馆管理系统菜单:")
    print("1. 添加新书")
    print("2. 查找书的详细信息")
    print("3. 查找图书的预订状态")
    print("4. 查找所有书")
    print("5. 更新图书信息")
    print("6. 删除图书")
    print("7. 退出")

    choice = input("请输入选项: ")

    if choice == "1":
        # 添加新书到Books表
        book_id = input("请输入图书编号: ")
        title = input("请输入标题: ")
        author = input("请输入作者: ")
        isbn = input("请输入ISBN: ")
        status = input("请输入图书状态: ")
        
        cursor.execute("INSERT INTO Books (BookID, Title, Author, ISBN, Status) VALUES (?, ?, ?, ?, ?)",
                       (book_id, title, author, isbn, status))
        conn.commit()
        print("图书添加成功!")

    elif choice == "2":
        # 查找书的详细信息
        search_input = input("请输入图书编号、标题、或用户ID: ")
        
        if search_input.startswith('LB'):
            cursor.execute("SELECT * FROM Books WHERE BookID=?", (search_input,))
        elif search_input.startswith('LU'):
            cursor.execute("SELECT * FROM Books WHERE BookID IN (SELECT BookID FROM Reservations WHERE UserID=?)",
                           (search_input,))
        elif search_input.startswith('LR'):
            cursor.execute("SELECT * FROM Reservations WHERE ReservationID=?", (search_input,))
        else:
            cursor.execute("SELECT * FROM Books WHERE Title=?", (search_input,))
        
        book = cursor.fetchone()
        if book:
            print("图书详细信息:")
            print("图书编号:", book[0])
            print("标题:", book[1])
            print("作者:", book[2])
            print("ISBN:", book[3])
            print("状态:", book[4])

        else:
            print("图书不存在!")

    elif choice == "3":
        # 查找图书的预订状态
        search_input = input("请输入图书编号、标题、或用户ID或ReservationID: ")

        if search_input.startswith('LB'):
            # 根据BookID查找图书的预订状态
            cursor.execute("SELECT ReservationID FROM Reservations WHERE BookID=?", (search_input,))
        elif search_input.startswith('LU'):
            # 根据UserID查找图书的预订状态
            cursor.execute("SELECT ReservationID FROM Reservations WHERE UserID=?", (search_input,))
        elif search_input.startswith('LR'):
             # 直接根据ReservationID查找
            cursor.execute("SELECT * FROM Reservations WHERE ReservationID=?", (search_input,))
        else:
            # 假定输入是书名（Title）
            cursor.execute("SELECT ReservationID FROM Reservations WHERE BookID IN (SELECT BookID FROM Books WHERE Title=?)",
                        (search_input,))

        reservations = cursor.fetchall()
        if reservations:
            print("图书的预订状态ReservationID:")
            for reservation in reservations:
                print(reservation[0])
        else:
            print("没有找到与输入匹配的预订状态ReservationID。")

    elif choice == "4":
        # 查找所有书，包括所有三个表的详细信息
        cursor.execute("SELECT * FROM Books")
        all_books = cursor.fetchall()
        
        if all_books:
            print("所有书的详细信息:")
            for book in all_books:
                print("图书编号:", book[0])
                print("标题:", book[1])
                print("作者:", book[2])
                print("ISBN:", book[3])
                print("状态:", book[4])
        else:
            print("没有找到任何书籍。")

    elif choice == "5":
        # 更新图书信息，如果修改涉及到更新图书的预订状态，则需要更新所有三个表
        book_id = input("请输入要更新的图书编号: ")
        title = input("请输入新的标题 (按回车键跳过): ")
        author = input("请输入新的作者 (按回车键跳过): ")
        isbn = input("请输入新的ISBN (按回车键跳过): ")
        status = input("请输入新的图书状态 (按回车键跳过): ")
        
        update_query = "UPDATE Books SET "
        update_values = []
        
        if title:
            update_query += "Title=?, "
            update_values.append(title)
        if author:
            update_query += "Author=?, "
            update_values.append(author)
        if isbn:
            update_query += "ISBN=?, "
            update_values.append(isbn)
        if status:
            update_query += "Status=?, "
            update_values.append(status)
        
        # 去掉最后的逗号和空格
        update_query = update_query.rstrip(', ')
        
        if update_values:
            update_query += " WHERE BookID=?"
            update_values.append(book_id)
            
            cursor.execute(update_query, tuple(update_values))
            conn.commit()
            print("图书信息已更新!")
        else:
            print("没有进行任何更新。")

    elif choice == "6":
        # 删除图书，如果被删除的书同时也被保留，需要同时删除Books和Reservations这两张表中的记录
        book_id = input("请输入要删除的图书编号: ")
        
        cursor.execute("DELETE FROM Books WHERE BookID=?", (book_id,))
        cursor.execute("DELETE FROM Reservations WHERE BookID=?", (book_id,))
        
        conn.commit()
        print("图书已删除!")

    elif choice == "7":
        break

# 关闭数据库连接
conn.close()
