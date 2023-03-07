# grafu atveju:
# virsune = konkreti busena, zaidimo konfiguracija
# briauna = veiksmas, kuri veda i kita busena(virsune)
# briauna turi tureti savo svori, kiek ji yra "gera"

# kaip keisti zaidima
# konteinerio dydis (siuo metu yra 28)
# tikslas surinkti 10 linijoje
# ar keisti chip reiksmes


class Vertex:
    def __init__(self, state, value):
        self.state = state
        self.value = value
        self.next_states = []  # o kaip mes tai gaunam?
        # paieska i ploti
        # arba vykdyti episodus

