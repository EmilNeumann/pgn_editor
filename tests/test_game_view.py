import unittest

from src.game_view import GameView


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


class GameViewTests(unittest.TestCase):
    def test_draw_uses_live_window_surface(self):
        window = FakeWindow()
        view = GameView(window)

        view.draw()

        self.assertIn(('fill', '#000000'), window.surface.calls)


if __name__ == '__main__':
    unittest.main()
