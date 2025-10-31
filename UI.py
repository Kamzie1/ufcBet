import pygame
from singleton import Singleton
from utils import is_number


class Navbar:
    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height
        self.surf = pygame.Surface((width, 36))
        self.rect = self.surf.get_frect(topleft=(0, 0))
        self.font = pygame.font.Font("consolas.ttf", 26)
        self.show_bets = False
        self.fights_button = Button((5, 5), 100, 26, "blue", "Fights")
        self.bets_button = Button((110, 5), 100, 26, "red", "Bets")

    def draw(self, screen, player):
        self.surf.fill("grey")
        text = self.font.render(str(player.points), True, "black")
        text_rect = text.get_frect(topright=(self.width - 5, 5))
        self.surf.blit(text, text_rect)
        self.bets_button.draw(self.surf)
        self.fights_button.draw(self.surf)
        screen.blit(self.surf)

    def event(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            if self.bets_button.rect.collidepoint(mouse_pos):
                self.show_bets = True
            elif self.fights_button.rect.collidepoint(mouse_pos):
                self.show_bets = False


class Button:
    def __init__(self, pos, width, height, color="blue", text="") -> None:
        self.width = width
        self.height = height
        self.surf = pygame.Surface((width, height))
        self.color = color
        self.text = text
        self.font = pygame.font.Font("consolas.ttf", 16)
        self.r_text = self.font.render(self.text, True, "black")
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
    def __init__(self, bet, pos, width, height, color="blue", text="") -> None:
        super().__init__(pos, width, height, color, text)
        self.bet = bet
        self.rect = self.surf.get_frect(topright=pos)


class lButton(Button):
    def __init__(self, bet, pos, width, height, color="blue", text="") -> None:
        super().__init__(pos, width, height, color, text)
        self.bet = bet
        self.rect = self.surf.get_frect(topleft=pos)


class cButton(Button):
    def __init__(self, pos, width, height, color="blue", text="") -> None:
        super().__init__(pos, width, height, color, text)
        self.rect = self.surf.get_frect(topleft=pos)
        self.r_text_rect = self.r_text.get_frect(
            center=(self.width / 2, self.height / 2)
        )
        self.font = pygame.font.Font("consolas.ttf", 26)


class Input:
    def __init__(self, width, height, pos, color, font_color, message):
        self.surf = pygame.Surface((width, height))
        self.rect = self.surf.get_frect(topleft=pos)
        self.surf.fill(color)
        self.color = color
        self.font = pygame.font.Font("consolas.ttf", 30)
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

    def draw(self, screen):
        self.surf.fill(self.color)
        if self.active:
            pygame.draw.rect(self.surf, "black", self.surf.get_rect(), 2)
            if self.display == self.message:
                self.display = ""
        elif not self.active and self.display == "":
            self.display = self.message
        text = self.font.render(self.display, True, self.font_color)
        text_rect = text.get_rect(topleft=(5, 5))
        self.surf.blit(text, text_rect)
        screen.blit(self.surf, self.rect)


class Pop_up(metaclass=Singleton):
    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return
        self._show = False
        self.width = 300
        self.height = 100
        self.surf = pygame.Surface((self.width, self.height))
        self.rect = self.surf.get_frect(center=(300, 350))
        self.input = Input(
            self.width - 10, 50, (5, 0), "grey", "black", "Start betting"
        )
        self.confirm_button = cButton(
            (5, self.height - 30), self.width - 10, 30, "blue", "Confirm"
        )
        self.bets = list()
        self.bet = 0
        self.fighter = ""

    def draw(self, screen):
        if not self.show:
            return
        self.surf.fill("white")
        self.input.draw(self.surf)
        self.confirm_button.draw(self.surf)
        screen.blit(self.surf, self.rect)
        pygame.draw.rect(screen, "black", self.rect, 1)

    @property
    def show(self):
        return self._show

    @show.setter
    def show(self, value):
        self._show = value
        self.input._display = self.input.message

    def event(self, event, mouse_pos, player):
        if self.rect.collidepoint(mouse_pos):
            mouse_pos = pozycja_myszy_na_surface(mouse_pos, (self.rect.x, self.rect.y))
            self.input.update(event, mouse_pos)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.confirm_button.rect.collidepoint(mouse_pos):
                    print("click")
                    if is_number(self.input.display):
                        value = float(self.input.display)
                        player.points -= value
                        bet = {"value": value * self.bet / 100, "fighter": self.fighter}
                        self.bets.append(bet)
                        self.show = False
                        print(self.bets)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.show = False


class DisplayBets:
    def __init__(self, width) -> None:
        self.width = width - 100
        self.x = width / 2
        self.font = pygame.font.Font("consolas.ttf", 16)

    def draw(self, screen, bet, id):
        y = id * 80 + 30
        surf = pygame.Surface((self.width, 60))
        surf.fill("white")
        rect = surf.get_frect(center=(self.x, y))
        fighter = bet["fighter"]
        F_fighter = self.font.render(fighter, True, "black")
        bet = bet["value"]
        F_bet = self.font.render(str(bet), True, "black")
        surf.blit(F_fighter, F_fighter.get_frect(topleft=(5, 5)))
        surf.blit(F_bet, F_bet.get_frect(topleft=(5, 30)))
        screen.blit(surf, rect)
