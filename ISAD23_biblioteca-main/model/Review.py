from .Connection import Connection
from .Author import Author
from .Book import Book

db = Connection()


class Review:
    def __init__(self, id, book_id, user_email, date_time, rating, review_text):
        self.id = id
        self.book_id = book_id
        self.user_email = user_email
        self.date_time = date_time
        self.rating = rating
        self.review_text = review_text
        self.title = self.get_book_title()

    def get_book_title(self):
        book = db.query_one("SELECT title FROM Book WHERE id = ?", (self.book_id,))
        if book:
            return book['title']
        else:
            return None

