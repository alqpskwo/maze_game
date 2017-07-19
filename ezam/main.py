from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Line, Rectangle, Color
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from maze import Maze, Player, Enemy, Gold, Crystal
import itertools


class GameWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        self.settings = {'maze_width': 12,
                         'maze_height': 12,
                         'num_enemies': 5,
                         'num_gold': 5,
                         'num_crystals': 5,
                         'enemy_speed': 4}
        self.load_welcome_screen()

    def new_game(self, *args):
        engine = EngineWidget(self.settings)
        engine.bind(on_game_over=self.load_game_over_screen)
        engine.bind(on_win=self.load_win_screen)
        self.clear_widgets()
        self.add_widget(engine)

    def load_game_over_screen(self, engine, *args):
        self.clear_widgets()
        game_over_widget = GameOverWidget()
        game_over_widget.return_btn.bind(on_release=self.load_welcome_screen)
        self.add_widget(game_over_widget)

    def load_welcome_screen(self, *args):
        self.clear_widgets()
        welcome_widget = WelcomeWidget()
        welcome_widget.new_game_btn.bind(on_release=self.new_game)
        welcome_widget.settings_btn.bind(on_release=self.load_settings_screen)
        self.add_widget(welcome_widget)

    def load_win_screen(self, engine, *args):
        self.clear_widgets()
        win_widget = WinWidget()
        win_widget.return_btn.bind(on_release=self.load_welcome_screen)
        self.add_widget(win_widget)

    def load_settings_screen(self, *args):
        self.clear_widgets()
        setting_screen_widget = SettingScreenWidget(self.settings)
        setting_screen_widget.return_btn.bind(on_release=self.load_welcome_screen)
        self.add_widget(setting_screen_widget)
        

class GameOverWidget(Widget):
    return_btn = ObjectProperty(None)


class WelcomeWidget(Widget):
    new_game_btn = ObjectProperty(None)


class WinWidget(Widget):
    return_btn = ObjectProperty(None)


class SettingScreenWidget(BoxLayout):
    return_btn = ObjectProperty(None)

    def __init__(self, settings,**kwargs):
        super(SettingScreenWidget,self).__init__(orientation='vertical', spacing=20, padding = (30, 50), **kwargs)
        self.add_widget(Label(text='Settings', font_size = 40, size_hint = (None, None), pos_hint = {'center_x':0.5}))
        self.add_widget(SettingWidget('maze_width', 'maze width:',
                                      5, 50, settings['maze_width'], settings))
        self.add_widget(SettingWidget('maze_height', 'maze height:',
                                      5, 50, settings['maze_height'], settings))
        self.add_widget(SettingWidget('num_enemies', 'number of enemies:',
                                      0, 50, settings['num_enemies'], settings))
        self.add_widget(SettingWidget('num_gold', 'number of gold coins:',
                                      0, 50, settings['num_gold'], settings))
        self.add_widget(SettingWidget('num_crystals', 'number of crystals:',
                                      0, 50, settings['num_crystals'], settings))
        self.add_widget(SettingWidget('enemy_speed', 'enemy speed:',
                                      1, 10, settings['enemy_speed'], settings))
        self.return_btn = Button(text="Done", size=(170,40), size_hint=(None, None), pos_hint = {'center_x':0.5})
        self.add_widget(self.return_btn)


class SettingWidget(BoxLayout):
    slider = ObjectProperty(None)
    desc_label = ObjectProperty(None)
    val_label = ObjectProperty(None)

    def __init__(self, field_name, desc, min_val, max_val, default, settings, **kwargs):
        super(SettingWidget, self).__init__(orientation='horizontal', **kwargs)
        self.slider.min = min_val
        self.slider.max = max_val
        self.slider.value = default
        self.settings = settings
        self.field_name = field_name
        self.settings[self.field_name] = default
        self.val_label.text = str(default)
        self.desc_label.text = desc

        self.slider.bind(value=self.on_val_change)

    def on_val_change(self, *args):
        self.settings[self.field_name] = int(self.slider.value)
        self.val_label.text = str(self.settings[self.field_name])


