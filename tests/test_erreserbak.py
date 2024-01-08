from . import BaseTestClass
from bs4 import BeautifulSoup


class TestErreserbaHistoria(BaseTestClass):

    def test_erabiltzailearen_historia_kontsultatu(self):
        # Erabiltzaile existentziatentzat erreserba-historia kontsultatu daitekeen egiaztatu
        erabiltzaile_izena = "Erabiltzaile1"
        res = self.client.get(f'/historia?erabiltzailea={erabiltzaile_izena}')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertGreater(len(page.find('div', class_='historia').find_all('div', class_='erreserba')), 0)

    def test_erabiltzailearen_historia_kontsultatu_erabiltzailea_ez_dagoenean(self):
        # Erabiltzaile ez dagoenean historia kontsultatu daitekeen egiaztatu
        erabiltzaile_izena = "ErabiltzaileEzDago"
        res = self.client.get(f'/historia?erabiltzailea={erabiltzaile_izena}')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(0, len(page.find('div', class_='historia').find_all('div', class_='erreserba')))

    def test_liburuaren_historia_kontsultatu(self):
        # Liburu existentziatentzat erreserba-historia kontsultatu daitekeen egiaztatu
        liburu_izena = "Liburu1"
        res = self.client.get(f'/historia?liburua={liburu_izena}')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertGreater(len(page.find('div', class_='historia').find_all('div', class_='erreserba')), 0)

    def test_liburuaren_historia_kontsultatu_liburua_ez_dagoenean(self):
        # Liburu ez dagoenean historia kontsultatu daitekeen egiaztatu
        liburu_izena = "LiburuEzDago"
        res = self.client.get(f'/historia?liburua={liburu_izena}')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(0, len(page.find('div', class_='historia').find_all('div', class_='erreserba')))

    def test_liburua_erreserbatu_ondo(self):
        # Egiaztatu liburua erreserbatu ahal dela
        liburu_izena = "LiburuErreserbatuAhal"
        erabiltzaile_izena = "Erabiltzailea1"

        # Liburua erreserbatu
        res = self.client.post(f'/erreserbatu/{liburu_izena}', data={'erabiltzailea': erabiltzaile_izena})
        self.assertEqual(200, res.status_code)

        # Liburutegiaren orrialdea eguneratu
        res = self.client.get('/catalogue')
        page = BeautifulSoup(res.data, features="html.parser")
        liburua_elementua = page.find('div', class_='card', string=liburu_izena)
        self.assertIsNotNone(liburua_elementua)

    def test_liburua_erreserbatu_ez_dagoen_libururik(self):
        # Egiaztatu ezin dela liburua erreserbatu ez dagoen libururik
        liburu_izena = "LiburuErreserbatuEz"
        erabiltzaile_izena = "Erabiltzailea1"

        # Liburua erreserbatu
        res = self.client.post(f'/erreserbatu/{liburu_izena}', data={'erabiltzailea': erabiltzaile_izena})
        self.assertEqual(200, res.status_code)

        # Ezin dela berriz erreserbatu
        res = self.client.post(f'/erreserbatu/{liburu_izena}', data={'erabiltzailea': erabiltzaile_izena})
        self.assertEqual(400, res.status_code)

    def test_liburua_itzuli_ondo(self):
        # Egiaztatu liburua ondo itzuli ahal dela
        liburu_izena = "LiburuErreserbatuAhal"
        erabiltzaile_izena = "Erabiltzailea1"

        # Liburua erreserbatu
        res = self.client.post(f'/erreserbatu/{liburu_izena}', data={'erabiltzailea': erabiltzaile_izena})
        self.assertEqual(200, res.status_code)

        # Liburua itzuli
        res = self.client.post(f'/itzuli/{liburu_izena}', data={'erabiltzailea': erabiltzaile_izena})
        self.assertEqual(200, res.status_code)

    def test_liburua_itzuli_erreserbatua_ez_dagoen_libururik(self):
        # Egiaztatu ezin dela liburua erreserbatua ez dagoen libururik itzuli
        liburu_izena = "LiburuErreserbatuEz"
        erabiltzaile_izena = "Erabiltzailea1"

        # Liburua itzuli
        res = self.client.post(f'/itzuli/{liburu_izena}', data={'erabiltzailea': erabiltzaile_izena})
        self.assertEqual(400, res.status_code)