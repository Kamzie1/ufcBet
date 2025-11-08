import pygame
from src.singleton import Singleton
from src.utils import is_number
from src.scraper import edited_ufc_odds


class Navbar:
    def __init__(self, width, height, DEFAULT_EVENT_ID, colors) -> None:
        self.width = width
        self.height = height
        self.surf = pygame.Surface((width, 36))
        self.rect = self.surf.get_frect(topleft=(0, 0))
        self.font = pygame.font.Font("src/consolas.ttf", 26)
        self.show_bets = False
        self.updated_event_id = False
        self._event_id = DEFAULT_EVENT_ID
        self.DEFAULT_EVENT_ID = DEFAULT_EVENT_ID
        self.fights_button = Button(
            (5, 5), 80, 26, colors["button2"], "Fights", colors["font"]
        )
        self.bets_button = Button(
            (90, 5), 80, 26, colors["button1"], "Bets", colors["font"]
        )
        self.refresh_button = Button(
            (175, 5), 80, 26, colors["button3"], "refresh", colors["font"]
        )
        self.event_input = Input(
            100, 26, (300, 5), colors["inactive"], colors["font"], "Event Id", 16
        )
        self.view_button = Button(
            (405, 5), 80, 26, colors["button1"], "Szukaj", colors["font"]
        )
        self.event_info = edited_ufc_odds(self.event_id)

    def refresh_colors(self, colors):
        self.fights_button = Button(
            (5, 5), 80, 26, colors["button2"], "Fights", colors["font"]
        )
        self.bets_button = Button(
            (90, 5), 80, 26, colors["button1"], "Bets", colors["font"]
        )
        self.refresh_button = Button(
            (175, 5), 80, 26, colors["button3"], "refresh", colors["font"]
        )
        self.event_input = Input(
            100, 26, (300, 5), colors["inactive"], colors["font"], "Event Id", 16
        )
        self.view_button = Button(
            (405, 5), 60, 26, colors["button1"], "Szukaj", colors["font"]
        )

    @property
    def event_id(self):
        return self._event_id

    @event_id.setter
    def event_id(self, value):
        if is_number(value):
            self._event_id = int(value)
            self.event_info = edited_ufc_odds(self.event_id)
            self.updated_event_id = True

    def draw(self, screen, player, colors):
        self.surf.fill(colors["nav"])
        text = self.font.render(str(player.points), True, colors["font"])
        text_rect = text.get_frect(topright=(self.width - 5, 5))
        self.surf.blit(text, text_rect)
        self.bets_button.draw(self.surf)
        self.fights_button.draw(self.surf)
        self.refresh_button.draw(self.surf)
        self.event_input.draw(self.surf, colors)
        self.view_button.draw(self.surf)
        screen.blit(self.surf)

    def event(self, event, mouse_pos, update_bets):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                if self.bets_button.rect.collidepoint(mouse_pos):
                    self.show_bets = True
                elif self.fights_button.rect.collidepoint(mouse_pos):
                    self.show_bets = False
                elif self.refresh_button.rect.collidepoint(mouse_pos):
                    update_bets()
                elif self.view_button.rect.collidepoint(mouse_pos):
                    self.event_id = self.event_input.display

        self.event_input.update(event, mouse_pos)


class Button:
    def __init__(
        self, pos, width, height, color="blue", text="", font_color="black"
    ) -> None:
        self.width = width
        self.height = height
        self.surf = pygame.Surface((width, height))
        self.color = color
        self.text = text
        self.font = pygame.font.Font("src/consolas.ttf", 16)
        self.r_text = self.font.render(self.text, True, font_color)
        self.r_text_rect = self.r_text.get_frect(topleft=(5, 3))
        self.rect = self.surf.get_frect(topleft=pos)

    def draw(self, screen):
        self.surf.fill(self.color)
        self.surf.blit(self.r_text, self.r_text_rect)
        screen.blit(self.surf, self.rect)


def pozycja_myszy_na_surface(mouse_pos, origin):
    return (
        mouse_pos[0] - origin[0],
        mouse_pos[1] - origin[1],
    )


class rButton(Button):
    def __init__(
        self, bet, pos, width, height, color="blue", text="", font_color="black"
    ) -> None:
        super().__init__(pos, width, height, color, text, font_color)
        self.bet = bet
        self.rect = self.surf.get_frect(topright=pos)


