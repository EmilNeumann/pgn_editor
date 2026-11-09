# coding: utf-8


import pygame

from . import Container
from .core import Label


class MenuItem(Label):
    def __init__(self, parent, text, callback):
        super().__init__(parent, text)
        self.callback = callback

    @property
    def width(self):
        return self.parent.width
    
    def click(self, pos):
        self.callback()

    def draw(self):
        self.background = "#1f1f1f" if self.hovered else "#000000"
        super().draw()


class Menu(Container):
    def add_menu_item(self, text, callback):
        menu_item = MenuItem(self, text, callback)
        menu_item.draw()
        menu_item.y = self.height
        self.widgets.append(menu_item)
        return menu_item

    @property
    def height(self):
        return sum(w.height for w in self.widgets)

    @property
    def width(self):
        if not self.widgets:
            return 0
        return max(w.min_width for w in self.widgets)


class MenuButton(Label):
    def __init__(self, parent, text):
        super().__init__(parent, text)
        self.menu = Menu(self.window)

    def click(self, pos):
        menu_bar = self.parent
        if self.window.visible_menu is self.menu:
            self.window.visible_menu = None
        else:
            self.window.visible_menu = self.menu
            self.menu.x = self.x
            self.menu.y = menu_bar.height


class MenuBar(Container):
    def draw(self):
        self.surface = pygame.Surface(self.size)
        self.surface.fill(self.background)
        x = 0
        for menu_button in self.widgets:
            menu_button.background = "#1f1f1f" if menu_button.hovered else "#000000"
            menu_button.x = x
            menu_button.draw()
            self.surface.blit(menu_button.surface, menu_button.position)
            x += menu_button.width
    
    @property
    def width(self):
        return self.parent.width
    
    @property
    def height(self):
        return max(widget.height for widget in self.widgets)
    
    def add_menu_button(self, text):
        menu_button = MenuButton(self, text)
        self.widgets.append(menu_button)
        return menu_button
