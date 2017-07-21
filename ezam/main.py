from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Line, Rectangle, Color
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty
from maze import Maze, Player, Enemy, Gold, Crystal
import time
import datetime
import itertools
import pdb


class GameWidget(AnchorLayout):
    def __init__(self, **kwargs):
        super(GameWidget, self).__init__(anchor_y='top', **kwargs)
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
        status_bar = StatusBarWidget(engine.start_time)
        engine.bind(score=status_bar.update_score)
        Clock.schedule_interval(status_bar.update_time, 0.01)
        status_bar.update_score(engine)
        self.clear_widgets()
        self.add_widget(status_bar, 0, )
        self.add_widget(engine, 1)
        
        

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
        total_s = int(time.time() - engine.start_time)
        total_time = str(datetime.timedelta(seconds=total_s))
        self.clear_widgets()
        win_widget = WinWidget(total_time)
        win_widget.return_btn.bind(on_release=self.load_welcome_screen)
        self.add_widget(win_widget)

    def load_settings_screen(self, *args):
        self.clear_widgets()
        settings_screen_widget = SettingsScreenWidget(self.settings)
        settings_screen_widget.return_btn.bind(on_release=self.load_welcome_screen)
        self.add_widget(settings_screen_widget)

class StatusBarWidget(BoxLayout):
    score_label = ObjectProperty(None)
    time_label = ObjectProperty(None)

    def __init__(self, start_time, **kwargs):
        super(StatusBarWidget, self).__init__(orientation='horizontal', **kwargs)
        self.start_time = start_time
    
    def update_score(self, engine, *args):
        #pdb.set_trace()
        self.score_label.text = "Gold: {}/{}".format(str(engine.score), str(engine.num_gold))

    def update_time(self, *args):
        s = int(time.time() - self.start_time)
        self.time_label.text = str(datetime.timedelta(seconds=s))
        

class GameOverWidget(Widget):
    return_btn = ObjectProperty(None)



class WelcomeWidget(Widget):
    new_game_btn = ObjectProperty(None)


class WinWidget(Widget):
    return_btn = ObjectProperty(None)
    time_label = ObjectProperty(None)
    def __init__(self, total_time, **kwargs):
        super(WinWidget, self).__init__(**kwargs)
        self.time_label.text = "You completed the maze in {}".format(total_time)


class SettingsScreenWidget(Widget):
    return_btn = ObjectProperty(None)
    settings_box = ObjectProperty(None)

    def __init__(self, settings,**kwargs):
        super(SettingsScreenWidget,self).__init__(**kwargs)
        self.settings_box.add_widget(SettingWidget('maze_width', 'maze width:',
                                      5, 50, settings['maze_width'], settings))
        self.settings_box.add_widget(SettingWidget('maze_height', 'maze height:',
                                      5, 50, settings['maze_height'], settings))
        self.settings_box.add_widget(SettingWidget('num_enemies', 'number of enemies:',
                                      0, 50, settings['num_enemies'], settings))
        self.settings_box.add_widget(SettingWidget('num_gold', 'number of gold coins:',
                                      0, 50, settings['num_gold'], settings))
        self.settings_box.add_widget(SettingWidget('num_crystals', 'number of crystals:',
                                      0, 50, settings['num_crystals'], settings))
        self.settings_box.add_widget(SettingWidget('enemy_speed', 'enemy speed:',
                                      1, 10, settings['enemy_speed'], settings))
        self.return_btn = Button(text="Done", size=(170,40), size_hint=(None, None), pos_hint = {'center_x':0.5})
        self.settings_box.add_widget(self.return_btn)


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
    score = NumericProperty(0)

    def __init__(self, settings, **kwargs):
        super(EngineWidget, self).__init__(**kwargs)
        self.register_event_type('on_game_over')
        self.register_event_type('on_win')
        self.cell_width = 20
        self.num_enemies = settings['num_enemies']
        self.num_gold = settings['num_gold']
        self.num_crystals = settings['num_crystals']
        self.enemy_speed = settings['enemy_speed']
        self.start_time = time.time()

        self.maze = Maze(2*settings['maze_width'] + 1, 2*settings['maze_height'] + 1)
        self.maze.generate()


        self.maze_widget = MazeWidget(self.maze, self.cell_width)
        self.add_widget(self.maze_widget, 1)


        empty_cells = itertools.cycle(self.maze.get_empty_cells())

        x,y = next(empty_cells)
        player = Player(x, y, self.maze)
        self.player_widget = PlayerWidget(player, self)
        self.add_widget(self.player_widget, 2)
        self.on_resize()
        self.bind(size=self.on_resize)

        self.non_player_object_widgets =[]

        for i in range(0, self.num_enemies):
            x,y = next(empty_cells)
            enemy_widget = EnemyWidget(Enemy(x, y, self.maze), self, speed=self.enemy_speed)
            self.non_player_object_widgets.append(enemy_widget)
            self.add_widget(enemy_widget, 3)

        for i in range(0, self.num_gold):
            x,y = next(empty_cells)
            gold_widget = GoldWidget(Gold(x, y, self.maze), self)
            self.non_player_object_widgets.append(gold_widget)
            self.add_widget(gold_widget, 4)

        for i in range(0, self.num_crystals):
            x,y = next(empty_cells)
            crystal_widget = CrystalWidget(Crystal(x, y, self.maze), self)
            self.non_player_object_widgets.append(crystal_widget)
            self.add_widget(crystal_widget, 5)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down,
                            on_key_up = self._on_keyboard_up)

        self.update_event = Clock.schedule_interval(self.update, 0.01)


    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] in ['up', 'down', 'left', 'right']:
            self.player_widget.direction.add(keycode[1])
            self.player_widget.move()

    def _on_keyboard_up(self, keyboard, keycode, *args):
        if keycode[1] in ['up', 'down', 'left', 'right']:
            self.player_widget.direction.discard(keycode[1])


    def remove_game_object(self, game_object_widget):
        self.non_player_object_widgets.remove(game_object_widget)
        self.remove_widget(game_object_widget)

    def check_collisions(self):
        for widget in self.non_player_object_widgets:
            if widget.collide_widget(self.player_widget):
                widget.game_object.collide(self.player_widget.game_object)

    def update(self, *args):
        
        self.maze_widget.x = self.player_widget.x - self.player_widget.relative_x
        self.maze_widget.y = self.player_widget.y - self.player_widget.relative_y
        self.maze_widget.redraw()

        for widget in self.non_player_object_widgets:
            widget.pos = (widget.relative_x + self.maze_widget.x,
                          widget.relative_y + self.maze_widget.y)

        self.check_collisions()
        self.player_widget.check_state()
        for widget in self.non_player_object_widgets:
            widget.check_state()



    def on_game_over(self, *args):
        print("you lose")
        self.update_event.cancel()

    def on_win(self, *args):
        print("you win")
        self.update_event.cancel()

    def on_resize(self, *args):
        self.player_widget.pos = (self.width / 2, self.height / 2)
        

