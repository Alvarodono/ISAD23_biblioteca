from .Connection import Connection

db = Connection()

class Forua:
    def __init__(self):
        self.gaiak = []

    def crear_gaia(self, titulo, contenido, autor):
        nuevo_gaia = self.Gaia(titulo, contenido, autor)
        self.gaiak.append(nuevo_gaia)
        return nuevo_gaia

    def obtener_gaiak(self):
        return self.gaiak

    def obtener_gaiak_por_titulo(self, titulo):
        for gaia in self.gaiak:
            if gaia.titulo == titulo:
                return gaia
        return None

    def comentar(self, gaia, contenido, autor):
        nuevo_comentario = self.Comentario(contenido, autor)
        gaia.comentarios.append(nuevo_comentario)
        return nuevo_comentario

    def comentar_comentario(self, comentario_id, contenido, autor):
        comentario_padre = self.obtener_comentario_por_id(comentario_id)
        nuevo_comentario = self.Comentario(contenido, autor)
        comentario_padre.comentarios.append(nuevo_comentario)
        return nuevo_comentario

    def obtener_comentario_por_id(self, comentario_id):
        for gaia in self.gaiak:
            for comentario in gaia.obtener_comentarios():
                if comentario.id == comentario_id:
                    return comentario
        return None

    class Comentario:
        contador_comentarios = 0

        def __init__(self, contenido, autor):
            Forua.Comentario.contador_comentarios += 1
            self.id = Forua.Comentario.contador_comentarios
            self.contenido = contenido
            self.autor = autor

    class Gaia:
        def __init__(self, titulo, contenido, autor):
            self.titulo = titulo
            self.contenido = contenido
            self.autor = autor
            self.comentarios = []

        def obtener_comentarios(self):
            return self.comentarios
