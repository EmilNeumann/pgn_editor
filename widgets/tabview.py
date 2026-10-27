# coding: utf-8


import pygame

from . import Container, Widget
from .core import Label


class Tab(Container):
    @property
    def y(self):
        return self.parent.tab_bar.height
    
    @property
    def width(self): return self.parent.width
    
    @property
    def height(self):
        return self.parent.height - self.y


class TabNameLabel(Label):
    def click(self, pos):
        tab_control = self.parent
        tab_bar = tab_control.parent
        tab_bar.select_tab(tab_control)


class TabCloseButton(Widget):
    @property
    def x(self):
        return self.parent.label.width
    
    @property
    def width(self):
        return self.parent.label.height
    
    @property
    def height(self):
        return self.parent.label.height
    
    def draw(self):
        super().draw()
        x = self.width // 3
        x2 = self.width - x
        color = "#ff0000" if self.hovered else "#7f0000"
        pygame.draw.line(self.surface, color, (x, x), (x2, x2))
        pygame.draw.line(self.surface, color, (x, x2), (x2, x))
    
    def click(self, pos):
        tab_control = self.parent
        tab_bar = tab_control.parent
        tab_bar.close_tab(tab_control)


class TabControl(Container):
    def __init__(self, parent, text, tab, with_close_button):
        super().__init__(parent)
        self.label = TabNameLabel(self, text)
        self.widgets.append(self.label)
        self.close_button = None
        if with_close_button:
            self.close_button = TabCloseButton(self)
            self.widgets.append(self.close_button)
        self.tab = tab
    
    @property
    def width(self):
        return sum(widget.width for widget in self.widgets)
    
    @property
    def height(self):
        return self.label.height
    
    @property
    def background(self):
        return self._background
    
    @background.setter
    def background(self, _background):
        self._background = _background
        self.label.background = _background
        if self.close_button is not None:
            self.close_button.background = _background


class TabBar(Container):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_tab_index = 0
    
    @property
    def width(self):
        return self.parent.width
    
    @property
    def height(self):
        return max((widget.height for widget in self.widgets), default=0)
    
    @property
    def selected_tab_control(self):
        if not self.widgets:
            return None
        return self.widgets[self.selected_tab_index]
    
    def draw(self):
        self.surface = pygame.Surface(self.size)
        self.surface.fill(self.background)
        for tab_control in self.widgets:
            tab_control.label.text_color = "#7f7f7f"
            tab_control.background = "#1f1f1f" if tab_control.hovered else "#000000"
        if self.selected_tab_control is not None:
            self.selected_tab_control.label.text_color = "#ffffff"
            self.selected_tab_control.background = "#1f1f1f"
        x = 0
        for tab_control in self.widgets:
            tab_control.draw()
            tab_control.x = x
            self.surface.blit(tab_control.surface, tab_control.position)
            x += tab_control.width
    
    def select_tab(self, tab_control):
        self.selected_tab_index = self.widgets.index(tab_control)
    
    def add_tab_control(self, text, tab, with_close_button=True):
        tab_control = TabControl(self, text, tab, with_close_button)
        self.widgets.append(tab_control)
        return tab_control
    
    def close_tab(self, tab_control):
        self.widgets.remove(tab_control)
        self.selected_tab_index = min(
            self.selected_tab_index,
            len(self.widgets) - 1
        )


class TabView(Container):
    def __init__(self, parent):
        super().__init__(parent)
        self.tab_bar = TabBar(self)
    
    @property
    def selected_tab(self):
        if not self.tab_bar.widgets:
            return None
        return self.tab_bar.selected_tab_control.tab
    
    def draw(self):
        self.surface = pygame.Surface(self.size)
        self.surface.fill(self.background)
        self.tab_bar.draw()
        self.surface.blit(self.tab_bar.surface, self.tab_bar.position)
        if self.selected_tab is not None:
            self.selected_tab.draw()
            self.surface.blit(self.selected_tab.surface, self.selected_tab.position)
    
    def click(self, pos):
        x, y = pos
        if y in range(self.tab_bar.height):
            self.tab_bar.click(pos)
        elif self.selected_tab is not None:
            self.selected_tab.click((x, y - self.tab_bar.height))
    
    def hover(self, pos):
        self.hovered = True
        x, y = pos
        if y in range(self.tab_bar.height):
            self.tab_bar.hover(pos)
            if self.selected_tab is not None:
                self.selected_tab.leave()
        else:
            if self.selected_tab is not None:
                self.selected_tab.hover((x, y - self.tab_bar.height))
            self.tab_bar.leave()
    
    def add_tab(self, text) -> Tab:
        tab = Tab(self)
        self.tab_bar.add_tab_control(text, tab)
        return tab
