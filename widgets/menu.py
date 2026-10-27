# coding: utf-8


import pygame

from . import Container
from .core import Label


class MenuItem(Label):
    def __init__(self, parent, text):
        super().__init__(parent, text)
        self.callback = lambda: None
    
    def click(self, pos):
        self.callback()


class Menu(Container):
    def add_menu_item(self, text):
        menu_item = MenuItem(self, text)
        self.widgets.append(menu_item)
        return menu_item


class MenuButton(Label):
    def __init__(self, parent, text):
        super().__init__(parent, text)
        self.menu = Menu(self.window)


class MenuBar(Container):
    def draw(self):
        self.surface = pygame.Surface(self.size)
        self.surface.fill(self.background)
        x = 0
        for menu_button in self.widgets:
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
