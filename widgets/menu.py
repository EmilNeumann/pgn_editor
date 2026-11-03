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
        menu_item.draw()
        menu_item.y = self.height
        self.widgets.append(menu_item)
        return menu_item

    @property
    def height(self):
        return sum(w.height for w in self.widgets)

    @property
    def width(self):
        return max(w.width for w in self.widgets)


class MenuButton(Label):
    def __init__(self, parent, text):
        super().__init__(parent, text)
        self.menu = Menu(self.window)

    def click(self, pos):
        menu_bar = self.parent
        if menu_bar.parent.visible_menu is self.menu:
            menu_bar.parent.visible_menu = None
        else:
            menu_bar.parent.visible_menu = self.menu
            menu_bar.parent.menu_position = (self.x, menu_bar.height)


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
