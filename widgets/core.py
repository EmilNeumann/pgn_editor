# coding: utf-8


import pygame

from . import Widget


class Label(Widget):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.text = text
        self.text_color = "#ffffff"
        self.text_surface = None
        self.margin = 5
    
    def draw(self):
        self.text_surface = self.window.font.render(
            self.text.encode('latin-1'), False,
            self.text_color, self.background
        )
        self._width = self.text_surface.get_width() + self.margin * 2
        self._height = self.text_surface.get_height() + self.margin * 2
        self.surface = pygame.Surface(self.size)
        self.surface.fill(self.background)
        self.surface.blit(self.text_surface, (self.margin, self.margin))
