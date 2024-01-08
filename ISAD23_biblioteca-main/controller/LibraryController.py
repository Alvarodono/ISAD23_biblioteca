from datetime import datetime

from flask import session
from model import Connection, Book, User
from model.tools import hash_password

db = Connection()


def get_reviews_by_user(user_email):
    query = """
        SELECT r.*, b.title as book_title, b.author as book_author
        FROM Reviews r
        INNER JOIN Book b ON r.book_id = b.id
        WHERE r.user_email = ?
        ORDER BY r.date_time DESC
    """
    reviews_data = db.select(query, (user_email,))
    reviews = [
        {
            'id': review[0],
            'book_id': review[1],
            'user_email': review[2],
            'title': review[6],
            'rating': review[3],
            'review_text': review[4],
            'date_time': review[5],
            'book_author': review[7],
        }
        for review in reviews_data
    ]
    return reviews


class LibraryController:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(LibraryController, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def get_reviews_by_user(self, user_email):
        query = """
            SELECT r.*, b.title as book_title, b.author as book_author
            FROM Reviews r
            INNER JOIN Book b ON r.book_id = b.id
            WHERE r.user_email = ?
            ORDER BY r.date_time DESC
        """
        reviews_data = db.select(query, (user_email,))
        reviews = [
            {
                'id': review[0],
                'book_id': review[1],
                'user_email': review[2],
                'title': review[6],
                'rating': review[3],
                'review_text': review[4],
                'date_time': review[5],
                'book_author': review[7],
            }
            for review in reviews_data
        ]
        return reviews

    def save_review(self, book_id, user_email, title, rating, review_text):
        try:
            book_title = title
            existing_review = db.select_one(
                "SELECT * FROM Reviews WHERE user_email = ? AND book_id = ?",
                (user_email, book_id)
            )

            if existing_review:
                print(f"Review already exists for user_email={user_email} and book_id={book_id}")
                return False

            db.insert(
                "INSERT INTO Reviews (user_email, book_id, title, rating, review_text) VALUES (?, ?, ?, ?, ?)",
                (user_email, book_id, book_title, rating, review_text)
            )

            print(f"Review saved successfully for user_email={user_email} and book_id={book_id}")
            return True

        except Exception as e:
            print(f"Error saving review: {e}")
            return False

    def get_review_by_id(self, review_id):
        query = "SELECT * FROM Reviews WHERE id = ?"
        review = db.select(query, (review_id,))
        return review[0] if len(review) > 0 else None


    def search_books(self, title="", author="", limit=6, page=0):
        count = db.select("""
                SELECT count() 
                FROM Book b, Author a 
                WHERE b.author=a.id 
                    AND b.title LIKE ? 
                    AND a.name LIKE ? 
        """, (f"%{title}%", f"%{author}%"))[0][0]
        res = db.select("""
                SELECT b.* 
                FROM Book b, Author a 
                WHERE b.author=a.id 
                    AND b.title LIKE ? 
                    AND a.name LIKE ? 
                LIMIT ? OFFSET ?
        """, (f"%{title}%", f"%{author}%", limit, limit * page))
        books = [
            Book(b[0], b[1], b[2], b[3], b[4])
            for b in res
        ]
        return books, count

    def get_user(self, email, password):
        user = db.select("SELECT * from User WHERE email = ? AND password = ?", (email, hash_password(password)))
        if len(user) > 0:
            return User(user[0][0], user[0][1], user[0][2])
        else:
            return None

    def get_user_cookies(self, token, time):
        user = db.select(
            "SELECT u.* from User u, Session s WHERE u.id = s.user_id AND s.last_login = ? AND s.session_hash = ?",
            (time, token))
        if len(user) > 0:
            return User(user[0][0], user[0][1], user[0][2])
        else:
            return None

    def search_book_by_id(self, book_id):
        res = db.select("SELECT * FROM Book WHERE id = ?", (book_id,))
        if res:
            book_data = res[0]
            return Book(book_data[0], book_data[1], book_data[2], book_data[3], book_data[4])
        else:
            return None

    def reserve_book(self, book_id, user_email):
        result = self.save_reserved_book(book_id, user_email)
        return result

    def save_reserved_book(self, book_id, user_email):
        try:
            existing_reservation = db.select_one(
                "SELECT * FROM User_Reserved_Book WHERE user_email = ? AND book_id = ?",
                (user_email, book_id)
            )

            if existing_reservation:
                return False

            db.insert(
                "INSERT INTO User_Reserved_Book (user_email, book_id) VALUES (?, ?)",
                (user_email, book_id)
            )

            return True

        except Exception as e:
            print(f"Error al reservar el libro: {e}")
            return False

    def get_reserved_books(self, user_email):
        query = """
            SELECT b.*
            FROM Book b
            JOIN User_Reserved_Book urb ON b.id = urb.book_id
            WHERE urb.user_email = ?
        """
        reserved_books_data = db.select(query, (user_email,))

        reserved_books = [
            Book(book_data[0], book_data[1], book_data[2], book_data[3], book_data[4])
            for book_data in reserved_books_data
        ]

        return reserved_books

    def get_read_books(self, user_email):
        query = """
                SELECT b.*
                FROM Book b
                INNER JOIN User_Read_Books urb ON b.id = urb.book_id
                WHERE urb.user_email = ?
            """
        read_books_data = db.select(query, (user_email,))
        read_books = [
            Book(b[0], b[1], b[2], b[3], b[4])
            for b in read_books_data
        ]
        return read_books

    def return_book(self, book_id, user_email):
        try:
            existing_read_book = db.select_one(
                "SELECT * FROM User_Read_Books WHERE user_email = ? AND book_id = ?",
                (user_email, book_id)
            )

            db.delete(
                "DELETE FROM User_Reserved_Book WHERE user_email = ? AND book_id = ?",
                (user_email, book_id)
            )

            if existing_read_book:
                return False

            db.insert(
                "INSERT INTO User_Read_Books (user_email, book_id, date_read) VALUES (?, ?, ?)",
                (user_email, book_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )

            return True

        except Exception as e:
            print(f"Error al devolver el libro: {e}")
            return False

    def get_reviews_by_book_id(self, book_id):
        query = "SELECT * FROM Reviews WHERE book_id = ?"
        reviews = db.select(query, (book_id,))
        return reviews


    def get_review_by_id(self, review_id):
        query = "SELECT * FROM Reviews WHERE id = ?"
        review = db.select(query, (review_id,))
        return review[0] if len(review) > 0 else None


    def edit_review(self, review_id, rating, review_text):
        try:
            db.update("""
                      UPDATE Reviews
                      SET rating = ?, review_text = ?
                      WHERE id = ?
                  """, (rating, review_text, review_id,))
        except Exception as e:
            print(f"Error editando review: {e}")


    def delete_review(self, review_id):
        try:
            db.delete("""
                      DELETE FROM Reviews
                      WHERE id = ?
                  """, (review_id,))
        except Exception as e:
            print(f"Error borrando review: {e}")

            from flask import session





