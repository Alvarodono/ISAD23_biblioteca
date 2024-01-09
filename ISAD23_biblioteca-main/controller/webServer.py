from .LibraryController import LibraryController
from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from datetime import datetime

from model.Forua import Forua

app = Flask(__name__, static_url_path='', static_folder='../view/static', template_folder='../view/')

library = LibraryController()
forua = Forua()  # Crear una instancia de la clase Forua


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

        # Llama a la función de LibraryController para devolver el libro y almacenar la lectura
        result = library.return_book(book_id, request.user.email)

        if result:
            # La devolución fue exitosa, puedes redirigir a alguna página de confirmación o a la lista de libros devueltos.
            return redirect('/profile')
        else:
            # Maneja el caso en que la devolución no fue exitosa.
            return redirect('/profile')  # Puedes redirigir a la página de perfil u otra según tus necesidades.

    else:
        return redirect('/login')


@app.route('/addreview')
def review():
    if 'user' not in dir(request) or not request.user or not request.user.token:
        return redirect('/login')  # Redirige a la página de inicio de sesión si el usuario no está autenticado

    book_id = request.args.get('bookId', type=int)
    book = library.search_book_by_id(book_id)

    # Obtiene la lista de libros leídos del usuario
    read_books = library.get_read_books(request.user.email)

    return render_template('addreview.html', user=request.user, book=book, read_books=read_books)

@app.route('/lagun_sarea')
def mostrar_lagunak():
    return render_template('laguna.html')


