from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.graphics import Line, Rectangle
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from maze import Maze, Player, Enemy, CollisionChecker


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
<<<<<<< HEAD
        player = Player(x, y, self.maze)
        self.player_widget = PlayerWidget(player, self)
        self.add_widget(self.player_widget)

        self.collision_checker = CollisionChecker(player)

        x,y = empty_cells.pop()
        enemy = Enemy(x, y, self.maze)
        self.enemy_widget = EnemyWidget(enemy, self)
        self.collision_checker.add(enemy)
=======
        self.player_widget = PlayerWidget(Player(x, y, self.maze))
        self.add_widget(self.player_widget)

        x,y = empty_cells.pop()
        self.enemy_widget = EnemyWidget(Enemy(x, y, self.maze))
>>>>>>> master
        self.add_widget(self.enemy_widget)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] in ['up', 'down', 'left', 'right']:
            self.player_widget.move(keycode[1])
<<<<<<< HEAD

    def remove_game_object(self, game_object_widget):
        self.collision_checker.remove(game_object_widget.game_object)
        self.remove_widget(game_object_widget)

    def check_collision(self, game_object_widget=None):
        if game_object_widget:
            self.collision_checker.check(game_object_widget.game_object)
        else:
            self.collision_checker.check_all()

class PlayerWidget(Widget):
    def __init__(self, player, engine, **kwargs):
=======

class PlayerWidget(Widget):
    def __init__(self, player, **kwargs):
>>>>>>> master
        super(PlayerWidget, self).__init__(**kwargs)
        self.player = player
        self.engine = engine
        self.update_pos()

    def update_pos(self):
        animation = Animation(x = 20 * self.player.x + 10,
                              y = 20 * self.player.y + 10,
                              d = 0.05)
        animation.start(self)

    def move(self, direction):
        self.player.move(direction)
        self.engine.check_collision()
        self.update_pos()

class EnemyWidget(Widget):
<<<<<<< HEAD
    def __init__(self, enemy, engine, **kwargs):
        super(EnemyWidget, self).__init__(**kwargs)
        self.game_object = enemy
        self.engine = engine
=======
    def __init__(self, enemy, **kwargs):
        super(EnemyWidget, self).__init__(**kwargs)
        self.enemy = enemy
>>>>>>> master
        self.update_pos()
        self.move_event = Clock.schedule_interval(self.move, 0.1)

    def update_pos(self):
        if self.game_object.marked_for_removal:
            self.move_event.cancel()
            self.engine.remove_game_object(self)
        else:
            animation = Animation(x = 20 * self.game_object.x + 10,
                                  y = 20 * self.game_object.y + 10,
                                  d = 0.05)
            animation.start(self)

    def move(self, dt):
        self.game_object.move()
        self.engine.check_collision(self)
        self.update_pos()



class EzamApp(App):
    def build(self):
        return EzamGame()


if __name__ == '__main__':
    EzamApp().run()