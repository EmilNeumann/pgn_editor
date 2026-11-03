# coding: utf-8


import pygame

from widgets.menu import Menu, MenuBar


SIZE = 300


class Window:
    def __init__(self):
        self.running = True
        self.surface = pygame.display.set_mode((SIZE, SIZE))
        self.font = pygame.font.SysFont("sourcecodepro", 16)
        self.visible_menu: Menu = None
        self.menu_position = (0, 0)
        self.menu_bar = MenuBar(self)
        file_button = self.menu_bar.add_menu_button("File")
        edit_button = self.menu_bar.add_menu_button("Edit")
        file_button.menu.add_menu_item("New")
        file_button.menu.add_menu_item("Open")
        file_button.menu.add_menu_item("Save")
        file_button.menu.add_menu_item("Save As")
        file_button.menu.add_menu_item("Quit").callback = self.quit
        edit_button.menu.add_menu_item("Cut")
        edit_button.menu.add_menu_item("Paste")
        edit_button.menu.add_menu_item("Move Variation Up")
        edit_button.menu.add_menu_item("Move Variation Down")
        edit_button.menu.add_menu_item("Move Variation To ...")
    
    def mainloop(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_button_down(event)
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_motion(event)
            self.draw()
            clock.tick(60)
            pygame.display.flip()
    
    def draw(self):
        self.surface.fill("#1f1f1f")
        self.menu_bar.draw()
        self.surface.blit(self.menu_bar.surface, self.menu_bar.position)
        if self.visible_menu is not None:
            self.visible_menu.draw()
            self.surface.blit(self.visible_menu.surface, self.menu_position)
    
    @property
    def width(self):
        return self.surface.get_width()

    def mouse_button_down(self, event):
        if event.button == 1:
            if event.pos[1] <= self.menu_bar.height:
                self.menu_bar.click(event.pos)
            elif self.visible_menu is not None:
                rel_x = event.pos[0] - self.menu_position[0]
                rel_y = event.pos[1] - self.menu_position[1]
                if rel_x in range(self.visible_menu.width) and rel_y in range(self.visible_menu.height):
                    self.visible_menu.click((rel_x, rel_y))
            else:
                pass  # TODO: call .click(event.pos) on the clicked widget

    def mouse_motion(self, event):
        pass

    def quit(self):
        self.running = False


def main():
    pygame.init()
    Window().mainloop()
    pygame.quit()


if __name__ == '__main__':
    main()
