# coding: utf-8


import pygame


class Widget:
    def __init__(self, parent):
        self.parent = parent
        self.window = getattr(parent, "window", parent)
        self.surface = None
        self.hovered = False
        self._x = 0
        self._y = 0
        self._width = 0
        self._height = 0
        self._background = "#000000"
    
    @property
    def x(self): return self._x
    
    @x.setter
    def x(self, _x): self._x = _x
    
    @property
    def y(self): return self._y
    
    @y.setter
    def y(self, _y): self._y = _y
    
    @property
    def position(self): return (self.x, self.y)
    
    @property
    def width(self): return self._width
    
    @width.setter
    def width(self, _width): self._width = _width
    
    @property
    def height(self): return self._height
    
    @height.setter
    def height(self, _height):
        self._height = _height
    
    @property
    def size(self): return (self.width, self.height)
    
    @size.setter
    def size(self, _size):
        _width, _height = _size
        self.width = _width
        self.height = _height
    
    @property
    def background(self): return self._background
    
    @background.setter
    def background(self, _background):
        self._background = _background
    
    def draw(self):
        self.surface = pygame.Surface(self.size)
        self.surface.fill(self.background)
    
    def click(self, pos): pass
    
    def hover(self, pos): self.hovered = True
    
    def leave(self): self.hovered = False
    
    def scroll(self, y): pass


class Container(Widget):
    """
    A widget that can contain other widgets.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.widgets = []
    
    def draw(self):
        super().draw()
        for widget in self.widgets:
            widget.draw()
            self.surface.blit(widget.surface, widget.position)
    
    def click(self, pos):
        x, y = pos
        for widget in self.widgets:
            rel_x = x - widget.x
            rel_y = y - widget.y
            if rel_x in range(widget.width) and rel_y in range(widget.height):
                widget.click((rel_x, rel_y))
    
    def hover(self, pos):
        super().hover(pos)
        x, y = pos
        for widget in self.widgets:
            rel_x = x - widget.x
            rel_y = y - widget.y
            if rel_x in range(widget.width) and rel_y in range(widget.height):
                widget.hover((rel_x, rel_y))
            else:
                widget.leave()
    
    def leave(self):
        super().leave()
        for widget in self.widgets:
            widget.leave()
    
    def scroll(self, y):
        for widget in self.widgets:
            widget.scroll(y)
