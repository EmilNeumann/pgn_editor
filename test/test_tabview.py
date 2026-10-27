# coding: utf-8


import pygame

from widgets.tabview import TabView, Tab


SIZE = 300


class Window:
    def __init__(self):
        self.surface = pygame.display.set_mode(
            (SIZE, SIZE),
            flags=pygame.RESIZABLE
        )
        self.font = pygame.font.SysFont("sourcecodepro", 16)
        self.tab_view = TabView(self)
        self.tab_view.width = SIZE
        self.tab_view.height = SIZE
        tab1 = self.tab_view.add_tab("Tab 1")
        tab1_tab_view = TabView(tab1)
        tab1_tab_view.width = tab1.width
        tab1_tab_view.height = tab1.height
        tab1.widgets.append(tab1_tab_view)
        games_tab = Tab(tab1_tab_view)
        tab1_tab_view.tab_bar.add_tab_control(
            "Games", games_tab,
            with_close_button=False
        )
        headers_tab = Tab(tab1_tab_view)
        tab1_tab_view.tab_bar.add_tab_control(
            "Headers", headers_tab,
            with_close_button=False
        )
        self.tab_view.add_tab("Tab 2")
    
    def mainloop(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_button_down(event)
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_motion(event)
                if event.type == pygame.MOUSEWHEEL:
                    self.mouse_wheel(event)
            self.draw()
            clock.tick(60)
            pygame.display.flip()
    
    def draw(self):
        self.surface.fill("#000000")
        self.tab_view.draw()
        self.surface.blit(self.tab_view.surface, self.tab_view.position)
    
    def mouse_button_down(self, event):
        if event.button == 1:
            self.tab_view.click(event.pos)
    
    def mouse_motion(self, event):
        self.tab_view.hover(event.pos)
    
    def mouse_wheel(self, event):
        self.tab_view.scroll(event.y)


def main():
    pygame.init()
    Window().mainloop()
    pygame.quit()


if __name__ == '__main__':
    main()
