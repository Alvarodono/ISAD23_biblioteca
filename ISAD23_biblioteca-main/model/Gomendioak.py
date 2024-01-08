from .Connection import Connection
from .Author import Author
from .Book import Book

db = Connection()


class Gomendioak:
    def __init__(self, id, book_id, user_email):
        self.id = id
        self.book_id = book_id
        self.user_email = user_email
        self.title = self.get_book_title()

    def get_book_title(self):
        book = db.query_one("SELECT title FROM Book WHERE id = ?", (self.book_id,))
        if book:
            return book['title']
        else:
            return None