class EngineWidget(Widget):
    def __init__(self, settings, **kwargs):
        super(EngineWidget, self).__init__(**kwargs)
        self.register_event_type('on_game_over')
        self.register_event_type('on_win')
        self.cell_width = 20
        self.num_enemies = settings['num_enemies']
        self.num_gold = settings['num_gold']
        self.num_crystals = settings['num_crystals']
        self.enemy_speed = settings['enemy_speed']

        self.maze = Maze(2*settings['maze_width'] + 1, 2*settings['maze_height'] + 1)
        self.maze.generate()

        with self.canvas:
            for segment in self.maze.get_wall_segments():
                x1, y1, x2, y2 = tuple((val + 0.5) * self.cell_width
                    for val in segment)
                if x1 > x2:
                    Line(points=(x1, y1, x1 + 0.5*self.cell_width, y1))
                    Line(points=(x2 - 0.5*self.cell_width, y2, x2, y2))
                elif y1 > y2:
                    Line(points=(x1, y1, x1, y1 + 0.5*self.cell_width))
                    Line(points=(x2, y2 - 0.5*self.cell_width, x2, y2))
                else:
                    Line(points = (x1, y1, x2, y2))

        empty_cells = itertools.cycle(self.maze.get_empty_cells())

        x,y = next(empty_cells)
        player = Player(x, y, self.maze)
        self.player_widget = PlayerWidget(player, engine=self)
        self.add_widget(self.player_widget)

        self.non_player_object_widgets =[]

        for i in range(0, self.num_enemies):
            x,y = next(empty_cells)
            enemy_widget = EnemyWidget(Enemy(x, y, self.maze), speed=self.enemy_speed, engine=self)
            self.non_player_object_widgets.append(enemy_widget)
            self.add_widget(enemy_widget)

        for i in range(0, self.num_gold):
            x,y = next(empty_cells)
            gold_widget = GoldWidget(Gold(x, y, self.maze))
            self.non_player_object_widgets.append(gold_widget)
            self.add_widget(gold_widget)

        for i in range(0, self.num_crystals):
            x,y = next(empty_cells)
            crystal_widget = CrystalWidget(Crystal(x, y, self.maze))
            self.non_player_object_widgets.append(crystal_widget)
            self.add_widget(crystal_widget)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.update_event = Clock.schedule_interval(self.update, 0.01)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] in ['up', 'down', 'left', 'right']:
            self.player_widget.move(keycode[1])

    def remove_game_object(self, game_object_widget):
        self.non_player_object_widgets.remove(game_object_widget)
        self.remove_widget(game_object_widget)

    def check_collisions(self):
        for widget in self.non_player_object_widgets:
            if widget.collide_widget(self.player_widget):
                widget.game_object.collide(self.player_widget.game_object)

    def update(self, *args):
        self.check_collisions()
        self.player_widget.check_state(self)
        for widget in self.non_player_object_widgets:
            widget.check_state(self)

    def on_game_over(self, *args):
        print("you lose")
        self.update_event.cancel()

    def on_win(self, *args):
        print("you win")
        self.update_event.cancel()

    def check_pos(self, game_object, *args):
        game_object.x = game_object.x % (self.maze.width * self.cell_width)
        game_object.y = game_object.y % (self.maze.height * self.cell_width)


class GameObjectWidget(Widget):
    def __init__(self, game_object, **kwargs):
        super(GameObjectWidget, self).__init__(**kwargs)
        self.game_object = game_object
        self.pos = (20*self.game_object.x+10, 20*self.game_object.y+10)

    def check_state(self, engine):
        if self.game_object.marked_for_removal:
            engine.remove_game_object(self)


class MovingGameObjectWidget(GameObjectWidget):
    def __init__(self, game_object, speed=11, engine=None, **kwargs):
        super(MovingGameObjectWidget, self).__init__(game_object, **kwargs)
        self.step_time = 0.6 - 0.05 * speed
        self.bind(pos=engine.check_pos)

    def animate(self, direction):
        old_x, old_y = self.game_object.prev_loc
        new_x, new_y = old_x, old_y
        if direction == 'up':
            new_y += 1
        elif direction == 'right':
            new_x += 1
        elif direction == 'down':
            new_y -= 1
        elif direction == 'left':
            new_x -= 1
        animation = Animation(x = 20 * new_x + 10,
                              y = 20 * new_y + 10,
                              d = self.step_time)
        animation.start(self)

    def move(self, *args):
        direction = self.game_object.move(*args)
        self.animate(direction)



class PlayerWidget(MovingGameObjectWidget):
    def __init__(self, player, **kwargs):
        super(PlayerWidget, self).__init__(player, **kwargs)
        self.has_crystal = False

    def check_state(self, engine):
        if self.game_object.marked_for_removal:
            engine.dispatch('on_game_over')
        if self.game_object.gold >= engine.num_gold:
            engine.dispatch('on_win')
        if self.game_object.has_crystal != self.has_crystal:
            self.has_crystal = self.game_object.has_crystal
            color = (0, 1, 1) if self.has_crystal else (0, 1, 0)
            self.canvas.get_group("color")[0].rgb = color


class EnemyWidget(MovingGameObjectWidget):
    def __init__(self, enemy, speed=11, **kwargs):
        super(EnemyWidget, self).__init__(enemy, speed=speed, **kwargs)
        self.move_event = Clock.schedule_interval(self.move, self.step_time)

    def check_state(self, engine):
        super(EnemyWidget, self).check_state(engine)
        if self.game_object.marked_for_removal:
            self.move_event.cancel()


class GoldWidget(GameObjectWidget):
    pass


class CrystalWidget(GameObjectWidget):
    pass



class EzamApp(App):
    def build(self):
        return GameWidget()


if __name__ == '__main__':
    EzamApp().run()