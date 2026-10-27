# coding: utf-8

import pygame

from widgets.core import Label


class Window:
    def __init__(self):
        self.surface = pygame.display.set_mode((300, 300))
        self.font = pygame.font.SysFont("sourcecodepro", 16)
        self.label = Label(self, "Hello World")
    
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
        self.label.draw()
        self.surface.blit(self.label.surface, self.label.position)



def main():
    pygame.init()
    Window().mainloop()
    pygame.quit()


if __name__ == '__main__':
    main()