# En tu aplicación Flask (webServer.py)
@app.route('/post-review', methods=['POST'])
def post_review():
    try:
        data = request.json
        book_id = data['book_id']
        rating = data['rating']
        review_text = data['review_text']
        title = data['title']  # Asegúrate de que estás recibiendo el título desde la solicitud JSON

        # Guarda la revisión usando tu controlador
        library.save_review(user_email=request.user.email, book_id=book_id, title=title, rating=rating,
                            review_text=review_text)

        return jsonify({'success': True, 'message': 'Review saved successfully'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Error saving review'})


@app.route('/read-reviews')
def read_reviews():
    bookId = request.args.get('bookId', type=int)
    book = library.search_book_by_id(bookId)
    reviews = library.get_reviews_by_book_id(bookId)
    return render_template('profile.html', reviews=reviews, book=book)


@app.template_filter('formatdatetime')
def format_datetime(value):
    if value is None:
        return ""

    datetime_object = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    return datetime_object.strftime('%B %d %Y, %H:%M:%S')


@app.route('/edit-review', methods=['GET', 'POST'])
def edit_review():
    review_id = request.args.get('reviewId')
    if request.method == 'GET':
        # Aquí obtienes el reviewId de la URL

        # Lógica para obtener la revisión de la base de datos según review_id
        # Puedes usar una función similar a get_review_by_id(review_id)
        review_data = library.get_review_by_id(review_id)  # Asegúrate de implementar esta función

        # Verifica si review_data es None
        if review_data is None:
            rating = None
            review_text = None
        else:
            # Asumo que el rating está en el índice 3 de la tupla o lista, ajusta esto según la estructura real de tus datos
            rating = review_data[3] if len(review_data) > 3 else None
            # Asumo que el review_text está en el índice 4 de la tupla o lista, ajusta esto según la estructura real de tus datos
            review_text = review_data[4] if len(review_data) > 4 else None
            review_id = review_data[0] if len(review_data) > 0 else None

        # Renderiza el formulario de edición con los datos de la revisión
        return render_template('edit_review.html', review=review_data, rating=rating, review_text=review_text, review_id=review_id)

    elif request.method == 'POST':
        review_id = request.json.get('review_id')
        print(review_id)
        # Aquí obtienes los datos actualizados del formulario
        updated_rating = request.json.get('rating')
        updated_review_text = request.json.get('review_text')

        # Lógica para actualizar la revisión en la base de datos
        # Puedes usar una función similar a update_review(review_id, updated_rating, updated_review_text)
        library.edit_review(review_id, updated_rating, updated_review_text)  # Asegúrate de implementar esta función

        # Redirige a la página de perfil después de la edición
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

    # Lógica para actualizar la revisión en la base de datos
    # Puedes usar una función similar a update_review(review_id, updated_title, updated_rating, updated_review_text)
    library.update_review(review_id, updated_rating, updated_review_text)  # Asegúrate de implementar esta función

    # Redirige a la página de perfil después de la edición
    return redirect(url_for('profile'))


@app.route('/reserve-book', methods=['GET'])
def reserve_book():
    # Obtiene el ID del libro desde los parámetros de la URL
    book_id = request.args.get('bookId')

    # Verifica si el usuario está autenticado
    if 'user' not in dir(request) or not request.user or not request.user.token:
        return redirect('/login')  # Redirige a la página de inicio de sesión si el usuario no está autenticado

    # Llama a la función de LibraryController para reservar el libro para el usuario actual
    result = library.reserve_book(book_id, request.user.email)

    if result:
        # La reserva fue exitosa, puedes redirigir a alguna página de confirmación o a la lista de libros reservados.
        return redirect('/catalogue')
    else:
        # Maneja el caso en el que la reserva no fue exitosa.
        return redirect('/catalogue')  # Puedes redirigir a la página de catálogo u otra según tus necesidades.


@app.route('/mostrar_foro')
def mostrar_foro():
    gaiak = forua.obtener_gaiak()
    return render_template('Forua.html', gaiak=gaiak)


@app.route('/crear_gaia', methods=['POST'])
def crear_gaia():
    # Verifica si hay un usuario autenticado
    if 'user' in dir(request) and request.user and request.user.token:
        titulo = request.form['titulo']
        contenido = request.form['contenido']
        autor = request.user.username  # Asegúrate de obtener el autor de la sesión actual

        nuevo_gaia = forua.crear_gaia(titulo, contenido, autor)
        return redirect('/mostrar_foro')
    else:
        # Si no hay usuario autenticado, redirige a la página de inicio de sesión
        return redirect('/login')  # Reemplaza '/login' con la ruta correcta hacia tu página de inicio de sesión


@app.route('/comentar_gaia/<titulo>', methods=['GET', 'POST'])
def comentar_gaia(titulo):
    if request.method == 'POST':
        contenido = request.form.get('contenido')


        # Verifica si hay un usuario autenticado
        if 'user' in dir(request) and request.user and request.user.token:
            autor = request.user.username
            gaia = forua.obtener_gaiak_por_titulo(titulo)
            if gaia:
                nuevo_comentario = forua.comentar(gaia, contenido, autor)  # Pasa el objeto gaia como primer argumento

                # Pasa el ID del nuevo comentario como parámetro en la URL de la redirección
                return redirect(url_for('comentar_gaia', titulo=titulo, nuevo_comentario_id=nuevo_comentario.id, gaia=gaia))
            else:
                flash('Tema no encontrado.', 'error')
                return redirect('/mostrar_foro')
        else:
            # Si no hay usuario autenticado, redirige a la página de inicio de sesión
            return redirect('/login')  # Reemplaza '/login' con la ruta correcta hacia tu página de inicio de sesión

    elif request.method == 'GET':
        gaia = forua.obtener_gaiak_por_titulo(titulo)
        # Lógica para manejar las solicitudes GET, si es necesario
        return render_template('foruaKomentatu.html', gaia=gaia)  # Pasa gaia como contexto para la plantilla


@app.route('/comentar_gaia/<titulo>', methods=['POST'])
def comentar_gaia_post(titulo):
    contenido = request.form['contenido']
    autor = request.user.username

    # Verifica si hay un usuario autenticado
    if 'user' in dir(request) and request.user and request.user.token:
        gaia = forua.obtener_gaiak_por_titulo(titulo)
        if gaia:
            nuevo_comentario = forua.comentar(gaia, contenido, autor)  # Pasa el objeto gaia como primer argumento

            # Pasa el ID del nuevo comentario como parámetro en la URL de la redirección
            return redirect(url_for('comentar_gaia', titulo=titulo, nuevo_comentario_id=nuevo_comentario.id))
        else:
            flash('Tema no encontrado.', 'error')
            return redirect('/mostrar_foro')
    else:
        # Si no hay usuario autenticado, redirige a la página de inicio de sesión
        return redirect('/login')  # Reemplaza '/login' con la ruta correcta hacia tu página de inicio de sesión



@app.route('/crear_gaia', methods=['GET'])
def formulario_crear_gaia():
    return render_template('foruaGaiaSortu.html')

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

