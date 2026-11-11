# coding: utf-8


import pygame

from . import Widget


class Label(Widget):
    def __init__(self, parent, text: str):
        super().__init__(parent)
        self.text = text
        self.text_color = "#ffffff"
        self.text_surface = None
        self.margin = 5
        self.min_width = 0
        self.min_height = 0
    
    def draw(self):
        self.text_surface = self.window.font.render(
            self.text.encode('latin-1'), False,
            self.text_color, self.background
        )
        self.min_width = self.text_surface.get_width() + self.margin * 2
        self.min_height = self.text_surface.get_height() + self.margin * 2
        self._width = max(self._width, self.min_width)
        self._height = max(self._height, self.min_height)
        self.surface = pygame.Surface(self.size)
        self.surface.fill(self.background)
        self.surface.blit(self.text_surface, (self.margin, self.margin))


class Scrollable(Widget):
    def __init__(self, parent):
        super().__init__(parent)
        self.line_offset = 0

    @property
    def line_count(self):
        return 0

    @property
    def max_visible_lines(self):
        return self.height // self.window.char_height

    def scroll(self, y):
        self.line_offset -= y * 3
        self.clip_offset()

    def clip_offset(self):
        self.line_offset = min(
            self.line_offset,
            self.line_count - self.max_visible_lines
        )
        self.line_offset = max(0, self.line_offset)


class ListBox(Scrollable):
    def __init__(self, parent, items: list[str]):
        super().__init__(parent)
        self.items = items.copy()
        self.selected_index: int = 0

    @property
    def line_count(self):
        return len(self.items)

    def draw(self):
        super().draw()
        for i, line in enumerate(self.items):
            background = "#000000"
            if i == self.selected_index:
                background = "#0000ff"
            text_surface = self.window.font.render(
                line.encode('latin-1'),
                False, "#ffffff", background
            )
            y = (i - self.line_offset) * self.window.char_height
            self.surface.blit(text_surface, (0, y))

    def click(self, pos):
        index = pos[1] // self.window.char_height + self.line_offset
        if index < len(self.items):
            self.selected_index = index
