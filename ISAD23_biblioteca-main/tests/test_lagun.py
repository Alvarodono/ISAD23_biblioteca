import unittest

class testLagun(unittest.TestCase):
    def setUp(self):
        self.laguna1 = self.Laguna("Aingeru", "El lobo estepario", "4 izar", "Ez dago info. gehigarririk.")
        self.laguna2 = self.Laguna("Álvaro", "Cordeluna", "3 izar", "Ez dago info. gehigarririk.")
        self.laguna3 = self.Laguna("Yeray", "La casa de los espíritus", "5 izar", "Ez dago info. gehigarririk.")

        self.lagunak = {"Aingeru": self.laguna1, "Álvaro": self.laguna2, "Yeray": self.laguna3}

    def test_eskaera_bidali(self):
        self.laguna1.eskaera_bidali(self.laguna2)
        self.assertIn("laguna2", self.laguna2.eskaerak)

    def test_eskaera_erakutsi(self):
        self.laguna1.eskaera_bidali(self.laguna2)
        self.laguna1.eskaera_bidali(self.laguna3)
        self.assertEqual(len(self.laguna2.eskaerak), 1)
        self.assertEqual(len(self.laguna2.eskaerak), 1)

    def test_eskaerak_onartu(self):
        self.laguna1.eskaera_bidali(self.laguna2)
        self.laguna2.eskaera_onartu(self.laguna1)
        self.assertNotIn("Aingeru", self.laguna2.eskaerak)
        self.assertIn("Aingeru", self.laguna2.lagunak)  

    def test_nonexistent_eskaerak_onartu(self):
        self.laguna1.eskaera_onartu(self.laguna2)
        self.assertNotIn("Álvaro", self.laguna1.lagunak)

if __name__ == "__main__":
    unittest.main()
