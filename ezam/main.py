from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.graphics import Line, Rectangle
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from maze import Maze, Player, Enemy


class EzamGame(Widget):


    def __init__(self, **kwargs):
        super(EzamGame, self).__init__(**kwargs)
        self.cell_width = 20

        self.maze = Maze(25, 25)
        self.maze.generate()

        with self.canvas:
            for segment in self.maze.get_wall_segments():
                coords = tuple((val + 0.5) * self.cell_width
                    for val in segment)
                Line(points = coords)

        empty_cells = self.maze.get_empty_cells()
        x,y = empty_cells.pop()
        self.player_view = PlayerView(Player(x, y, self.maze))
        self.add_widget(self.player_view)

        x,y = empty_cells.pop()
        self.enemy_view = EnemyView(Enemy(x, y, self.maze))
        self.add_widget(self.enemy_view)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] in ['up', 'down', 'left', 'right']:
            self.player_view.move(keycode[1])

class PlayerView(Widget):
    def __init__(self, player, **kwargs):
        super(PlayerView, self).__init__(**kwargs)
        self.player = player
        self.update_pos()

    def update_pos(self):
        animation = Animation(x = 20 * self.player.x + 10,
                              y = 20 * self.player.y + 10,
                              d = 0.05)
        animation.start(self)

    def move(self, direction):
        self.player.move(direction)
        self.update_pos()

class EnemyView(Widget):
    def __init__(self, enemy, **kwargs):
        super(EnemyView, self).__init__(**kwargs)
        self.enemy = enemy
        self.update_pos()
        Clock.schedule_interval(self.move, 0.1)

    def update_pos(self):
        animation = Animation(x = 20 * self.enemy.x + 10,
                              y = 20 * self.enemy.y + 10,
                              d = 0.05)
        animation.start(self)

    def move(self, dt):
        self.enemy.move()
        self.update_pos()



class EzamApp(App):
    def build(self):
        return EzamGame()


if __name__ == '__main__':
    EzamApp().run()