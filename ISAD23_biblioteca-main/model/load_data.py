import hashlib
import sqlite3
import json

salt = "library"

try:
    con = sqlite3.connect("datos.db")
    cur = con.cursor()

    # Crear tablas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Author(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(40) UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Book(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(50),
            author INTEGER,
            cover VARCHAR(50),
            description TEXT,
            FOREIGN KEY(author) REFERENCES Author(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS User(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(20),
            email VARCHAR(30),
            password VARCHAR(64)  -- Usar SHA-256
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Session(
            session_hash VARCHAR(64) PRIMARY KEY,
            user_id INTEGER,
            last_login FLOAT,
            FOREIGN KEY(user_id) REFERENCES User(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS User_Reserved_Book(
            user_id INTEGER,
            book_id INTEGER,
            PRIMARY KEY (user_id, book_id),
            FOREIGN KEY(user_id) REFERENCES User(id),
            FOREIGN KEY(book_id) REFERENCES Book(id)
        )
    """)

    # Insertar usuarios
    with open('usuarios.json', 'r') as f:
        usuarios = json.load(f)['usuarios']

    for user in usuarios:
        dataBase_password = user['password'] + salt
        hashed = hashlib.sha256(dataBase_password.encode())
        dataBase_password = hashed.hexdigest()
        cur.execute("INSERT INTO User VALUES (NULL, ?, ?, ?)", (user['nombres'], user['email'], dataBase_password))
        con.commit()

    # Insertar libros
    with open('libros.tsv', 'r') as f:
        libros = [x.split("\t") for x in f.readlines()]

    for author, title, cover, description in libros:
        cur.execute("INSERT OR IGNORE INTO Author (name) VALUES (?)", (author,))
        con.commit()

        cur.execute("SELECT id FROM Author WHERE name=?", (author,))
        author_id = cur.fetchone()[0]

        cur.execute("INSERT INTO Book VALUES (NULL, ?, ?, ?, ?)",
                    (title, author_id, cover, description.strip()))
        con.commit()

except sqlite3.Error as e:
    print("Error en la base de datos:", e)
finally:
    if con:
        con.close()