class lButton(Button):
    def __init__(
        self, bet, pos, width, height, color="blue", text="", font_color="black"
    ) -> None:
        super().__init__(pos, width, height, color, text, font_color)
        self.bet = bet
        self.rect = self.surf.get_frect(topleft=pos)


class cButton(Button):
    def __init__(
        self, pos, width, height, color="blue", text="", font_color="black"
    ) -> None:
        super().__init__(pos, width, height, color, text, font_color)
        self.rect = self.surf.get_frect(topleft=pos)
        self.r_text_rect = self.r_text.get_frect(
            center=(self.width / 2, self.height / 2)
        )
        self.font = pygame.font.Font("src/consolas.ttf", 32)


class Input:
    def __init__(self, width, height, pos, color, font_color, message, size=30):
        self.surf = pygame.Surface((width, height))
        self.rect = self.surf.get_frect(topleft=pos)
        self.surf.fill(color)
        self.color = color
        self.font = pygame.font.Font("src/consolas.ttf", size)
        self.font_color = font_color
        self.message = message
        self._display = message
        self.active = False

    @property
    def display(self):
        return self._display

    @display.setter
    def display(self, value):
        self._display = value
        self.surf.fill(self.color)
        text = self.font.render(self.display, True, self.font_color)
        text_rect = text.get_rect(topleft=(5, 5))
        self.surf.blit(text, text_rect)

    def update(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.active = True
            else:
                self.active = False
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.display = self.display[:-1]
            else:
                self.display += event.unicode

    def draw(self, screen, colors):
        self.surf.fill(self.color)
        if self.active:
            pygame.draw.rect(self.surf, colors["font"], self.surf.get_rect(), 2)
            if self.display == self.message:
                self.display = ""
        elif not self.active and self.display == "":
            self.display = self.message
        text = self.font.render(self.display, True, self.font_color)
        text_rect = text.get_rect(topleft=(5, 5))
        self.surf.blit(text, text_rect)
        screen.blit(self.surf, self.rect)


class Pop_up(metaclass=Singleton):
    def __init__(self, colors) -> None:
        if hasattr(self, "_initialized"):
            return
        self._show = False
        self.width = 300
        self.height = 100
        self.surf = pygame.Surface((self.width, self.height))
        self.rect = self.surf.get_frect(center=(300, 350))
        self.input = Input(
            self.width - 10, 50, (5, 5), colors["nav"], colors["font"], "Start betting"
        )
        self.confirm_button = cButton(
            (5, self.height - 31),
            self.width - 10,
            30,
            colors["button2"],
            "Confirm",
            colors["font"],
        )
        self.bets = list()
        self.bet = 0
        self.fight_id = 0
        self.fighter_id = 0
        self.fighter = ""
        self.eventName = ""
        self.date = ""
        self.resolved = False
        self.updated_bets = False

    def refresh_colors(self, colors):
        self.input = Input(
            self.width - 10, 50, (5, 5), colors["nav"], colors["font"], "Start betting"
        )
        self.confirm_button = cButton(
            (5, self.height - 31),
            self.width - 10,
            30,
            colors["button2"],
            "Confirm",
            colors["font"],
        )

    def draw(self, screen, colors):
        if not self.show:
            return
        self.surf.fill(colors["screen"])
        self.input.draw(self.surf, colors)
        self.confirm_button.draw(self.surf)
        screen.blit(self.surf, self.rect)
        pygame.draw.rect(screen, colors["font"], self.rect, 1)

    @property
    def show(self):
        return self._show

    @show.setter
    def show(self, value):
        self._show = value
        self.input._display = self.input.message

    def update(self, fighter, fighter_id, bet, fight_id, event, date):
        self.fighter = fighter
        self.fight_id = fight_id
        self.fighter_id = fighter_id
        self.eventName = event
        self.date = date
        self.bet = bet
        self.show = True

    def event(self, event, mouse_pos, player):
        if self.rect.collidepoint(mouse_pos) and self._show:
            mouse_pos = pozycja_myszy_na_surface(mouse_pos, (self.rect.x, self.rect.y))
            self.input.update(event, mouse_pos)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.confirm_button.rect.collidepoint(mouse_pos):
                    if is_number(self.input.display):
                        value = float(self.input.display)
                        if player.points >= value:
                            player.points -= value
                            if self.bet >= 0:
                                value = int(self.bet * value / 100) + value
                            else:
                                value = int(value / abs(self.bet) * 100) + value

                            bet = {
                                "value": value,
                                "fighter": self.fighter,
                                "fight_id": self.fight_id,
                                "fighter_id": self.fighter_id,
                                "event": self.eventName,
                                "date": self.date,
                                "resolved": False,
                                "result": "",
                            }
                            self.bets.insert(0, bet)
                            self.updated_bets = True
                            self.show = False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.show = False


class DisplayBets:
    def __init__(self, width) -> None:
        self.width = width - 100
        self.x = width / 2
        self.font = pygame.font.Font("src/consolas.ttf", 16)

    def draw(self, screen, bet, id, colors):
        y = id * 80 + 50
        surf = pygame.Surface((self.width, 60))
        rect = surf.get_frect(center=(self.x, y))
        fighter = bet["fighter"]
        F_fighter = self.font.render(fighter, True, colors["font"])
        value = bet["value"]
        F_bet = self.font.render(str(value), True, colors["font"])
        F_event = self.font.render(bet["event"], True, colors["font"])
        F_date = self.font.render(bet["date"], True, colors["font"])
        F_result = self.font.render(bet["result"], True, colors["font"])
        if bet["resolved"]:
            color = colors["inactive"]
        else:
            color = colors["screen"]
        surf.fill(color)
        surf.blit(F_event, F_event.get_frect(topleft=(5, 5)))
        surf.blit(F_date, F_date.get_frect(topright=(self.width - 10, 5)))
        surf.blit(F_fighter, F_fighter.get_frect(topleft=(30, 30)))
        surf.blit(F_bet, F_bet.get_frect(topright=(self.width - 30, 30)))
        surf.blit(F_result, F_result.get_frect(center=(self.width / 2, 45)))
        screen.blit(surf, rect)
        pygame.draw.rect(screen, colors["font"], rect, 1)


class Notification:
    def __init__(self, text, colors) -> None:
        self._show = True
        self.width = 300
        self.height = 100
        self.surf = pygame.Surface((self.width, self.height))
        self.rect = self.surf.get_frect(center=(300, 350))
        self.font = pygame.font.Font("src/consolas.ttf", 20)
        self.confirm_button = cButton(
            (5, self.height - 30),
            self.width - 10,
            30,
            colors["button1"],
            "Confirm",
            colors["font"],
        )
        self.display = text
        self.text = self.font.render(self.display, True, colors["font"])
        self.text_rect = self.text.get_frect(topleft=(5, 5))
        self.text_box = pygame.Surface((self.width - 10, 50))
        self.text_box.fill(colors["screen"])
        self.text_box_rect = self.text_box.get_frect(topleft=(5, 5))

    def draw(self, screen, colors):
        if not self._show:
            return
        self.surf.fill(colors["screen"])
        self.text_box.fill(colors["screen"])

        self.confirm_button.draw(self.surf)
        self.text_box.blit(self.text, self.text_rect)
        self.surf.blit(self.text_box, self.text_box_rect)
        pygame.draw.rect(self.surf, colors["nav"], self.text_box_rect, 1)
        screen.blit(self.surf, self.rect)
        pygame.draw.rect(screen, colors["font"], self.rect, 1)

    def event(self, event, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            mouse_pos = pozycja_myszy_na_surface(mouse_pos, (self.rect.x, self.rect.y))
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.confirm_button.rect.collidepoint(mouse_pos):
                    self._show = False
            return True


class NotificationObserver:
    def __init__(self) -> None:
        self.notifications = []

    def add(self, notification):
        self.notifications.append(notification)

    def create(self, bet, result, colors):
        if result == "WON":
            znak = "+"
            text = f"{bet["fighter"]} {result} {znak}{bet["value"]}"
        else:
            text = f"{bet["fighter"]} {result}"
        self.add(Notification(text, colors))

    def draw(self, screen, colors):
        for notification in self.notifications:
            notification.draw(screen, colors)
            break

    def update(self, event, mouse_pos):
        for notification in self.notifications:
            if notification.event(event, mouse_pos):
                break
        self.notifications = [
            notification for notification in self.notifications if notification._show
        ]

    def refresh_colors(self, colors):
        new_notifications = []
        for notification in self.notifications:
            new_notifications.append(Notification(notification.display, colors))
        self.notifications = new_notifications
