import unittest

from src.game_view import GameView
from src.window import Window


class FakeSurface:
    def __init__(self):
        self.calls = []

    def fill(self, color):
        self.calls.append(('fill', color))

    def blit(self, *args, **kwargs):
        self.calls.append(('blit', args, kwargs))


class FakeWindow:
    def __init__(self):
        self.surface = FakeSurface()
        self.font = None
        self.mode = type('Mode', (), {'show_list': False, 'show_board': False, 'show_tree': False, 'show_move_list': False, 'active_square': None})()
        self.selected_node = None
        self.visible_nodes = []
        self.font_size = 15
        self.font_type = 'arial'


class GameViewTests(unittest.TestCase):
    def test_draw_uses_live_window_surface(self):
        window = FakeWindow()
        view = GameView(window)

        view.draw()

        self.assertIn(('fill', '#000000'), window.surface.calls)


class WindowOptionsTests(unittest.TestCase):
    def test_cycle_font_size_and_type(self):
        window = Window()

        window.cycle_font_size()
        self.assertEqual(window.font_size, 18)
        self.assertGreater(len(window.visible_nodes), 0)

        window.cycle_font_type()
        self.assertEqual(window.font_type, 'consolas')
        self.assertGreater(len(window.visible_nodes), 0)

    def test_game_view_uses_latest_window_font(self):
        window = FakeWindow()
        view = GameView(window)

        window.font = 'first-font'
        self.assertEqual(view.font_view, 'first-font')

        window.font = 'second-font'
        self.assertEqual(view.font_view, 'second-font')


if __name__ == '__main__':
    unittest.main()
