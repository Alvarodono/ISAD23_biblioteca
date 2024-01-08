import datetime
from .Connection import Connection
from .tools import hash_password


from sqlalchemy.orm import relationship

db = Connection()

class Session:
	def __init__(self, hash, time):
		self.hash = hash
		self.time = time

	def __str__(self):
		return f"{self.hash} ({self.time})"



class UserReservedBook:
    def __init__(self, id, user_email, book_id):
        self.id = id
        self.user_email = user_email
        self.book_id = book_id



class User:
	def __init__(self, id, username, email):
		self.id = id
		self.username = username
		self.email = email

	def __str__(self):
		return f"{self.username} ({self.email})"

	def get_reserved_books(self):
		query = "SELECT * FROM User_Reserved_Book WHERE user_email = ?"
		reserved_books_data = db.select(query, (self.email,))

		reserved_books = []
		for data in reserved_books_data:
			reserved_book = UserReservedBook(data['id'], data['user_email'], data['book_id'])
			reserved_books.append(reserved_book)

		return reserved_books

	def new_session(self):
		now = float(datetime.datetime.now().time().strftime("%Y%m%d%H%M%S.%f"))
		session_hash = hash_password(str(self.id)+str(now))
		db.insert("INSERT INTO Session VALUES (?, ?, ?)", (session_hash, self.id, now))
		return Session(session_hash, now)

	def validate_session(self, session_hash):
		s = db.select("SELECT * from Session WHERE user_id = ? AND session_hash = ?", (self.id, session_hash))
		if len(s) > 0:
			now = float(datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f"))
			session_hash_new = hash_password(str(self.id) + str(now))
			db.update("UPDATE Session SET session_hash = ?, last_login=? WHERE session_hash = ? and user_id = ?", (session_hash_new, now, session_hash, self.id))
			return Session(session_hash_new, now)
		else:
			return None

	def delete_session(self, session_hash):
		db.delete("DELETE FROM Session WHERE session_hash = ? AND user_id = ?", (session_hash, self.id))