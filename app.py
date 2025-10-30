import pygame
from scraper import get_best_fight_odds
from UI import Navbar, pozycja_myszy_na_surface, Pop_up
from fight_card import Fight_Card


class Player:
    def __init__(self, points) -> None:
        self.points = points


class App:
    def __init__(self) -> None:
        pygame.init()
        self.width = 600
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("UFC BET")
        self.clock = pygame.time.Clock()
        self.fights = get_best_fight_odds()
        self.url = "appData"
        self.get_data_from_file()
        self.nav = Navbar(self.width, self.height)
        self.fights_box = pygame.Surface((self.width, self.height - 36))
        self.fights_box_rect = self.fights_box.get_frect(topleft=(0, 36))
        self.slide_height = len(self.fights) * 80 + 30
        self.slide_surf = pygame.Surface((self.width, self.slide_height))
        self._offset = 0
        self.slide_rect = self.slide_surf.get_frect(topleft=(0, -self.offset))
        self.scroll_speed = 30
        self.fight_cards = pygame.sprite.Group()
        self.update_fight_cards()
        self.pop_up = Pop_up()
        self.pop_up.bets = self.group(self.file_data[1:])

    def group(self, data):
        bets = []
        print(data)
        for idx in range(0, len(data), 2):
            bet = dict()
            bet["value"] = data[idx]
            bet["fighter"] = data[idx + 1]
            bets.append(bet)
        return bets

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        if value < -self.slide_height + self.width - self.scroll_speed:
            return
        if value > self.scroll_speed:
            return
        self._offset = value
        self.slide_rect = self.slide_surf.get_frect(topleft=(0, self._offset))

    def get_data_from_file(self):
        try:
            f = open(self.url, "r")
            self.file_data = f.read().split("|")[:-1]
            f.close()
        except:
            f = open(self.url, "w+")
            f.write("1000|")
            self.file_data = [1000]
            f.close()
        self.player = Player(float(self.file_data[0]))

    def run(self):
        while True:
            self.event_handler()
            self.draw()

    def draw(self):
        self.screen.fill("white")

        self.nav.draw(self.screen, self.player)
        self.display_fights()
        self.pop_up.draw(self.screen)

        pygame.display.update()
        self.clock.tick(60)

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_to_file()
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEWHEEL:
                if event.y == -1:
                    self.offset -= self.scroll_speed
                elif event.y == 1:
                    self.offset += self.scroll_speed
            mouse_pos = pygame.mouse.get_pos()
            self.pop_up.event(event, mouse_pos, self.player)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.fights_box_rect.collidepoint(mouse_pos):
                    mouse_pos = pozycja_myszy_na_surface(mouse_pos, (0, 36))
                    mouse_pos = pozycja_myszy_na_surface(mouse_pos, (0, self.offset))
                    for fight_card in self.fight_cards:
                        if fight_card.rect.collidepoint(mouse_pos):
                            fight_card.event(mouse_pos)

    def save_to_file(self):
        with open(self.url, "w+") as f:
            f.write(str(self.player.points))
            f.write("|")
            for bet in self.pop_up.bets:
                f.write(str(bet["value"]))
                f.write("|")
                f.write(bet["fighter"])
                f.write("|")

    def update_fight_cards(self):
        for id, fight in enumerate(self.fights):
            self.update_fight_card(id, fight)

    def display_fights(self):
        self.fights_box.fill("green")
        self.slide_surf.fill("yellow")

        for fight_card in self.fight_cards:
            fight_card.draw(self.slide_surf)

        self.fights_box.blit(self.slide_surf, self.slide_rect)
        self.screen.blit(self.fights_box, self.fights_box_rect)

    def update_fight_card(self, id, fight):
        Fight_Card(fight, id, self.width, self.fight_cards)


if __name__ == "__main__":
    app = App()
    app.run()
