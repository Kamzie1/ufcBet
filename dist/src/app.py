import pygame
from src.scraper import resolve
from src.UI import (
    Navbar,
    pozycja_myszy_na_surface,
    Pop_up,
    DisplayBets,
    NotificationObserver,
    Button,
)
from src.fight_card import Fight_Card

DEFAULT_EVENT_ID = 1286


class Player:
    def __init__(self) -> None:
        self.points = 1000.0
        self.light = {
            "font": "black",
            "screen": "white",
            "inactive": (126, 126, 126),
            "nav": "grey",
            "button1": "red",
            "button2": "blue",
            "button3": "green",
        }
        self.black = {
            "font": "white",
            "screen": "black",
            "inactive": (180, 180, 180),
            "nav": (126, 126, 126),
            "button1": "red",
            "button2": "blue",
            "button3": "green",
        }
        self._mode = True
        self.colors = self.light

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value:
            self.colors = self.light
        else:
            self.colors = self.black
        self._mode = value


class App:
    def __init__(self) -> None:
        pygame.init()
        self.width = 600
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))

        pygame.display.set_caption("UFC BET")
        self.url = "src/appData"
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.get_data_from_file()
        self.nav = Navbar(self.width, self.height, DEFAULT_EVENT_ID, self.player.colors)
        self.notify = NotificationObserver()
        self.pop_up = Pop_up(self.player.colors)
        self.pop_up.bets = self.group(
            self.file_data[2:],
        )
        self.update_bets()
        self.fights_box = pygame.Surface((self.width, self.height - 72))
        self.fights_box_rect = self.fights_box.get_frect(topleft=(0, 36))
        self.slide_height = len(self.nav.event_info["fights"]) * 80 + 30
        self.slide_surf = pygame.Surface((self.width, self.slide_height))
        self._offset = 0
        self.slide_rect = self.slide_surf.get_frect(topleft=(0, -self.offset))
        self.scroll_speed = 30
        self.fight_cards = pygame.sprite.Group()
        self.update_fight_cards()
        self.bet_box = pygame.Surface((self.width, self.height - 72))
        self.bet_box_rect = self.fights_box.get_frect(topleft=(0, 36))
        self._bet_slide_height = len(self.pop_up.bets) * 80 + 30
        self.bet_slide_surf = pygame.Surface((self.width, self.bet_slide_height))
        self._betOffset = 0
        self.bet_slide_rect = self.bet_slide_surf.get_frect(
            topleft=(0, -self.bet_offset)
        )
        self.display_bet = DisplayBets(self.width)
        self.set_color_mode = Button(
            (5, self.height - 31),
            50,
            20,
            self.player.colors["screen"],
            "Mode",
            self.player.colors["font"],
        )
        self.font = pygame.font.Font("src/consolas.ttf", 16)

    def update_bets(self):
        bets = self.pop_up.bets
        new_bets = []
        for bet in bets:
            if bet["resolved"]:
                new_bets.append(bet)
                continue
            result = resolve(bet["fight_id"], bet["fighter_id"])
            if result == 1:
                self.player.points += float(bet["value"])
                self.notify.create(bet, "WON", self.player.colors)
                bet["resolved"] = True
                bet["result"] = "WON"
            elif result == -1:
                self.notify.create(bet, "LOST", self.player.colors)
                bet["resolved"] = True
                bet["result"] = "LOST"
            new_bets.append(bet)
        self.pop_up.bets = new_bets

    def group(self, data):
        bets = []
        for idx in range(0, len(data), 8):
            bet = dict()
            bet["value"] = data[idx]
            bet["fighter"] = data[idx + 1]
            bet["fight_id"] = int(data[idx + 2])
            bet["fighter_id"] = int(data[idx + 3])
            bet["event"] = data[idx + 4]
            bet["date"] = data[idx + 5]
            bet["resolved"] = bool(int(data[idx + 6]))
            bet["result"] = data[idx + 7]
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

    @property
    def bet_offset(self):
        return self._betOffset

    @bet_offset.setter
    def bet_offset(self, value):
        if value < -self.bet_slide_height + self.width - self.scroll_speed:
            return
        if value > self.scroll_speed:
            return
        self._betOffset = value
        self.bet_slide_rect = self.bet_slide_surf.get_frect(
            topleft=(0, self._betOffset)
        )

    @property
    def bet_slide_height(self):
        return self._bet_slide_height

    @bet_slide_height.setter
    def bet_slide_height(self, value):
        self._bet_slide_height = value
        self.bet_slide_surf = pygame.Surface((self.width, self.bet_slide_height))

    def get_data_from_file(self):
        try:
            f = open(self.url, "r")
            self.file_data = f.read().split("|")[:-1]
            f.close()
        except:
            self.file_data = [1000, "1"]
        self.player.points = float(self.file_data[0])
        self.player.mode = bool(int(self.file_data[1]))

    def run(self):
        while True:
            self.event_handler()
            self.draw()

    def display_bets(self):
        self.bet_box.fill(self.player.colors["screen"])
        self.bet_slide_surf.fill(self.player.colors["screen"])
        for id, bet in enumerate(self.pop_up.bets):
            self.display_bet.draw(self.bet_slide_surf, bet, id, self.player.colors)

        self.bet_box.blit(self.bet_slide_surf, self.bet_slide_rect)
        self.screen.blit(self.bet_box, self.bet_box_rect)

    def draw(self):
        self.screen.fill(self.player.colors["inactive"])
        self.nav.draw(self.screen, self.player, self.player.colors)
        self.set_color_mode.draw(self.screen)
        if self.nav.show_bets:
            self.display_bets()
        else:
            self.display_fights()

        self.pop_up.draw(self.screen, self.player.colors)
        self.notify.draw(self.screen, self.player.colors)

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
                    if not self.nav.show_bets:
                        self.offset -= self.scroll_speed
                    else:
                        self.bet_offset -= self.scroll_speed
                elif event.y == 1:
                    if not self.nav.show_bets:
                        self.offset += self.scroll_speed
                    else:
                        self.bet_offset += self.scroll_speed
            mouse_pos = pygame.mouse.get_pos()
            self.notify.update(event, mouse_pos)
            self.pop_up.event(event, mouse_pos, self.player)
            self.nav.event(event, mouse_pos, self.update_bets)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.set_color_mode.rect.collidepoint(mouse_pos):
                    self.player.mode = not self.player.mode
                    self.refresh_colors()
                if self.fights_box_rect.collidepoint(mouse_pos):
                    mouse_pos = pozycja_myszy_na_surface(mouse_pos, (0, 36))
                    mouse_pos = pozycja_myszy_na_surface(mouse_pos, (0, self.offset))
                    for fight_card in self.fight_cards:
                        if fight_card.rect.collidepoint(mouse_pos):
                            fight_card.event(mouse_pos)
            if self.nav.updated_event_id:
                self.update_fight_cards()
                self.nav.updated_event_id = False
            if self.pop_up.updated_bets:
                self.bet_slide_height = len(self.pop_up.bets) * 80 + 30
                self.pop_up.updated_bets = False

    def refresh_colors(self):
        self.set_color_mode = Button(
            (5, self.height - 31),
            50,
            20,
            self.player.colors["screen"],
            "Mode",
            self.player.colors["font"],
        )
        self.nav.refresh_colors(self.player.colors)
        self.pop_up.refresh_colors(self.player.colors)
        self.notify.refresh_colors(self.player.colors)
        self.update_fight_cards()

    def update_fight_cards(self):
        for id, fight in enumerate(self.nav.event_info["fights"]):
            self.update_fight_card(id, fight)

    def save_to_file(self):
        with open(self.url, "w+") as f:
            f.write(str(self.player.points))
            f.write("|")
            f.write(str(int(self.player.mode)))
            f.write("|")
            for bet in self.pop_up.bets:
                f.write(str(bet["value"]))
                f.write("|")
                f.write(bet["fighter"])
                f.write("|")
                f.write(str(bet["fight_id"]))
                f.write("|")
                f.write(str(bet["fighter_id"]))
                f.write("|")
                f.write(str(bet["event"]))
                f.write("|")
                f.write(str(bet["date"]))
                f.write("|")
                f.write(str(int(bet["resolved"])))
                f.write("|")
                f.write(bet["result"])
                f.write("|")

    def display_fights(self):
        self.fights_box.fill(self.player.colors["screen"])
        self.slide_surf.fill(self.player.colors["screen"])

        display = (
            f" {self.nav.event_info["event"]}         {self.nav.event_info["date"]}"
        )
        text = self.font.render(display, True, self.player.colors["font"])
        text_rect = text.get_frect(bottomright=(self.width - 10, self.height - 10))
        self.screen.blit(text, text_rect)

        for fight_card in self.fight_cards:
            fight_card.draw(self.slide_surf, self.player.colors)

        self.fights_box.blit(self.slide_surf, self.slide_rect)
        self.screen.blit(self.fights_box, self.fights_box_rect)

    def update_fight_card(self, id, fight):
        Fight_Card(
            fight,
            id,
            self.width,
            self.fight_cards,
            self.nav.event_info["event"],
            self.player.colors,
        )


if __name__ == "__main__":
    app = App()
    app.run()
