from jinja2 import Undefined
from sqlalchemy.sql.functions import user

from .LibraryController import LibraryController
from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify, flash
from datetime import datetime

from model.Forua import Forua

app = Flask(__name__, static_url_path='', static_folder='../view/static', template_folder='../view/')

library = LibraryController()
forua = Forua()


@app.before_request
def get_logged_user():
    if '/css' not in request.path and '/js' not in request.path:
        token = request.cookies.get('token')
        time = request.cookies.get('time')
        if token and time:
            request.user = library.get_user_cookies(token, float(time))
            if request.user:
                request.user.token = token


@app.after_request
def add_cookies(response):
    if 'user' in dir(request) and request.user and request.user.token:
        session = request.user.validate_session(request.user.token)
        response.set_cookie('token', session.hash)
        response.set_cookie('time', str(session.time))
    return response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/catalogue')
def catalogue():
    title = request.values.get("title", "")
    author = request.values.get("author", "")
    page = int(request.values.get("page", 1))
    books, nb_books = library.search_books(title=title, author=author, page=page - 1)
    total_pages = (nb_books // 6) + 1
    return render_template('catalogue.html', books=books, title=title, author=author, current_page=page,
                           total_pages=total_pages, max=max, min=min)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in dir(request) and request.user and request.user.token:
        return redirect('/')
    email = request.values.get("email", "")
    password = request.values.get("password", "")
    user = library.get_user(email, password)
    if user:
        session = user.new_session()
        resp = redirect("/")
        resp.set_cookie('token', session.hash)
        resp.set_cookie('time', str(session.time))
    else:
        if request.method == 'POST':
            return redirect('/login')
        else:
            resp = render_template('login.html')
    return resp


@app.route('/logout')
def logout():
    path = request.values.get("path", "/")
    resp = redirect(path)
    resp.delete_cookie('token')
    resp.delete_cookie('time')
    if 'user' in dir(request) and request.user and request.user.token:
        request.user.delete_session(request.user.token)
        request.user = None
    return resp


@app.route('/profile')
def profile():
    if 'user' in dir(request) and request.user and request.user.token:
        user = request.user
        reserved_books = library.get_reserved_books(user.email)
        read_books = library.get_read_books(user.email)
        reviews = library.get_reviews_by_user(user.email)
        return render_template('profile.html', user=user, library=library, reserved_books=reserved_books,
                               read_books=read_books, reviews=reviews)
    else:
        return redirect('/login')


@app.route('/return-book')
def return_book():
    if 'user' in dir(request) and request.user and request.user.token:
        book_id = request.args.get('bookId')
        result = library.return_book(book_id, request.user.email)

        if result:
            return redirect('/profile')
        else:
            return redirect('/profile')

    else:
        return redirect('/login')


@app.route('/addreview')
def review():
    if 'user' not in dir(request) or not request.user or not request.user.token:
        return redirect('/login')

    book_id = request.args.get('bookId', type=int)
    book = library.search_book_by_id(book_id)
    read_books = library.get_read_books(request.user.email)

    return render_template('addreview.html', user=request.user, book=book, read_books=read_books)

@app.route('/lagun_sarea')
def mostrar_lagunak():
    return render_template('laguna.html')


@app.route('/post-review', methods=['POST'])
def post_review():
    try:
        data = request.json
        book_id = data['book_id']
        rating = data['rating']
        review_text = data['review_text']
        title = data['title']
        user_email = request.user.email

        print(f"Received review: book_id={book_id}, rating={rating}, review_text={review_text}, title={title}, user_email={user_email}")

        success = library.save_review(user_email=user_email, book_id=book_id, title=title, rating=rating, review_text=review_text)

        if success:
            return jsonify({'success': True, 'message': 'Review saved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Review already exists for this user and book'})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Error saving review'})


@app.route('/read-reviews')
def read_reviews():
    bookId = request.args.get('bookId', type=int)
    book = library.search_book_by_id(bookId)
    reviews = library.get_reviews_by_book_id(bookId)

    print(f"Reviews for bookId={bookId}: {reviews}")

    return render_template('profile.html', user=request.user, reviews=reviews, book=book)


@app.template_filter('formatdatetime')
def format_datetime(value):
    if value is not Undefined and isinstance(value, str):
        datetime_object = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return datetime_object.strftime('%B %d %Y, %H:%M:%S')
    else:
        return "Undefined"


@app.route('/edit-review', methods=['GET', 'POST'])
def edit_review():
    review_id = request.args.get('reviewId')
    if request.method == 'GET':
        review_data = library.get_review_by_id(review_id)
        if review_data is None:
            rating = None
            review_text = None
        else:
            rating = review_data[3] if len(review_data) > 3 else None
            review_text = review_data[4] if len(review_data) > 4 else None
            review_id = review_data[0] if len(review_data) > 0 else None
        return render_template('edit_review.html', review=review_data, rating=rating, review_text=review_text, review_id=review_id)

    elif request.method == 'POST':
        review_id = request.json.get('review_id')
        print(review_id)
        updated_rating = request.json.get('rating')
        updated_review_text = request.json.get('review_text')
        library.edit_review(review_id, updated_rating, updated_review_text)
        return redirect(url_for('profile'))


@app.route('/delete-review')
def delete_review():
    reviewId = request.args.get('reviewId', type=int)
    review = library.get_review_by_id(reviewId)
    library.delete_review(reviewId)
    return redirect(url_for('read_reviews', bookId=review[1]))


@app.route('/update-review', methods=['POST'])
def update_review():
    data = request.form
    review_id = data.get('review_id')
    updated_rating = data.get('updated_rating')
    updated_review_text = data.get('updated_review_text')
    library.update_review(review_id, updated_rating, updated_review_text)
    return redirect(url_for('profile'))


@app.route('/reserve-book', methods=['GET'])
def reserve_book():
    book_id = request.args.get('bookId')
    if 'user' not in dir(request) or not request.user or not request.user.token:
        return redirect('/login')
    result = library.reserve_book(book_id, request.user.email)

    if result:
        return redirect('/catalogue')
    else:
        return redirect('/catalogue')


@app.route('/mostrar_foro')
def mostrar_foro():
    gaiak = forua.obtener_gaiak()
    return render_template('Forua.html', gaiak=gaiak)


@app.route('/crear_gaia', methods=['POST'])
def crear_gaia():
    if 'user' in dir(request) and request.user and request.user.token:
        titulo = request.form['titulo']
        contenido = request.form['contenido']
        autor = request.user.username

        nuevo_gaia = forua.crear_gaia(titulo, contenido, autor)
        return redirect('/mostrar_foro')
    else:
        return redirect('/login')


@app.route('/comentar_gaia/<titulo>', methods=['GET', 'POST'])
def comentar_gaia(titulo):
    if request.method == 'POST':
        contenido = request.form.get('contenido')
        if 'user' in dir(request) and request.user and request.user.token:
            autor = request.user.username
            gaia = forua.obtener_gaiak_por_titulo(titulo)
            if gaia:
                nuevo_comentario = forua.comentar(gaia, contenido, autor)
                return redirect(url_for('comentar_gaia', titulo=titulo, nuevo_comentario_id=nuevo_comentario.id, gaia=gaia))
            else:
                flash('Tema no encontrado.', 'error')
                return redirect('/mostrar_foro')
        else:
            return redirect('/login')

    elif request.method == 'GET':
        gaia = forua.obtener_gaiak_por_titulo(titulo)
        return render_template('foruaKomentatu.html', gaia=gaia)


@app.route('/comentar_gaia/<titulo>', methods=['POST'])
def comentar_gaia_post(titulo):
    contenido = request.form['contenido']
    autor = request.user.username
    if 'user' in dir(request) and request.user and request.user.token:
        gaia = forua.obtener_gaiak_por_titulo(titulo)
        if gaia:
            nuevo_comentario = forua.comentar(gaia, contenido, autor)
            return redirect(url_for('comentar_gaia', titulo=titulo, nuevo_comentario_id=nuevo_comentario.id))
        else:
            flash('Tema no encontrado.', 'error')
            return redirect('/mostrar_foro')
    else:
        return redirect('/login')



@app.route('/crear_gaia', methods=['GET'])
def formulario_crear_gaia():
    return render_template('foruaGaiaSortu.html')

@app.route('/mostrar_gomendio')
def mostrar_gomendio():
    if 'user' in dir(request) and request.user and request.user.token:
        user = request.user
        unread_books = library.get_unread_books(user.email)

        return render_template('Gomendioak.html', user=user, library=library,
                               unread_books=unread_books)
    else:
        return redirect('/login')

@app.route('/mostrar_admin')
def mostrar_admin():
    if 'user' in dir(request) and request.user and request.user.token:
        # Verifica si el usuario es administrador utilizando el método isAdmin
        if request.user.isNotAdmin():
            # Si el usuario es administrador, muestra la página de administrador
            return render_template('/index.html')
        else:
            return render_template('administratzaile.html')
    else:
        # Si no hay usuario autenticado, redirige a la página de inicio de sesión
        return redirect('/login')

@app.route('/gehituErabiltzaile')
def gehituErabiltzaile():
    if 'user' in dir(request) and request.user and request.user.token:
        return render_template('gehituErabiltzaile.html')
    else:
        # Si no hay usuario autenticado, redirige a la página de inicio de sesión
        return redirect('/login')
@app.route('/ezabatuErabiltzaile')
def ezabatuErabiltzaile():
    if 'user' in dir(request) and request.user and request.user.token:
        return render_template('ezabatuErabiltzaile.html')
    else:
        return redirect('/login')
@app.route('/sartuLiburua')
def sartuLiburua():
    return render_template('sartuLiburua.html')