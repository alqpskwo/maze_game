from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Line
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from maze import Maze, Player, Enemy, CollisionChecker


class GameWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        self.new_game()

    def new_game(self, *args):
        engine = EngineWidget()
        engine.bind(on_game_over=self.on_game_over)
        self.clear_widgets()
        self.add_widget(engine)

    def on_game_over(self, engine, *args):
        self.clear_widgets()
        game_over_widget = GameOverWidget()
        game_over_widget.new_game_btn.bind(on_release=self.new_game)
        self.add_widget(game_over_widget)

class GameOverWidget(Widget):
    new_game_btn = ObjectProperty(None)

class EngineWidget(Widget):
    def __init__(self, **kwargs):
        super(EngineWidget, self).__init__(**kwargs)
        self.register_event_type('on_game_over')
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
        player = Player(x, y, self.maze)
        self.player_widget = PlayerWidget(player, self)
        self.player_widget.bind(on_killed = self.on_game_over)
        self.add_widget(self.player_widget)

        self.collision_checker = CollisionChecker(player)

        self.non_player_objects =[]

        for i in range(0, 5):
            x,y = empty_cells.pop()
            enemy = Enemy(x, y, self.maze)
            self.non_player_objects.append(enemy)
            self.add_widget(EnemyWidget(enemy, self))

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] in ['up', 'down', 'left', 'right']:
            self.player_widget.move(keycode[1])

    def remove_game_object(self, game_object_widget):
        self.non_player_objects.remove(game_object_widget.game_object)
        self.remove_widget(game_object_widget)

    def check_collision(self, game_object_widget=None):
        if game_object_widget:
            self.collision_checker.check([game_object_widget.game_object])
        else:
            self.collision_checker.check(self.non_player_objects)

    def on_game_over(self, *args):
        print("game over")


class PlayerWidget(Widget):
    def __init__(self, player, engine, **kwargs):
        super(PlayerWidget, self).__init__(**kwargs)
        self.game_object = player
        self.engine = engine
        self.update_pos()

    def update_pos(self):
        if self.game_object.marked_for_removal:
            self.engine.dispatch('on_game_over')
        animation = Animation(x = 20 * self.game_object.x + 10,
                              y = 20 * self.game_object.y + 10,
                              d = 0.05)
        animation.start(self)

    def move(self, direction):
        self.game_object.move(direction)
        self.engine.check_collision()
        self.update_pos()

    def on_killed(self, *args):
        print("I am dead")

class EnemyWidget(Widget):
    def __init__(self, enemy, engine, **kwargs):
        super(EnemyWidget, self).__init__(**kwargs)
        self.game_object = enemy
        self.engine = engine
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
        return GameWidget()


if __name__ == '__main__':
    EzamApp().run()