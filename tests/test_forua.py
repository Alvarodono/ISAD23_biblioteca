from . import BaseTestClass
from bs4 import BeautifulSoup
from model.Forua import Forua

class TestForua(BaseTestClass):

    def test_consultar_temas(self):
        # Accede a la página que muestra la lista de temas en el foro
        res = self.client.get('/mostrar_foro')

        # Verifica que la página carga correctamente (código de estado 200)
        self.assertEqual(200, res.status_code)

    def test_visualizar_comentarios(self):
        # Asegúrate de que haya al menos un tema en el foro
        gaia_title = 'Proba'
        forua_instance = Forua()  # Crea una instancia de Forua
        gaia = forua_instance.obtener_gaiak_por_titulo(titulo=gaia_title)

        if gaia is None:
            # Si no existe, crea un tema de prueba
            gaia = forua_instance.crear_gaia(gaia_title, "Contenido de prueba", "Autor de prueba")

        # Accede a la página que muestra los comentarios de un tema específico
        res = self.client.get(f'/comentar_gaia/{gaia_title}')

        # Verifica que la página carga correctamente (código de estado 200)
        self.assertEqual(200, res.status_code)

        # Verifica que el gaia se ha creado correctamente
        self.assertIsNotNone(gaia)

        self.assertTrue(gaia.obtener_comentarios())

    def test_escribir_comentario(self):
        # Supongamos que el título del tema es 'Proba'
        gaia_title = 'Proba'

        # Asegúrate de que haya al menos un tema en el foro
        forua_instance = Forua()  # Crea una instancia de Forua
        gaia = forua_instance.obtener_gaiak_por_titulo(titulo=gaia_title)

        if gaia is None:
            # Si no existe, crea un tema de prueba
            gaia = forua_instance.crear_gaia(gaia_title, "Contenido de prueba", "Autor de prueba")

        # Autentica al usuario (puedes usar el método de autenticación que tengas en tu aplicación)
        self.login('james@gmail.com', '123456')

        # Accede a la página para comentar en un tema específico
        res = self.client.get(f'/comentar_gaia/{gaia_title}')

        # Verifica que la página carga correctamente (código de estado 200)
        self.assertEqual(200, res.status_code)

        # Simula el envío de un formulario para agregar un comentario
        comentario_contenido = 'Komentario proba'
        res = self.client.post(f'/comentar_gaia/{gaia_title}', data={'contenido': comentario_contenido})

        # Verifica que el comentario se ha agregado correctamente (código de estado 302 o el que utilices para redirecciones)
        self.assertEqual(302, res.status_code)
