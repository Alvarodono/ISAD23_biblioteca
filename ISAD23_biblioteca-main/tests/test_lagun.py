from . import BaseTestClass
from bs4 import BeautifulSoup

class TestLagun(BaseTestClass):

    def testEskaeraBidali(self):
        self.login('user1@example.com', 'password')

        res = self.client.post('/eskaera_bidali/2')

        self.assertEqual(200, res.status_code)
        self.assertIn('Friend request sent successfully', res.get_data(as_text=True))

    def testEskaeraJaso(self):
        self.login('user2@example.com', 'password')

        res = self.client.get('/eskaerak_erakutsi')

        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertIsNotNone(page.find('div', class_='friend-request'))

    def testEskaeraOnartu(self):
        self.login('user2@example.com', 'password')

        res = self.client.post('/eskaera_onartu/1')

        self.assertEqual(200, res.status_code)
        self.assertIn('Eskaera onartu da.', res.get_data(as_text=True))

    def testEskaeraErrefusatu(self):
        self.login('user2@example.com', 'password')

        res = self.client.post('/eskaera-errefusatu/3')

        self.assertEqual(200, res.status_code)
        self.assertIn('Eskaera errefusatu da.', res.get_data(as_text=True))

    def testLagunZerrendaIkusi(self):
        self.login('user1@example.com', 'password')

        res = self.client.get('/lagunak')

        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertIsNotNone(page.find('div', class_='friends-list'))



