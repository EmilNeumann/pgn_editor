# coding: utf-8


import pygame

from widgets.menu import MenuBar


SIZE = 300


class Window:
    def __init__(self):
        self.surface = pygame.display.set_mode((SIZE, SIZE))
        self.font = pygame.font.SysFont("sourcecodepro", 16)
        self.menu_bar = MenuBar(self)
        self.menu_bar.add_menu_button("File")
        self.menu_bar.add_menu_button("Edit")
    
    def mainloop(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.draw()
            clock.tick(60)
            pygame.display.flip()
    
    def draw(self):
        self.surface.fill("#000000")
        self.menu_bar.draw()
        self.surface.blit(self.menu_bar.surface, self.menu_bar.position)
    
    @property
    def width(self):
        return self.surface.get_width()


def main():
    pygame.init()
    Window().mainloop()
    pygame.quit()


if __name__ == '__main__':
    main()
