# coding: utf-8

import pygame

from widgets.core import ListBox


SIZE = 300


class Window:
    def __init__(self):
        self.font_size = 16
        self.font = pygame.font.SysFont("sourcecodepro", self.font_size)
        self.char_width, self.char_height = self.font.size(" ")
        self.surface = pygame.display.set_mode((SIZE, SIZE), flags=pygame.RESIZABLE)
        self.listbox = ListBox(self, [f"Item {i}" for i in range(20)])
        self.listbox.width = SIZE
        self.listbox.height = SIZE

    def mainloop(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_button_down(event)
                if event.type == pygame.MOUSEWHEEL:
                    self.mouse_wheel(event)
                if event.type == pygame.KEYDOWN:
                    self.key_down(event)
            self.draw()
            pygame.display.flip()
            clock.tick(60)

    def draw(self):
        self.surface.fill("#000000")
        self.listbox.draw()
        self.surface.blit(self.listbox.surface, self.listbox.position)

    def mouse_button_down(self, event):
        if event.button == 1:
            rel_x = event.pos[0] - self.listbox.x
            rel_y = event.pos[1] - self.listbox.y
            if rel_x in range(self.listbox.width) and rel_y in range(self.listbox.height):
                self.listbox.click((rel_x, rel_y))

    def mouse_wheel(self, event):
        self.listbox.scroll(event.y)

    def key_down(self, event):
        if event.key == pygame.K_UP:
            self.listbox.selected_index = max(0, self.listbox.selected_index - 1)
        if event.key == pygame.K_DOWN:
            self.listbox.selected_index = min(self.listbox.selected_index + 1, self.listbox.line_count - 1)


def main():
    pygame.init()
    Window().mainloop()
    pygame.quit()

if __name__ == '__main__':
    main()