class MazeWidget(Widget):
    def __init__(self, maze, cell_width, **kwargs):
        super(MazeWidget, self).__init__(**kwargs)
        self.maze = maze
        self.canvas_instructions = []
        with self.canvas:
                Color(rgb=(1,1,1,1))
                for segment in self.maze.get_wall_segments():
                    x1, y1, x2, y2 = tuple((val + 0.5) * cell_width
                        for val in segment)
                    
                    l = Line(points = (x1, y1, x2, y2))
                    self.canvas_instructions.append((l, l.points[:]))

    def redraw(self):
        for (line, points) in self.canvas_instructions:
            new_points = []
            xy_cycle = itertools.cycle([self.x, self.y])
            for coord in points:
                new_points.append(next(xy_cycle) + coord)
            line.points = new_points


class GameObjectWidget(Widget):
    relative_x = NumericProperty(None)
    relative_y = NumericProperty(None)

    def __init__(self, game_object, engine, **kwargs):
        super(GameObjectWidget, self).__init__(**kwargs)
        self.game_object = game_object
        self.relative_x = 20*self.game_object.x+10
        self.relative_y = 20*self.game_object.y+10
        self.engine = engine
        self.animation_queue = []

    def check_state(self):
        if self.game_object.marked_for_removal:
            self.engine.remove_game_object(self)


class MovingGameObjectWidget(GameObjectWidget):
    def __init__(self, game_object, engine, speed=10, **kwargs):
        super(MovingGameObjectWidget, self).__init__(game_object, engine, **kwargs)
        self.step_time = 0.6 - 0.05 * speed
        self.animating = False
        self.animation_queue = []
        

    def add_animation(self):
        animation = Animation(relative_x = 20 * self.game_object.x + 10,
                              relative_y = 20 * self.game_object.y + 10,
                              d = self.step_time)

        animation.bind(on_complete=self.on_animation_complete)
        self.animation_queue.append(animation)
        self.animate()

    def animate(self):
        if (not self.animating) and len(self.animation_queue) > 0:
            animation = self.animation_queue.pop(0)
            self.animating = True
            animation.start(self)

    def move(self, *args):
        moved = self.game_object.move(*args)
        if moved:
            self.add_animation()

    def on_animation_complete(self, *args):
        self.animating = False
        self.animate()




class PlayerWidget(MovingGameObjectWidget):
    def __init__(self, player, engine, **kwargs):
        super(PlayerWidget, self).__init__(player, engine, **kwargs)
        self.has_crystal = False
        self.gold = -1
        self.direction = set()
        self.move_event = Clock.schedule_interval(self.move, 0.01)

    def check_state(self):
        if self.game_object.marked_for_removal:
            self.engine.dispatch('on_game_over')
        if self.game_object.gold >= self.engine.num_gold:
            self.engine.dispatch('on_win')
        if self.game_object.has_crystal != self.has_crystal:
            self.has_crystal = self.game_object.has_crystal
            color = (0, 1, 1) if self.has_crystal else (0, 1, 0)
            self.canvas.get_group("color")[0].rgb = color
        if self.engine.score != self.game_object.gold:
            self.engine.score = self.game_object.gold

    def move(self, *args):
        if not self.animating and self.direction:
            for direction in self.direction:
                super(PlayerWidget, self).move(direction)



class EnemyWidget(MovingGameObjectWidget):
    def __init__(self, enemy, engine, speed=11, **kwargs):
        super(EnemyWidget, self).__init__(enemy, engine, speed=speed, **kwargs)
        self.move_event = Clock.schedule_interval(self.move, self.step_time)
        

    def check_state(self):
        super(EnemyWidget, self).check_state()
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