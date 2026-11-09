# coding: utf-8


import pygame

from widgets.menu import Menu, MenuBar


SIZE = 400


class Window:
    def __init__(self):
        self.running = True
        self.surface = pygame.display.set_mode((SIZE, SIZE), flags=pygame.RESIZABLE)
        self.font = pygame.font.SysFont("sourcecodepro", 16)
        self.visible_menu: Menu = None
        self.menu_bar = MenuBar(self)
        file_button = self.menu_bar.add_menu_button("File")
        game_button = self.menu_bar.add_menu_button("Game")
        tree_button = self.menu_bar.add_menu_button("Tree")
        node_button = self.menu_bar.add_menu_button("Node")
        mode_button = self.menu_bar.add_menu_button("Mode")
        help_button = self.menu_bar.add_menu_button("Help")
        f = lambda: None  # callback function which does nothing
        file_button.menu.add_menu_item("New File", f)
        file_button.menu.add_menu_item("Open", f)
        file_button.menu.add_menu_item("Save", f)
        file_button.menu.add_menu_item("Save As", f)
        file_button.menu.add_menu_item("Quit", self.quit)
        game_button.menu.add_menu_item("New Game", f)
        game_button.menu.add_menu_item("Move Up", f)
        game_button.menu.add_menu_item("Move Down", f)
        tree_button.menu.add_menu_item("Cut", f)
        tree_button.menu.add_menu_item("Copy", f)
        tree_button.menu.add_menu_item("Paste", f)
        tree_button.menu.add_menu_item("Move Up", f)
        tree_button.menu.add_menu_item("Move Down", f)
        tree_button.menu.add_menu_item("Delete", f)
        node_button.menu.add_menu_item("Edit Comment", f)
        node_button.menu.add_menu_item("Expand / Collapse", f)
        mode_button.menu.add_menu_item("Read-only", f)
        mode_button.menu.add_menu_item("Edit Mode", f)
        mode_button.menu.add_menu_item("Practice", f)
        help_button.menu.add_menu_item("About", f)
    
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
            self.surface.blit(self.visible_menu.surface, self.visible_menu.position)
    
    @property
    def width(self):
        return self.surface.get_width()

    def mouse_button_down(self, event):
        if event.button == 1:
            if event.pos[1] <= self.menu_bar.height:
                self.menu_bar.click(event.pos)
            elif self.visible_menu is not None:
                rel_x = event.pos[0] - self.visible_menu.x
                rel_y = event.pos[1] - self.visible_menu.y
                if rel_x in range(self.visible_menu.width) and rel_y in range(self.visible_menu.height):
                    self.visible_menu.click((rel_x, rel_y))
            else:
                pass  # TODO: call .click(event.pos) on the clicked widget

    def mouse_motion(self, event):
        if event.pos[1] <= self.menu_bar.height:
            self.menu_bar.hover(event.pos)
        else:
            self.menu_bar.leave()
        if self.visible_menu is not None:
            rel_x = event.pos[0] - self.visible_menu.x
            rel_y = event.pos[1] - self.visible_menu.y
            if rel_x in range(self.visible_menu.width) and rel_y in range(self.visible_menu.height):
                self.visible_menu.hover((rel_x, rel_y))
            else:
                self.visible_menu.leave()

    def quit(self):
        self.running = False


def main():
    pygame.init()
    Window().mainloop()
    pygame.quit()


if __name__ == '__main__':
    main()
