class Laguna:
    def __init__(self, izena, erreserba, erreseina, infoGehigarria):
        self.izena = izena
        self.erreserba = erreserba
        self.erreseina = erreseina
        self.infoGehigarria = infoGehigarria
        self.eskaerak= []

    def profila_ikusi(self):
        print(f"Izena: {self.izena}")
        print(f"Erreserbak: {self.erreserba}")
        print(f"Erreseinak: {self.erreseina}")
        print(f"Info. gehigarria: {self.infoGehigarria}")
        print("\n")

    def eskaera_bidali(self, lagun_helmuga):
        lagun_helmuga.eskaerak.append(self.izena)
        print(f"Solicitud de amistad enviada a {lagun_helmuga.izena}.")

    def eskaerak_erakutsi(self):
        if self.eskaerak:
            print("Lagun izateko eskaerak:")
            for eskaera in self.eskaerak:
                print(f"- {eskaera}")
        else:
            print("Ez dauzkazu lagun izateko eskaerarik.")

    def eskaera_onartu(self, lagun_eskatzaile):
        if lagun_eskatzaile.izena in self.eskaerak:
            self.eskaerak.remove(lagun_eskatzaile.izena)
            print(f"{lagun_eskatzaile.izena}ren eskaera onartu duzu. Lagunak zarete orain.")
        else:
            print(f"{lagun_eskatzaile.izena}ek ez du eskaerarik bidali.")


def main():
    # Lagun batzuk sortu
    laguna1 = Laguna("Oihan", "El lobo estepario", "4 izar", "Ez dago info. gehigarririk.")
    laguna2 = Laguna("Unai", "Cordeluna", "3 izar", "Ez dago info. gehigarririk.")
    laguna3 = Laguna("Iker", "La casa de los espíritus", "5 izar", "Ez dago info. gehigarririk.")

    # Lagunak gorde
    lagunak = {"Oihan": laguna1, "Unai": laguna2, "Iker": laguna3}

    # Lagunen profilak ikusi
    while True:
        print("Lagunen zerrenda:")
        for izena_lagun in lagunak:
            print(f"- {izena_lagun}")

        izena_lagun_aukeratuta = input("\nZure lagunaren izena idatzi (edo 'irten' bukatzeko): ").lower()

        if izena_lagun_aukeratuta == 'irten':
            break

        if izena_lagun_aukeratuta in lagunak:
            lagun_aukeratuta = lagunak[izena_lagun_aukeratuta]
            lagun_aukeratuta.profila_ikusi()

            bidali = input("Eskaeraren bat bidali nahi duzu? (bai/ez): ").lower()
            if bidali == 'bai':
                lagun_aukeratuta.eskaera_bidali(laguna1) 
                lagun_aukeratuta.eskaerak_erakutsi()

            onartu = input("Eskaeraren bat onartu nahi duzu? (bai/ez): ").lower()
            if onartu == 'bai':
                lagun_aukeratuta.eskaerak_erakutsi()
                izen_eskatzaile = input("Onartu nahi duzun lagunaren izena idatzi: ").capitalize()
                if izen_eskatzaile in lagunak:
                    lagun_eskatzaile = lagunak[izen_eskatzaile]
                    lagun_aukeratuta.eskaera_onartu(lagun_eskatzaile)
                else:
                    print("Amigo no encontrado.")
        else:
            print("Laguna ez da aurkitu. Saiatu berriro.\n")


if __name__ == "__main__":
    main()

