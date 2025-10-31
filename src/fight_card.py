import pygame
from src.UI import lButton, rButton, pozycja_myszy_na_surface, Pop_up


class Fight_Card(pygame.sprite.Sprite):
    def __init__(self, fight, id, width, group) -> None:
        super().__init__(group)
        self.width = width - 100
        self.x = width / 2
        self.surf = pygame.Surface((self.width, 60))
        self.y = id * 80 + 30
        self.rect = self.surf.get_frect(center=(self.x, self.y))
        self.font = pygame.font.Font("src/consolas.ttf", 16)
        self.fight_id = fight["id"]
        self.date = fight["date"]
        self.fighter1_id = fight["fighters"][0]
        self.fighter1 = fight[self.fighter1_id]["Name"]
        self.F_fighter1 = self.font.render(self.fighter1, True, "black")
        self.bet1 = fight[self.fighter1]
        if self.bet1 is None:
            self.bet1 = "-"
        self.F_bet1 = self.font.render(str(self.bet1), True, "black")
        self.fighter2_id = fight["fighters"][1]
        self.fighter2 = fight[self.fighter2_id]["Name"]
        self.F_fighter2 = self.font.render(self.fighter2, True, "black")
        self.bet2 = fight[self.fighter2]
        if self.bet2 is None:
            self.bet2 = "-"
        self.F_bet2 = self.font.render(str(self.bet2), True, "black")
        self.button1 = lButton(self.bet1, (40, 30), 40, 20, text="BET")
        self.button2 = rButton(self.bet2, (self.width - 40, 30), 40, 20, text="BET")

    def draw(self, screen):
        self.surf.fill("white")
        self.surf.blit(self.F_fighter1, self.F_fighter1.get_frect(topleft=(5, 5)))
        self.surf.blit(self.F_bet1, self.F_bet1.get_frect(topleft=(5, 30)))
        self.surf.blit(
            self.F_fighter2, self.F_fighter2.get_frect(topright=(self.width - 5, 5))
        )
        self.surf.blit(
            self.F_bet2, self.F_bet2.get_frect(topright=(self.width - 5, 30))
        )
        self.button1.draw(self.surf)
        self.button2.draw(self.surf)
        screen.blit(self.surf, self.rect)

    def event(self, mouse_pos):
        mouse_pos = pozycja_myszy_na_surface(mouse_pos, (self.rect.x, self.rect.y))  # type: ignore
        if self.button1.rect.collidepoint(mouse_pos):
            pop_up = Pop_up()
            pop_up.show = True
            pop_up.fighter = self.fighter1
            pop_up.fighter_id = self.fighter1_id
            pop_up.bet = int(self.bet1)
            pop_up.fight_id = self.fight_id
        elif self.button2.rect.collidepoint(mouse_pos):
            pop_up = Pop_up()
            pop_up.bet = int(self.bet2)
            pop_up.fighter = self.fighter2
            pop_up.fighter_id = self.fighter2_id
            pop_up.fight_id = self.fight_id
            pop_up.show = True
