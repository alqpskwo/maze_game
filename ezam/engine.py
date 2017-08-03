from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Line, Rectangle, Color
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty
import time
import datetime
import itertools
import pdb
from maze import Maze, Player, Enemy, Gold, Crystal

# Width in pixels of a single cell in the maze
CELL_WIDTH = 20

class StatusBarWidget(BoxLayout):
    """
    Widget displaying the score and time of an active game.
    """
    score_label = ObjectProperty(None)
    time_label = ObjectProperty(None)

    def __init__(self, start_time, **kwargs):
        super(StatusBarWidget, self).__init__(orientation='horizontal', 
                                              **kwargs)
        self.start_time = start_time
        Clock.schedule_interval(self.update_time, 0.01)
    
    def update_score(self, engine, *args):
        """
        Update the score label to show the current score.
        """
        #pdb.set_trace()
        self.score_label.text = "Gold: {}/{}".format(str(engine.score),
                                                     str(engine.win_score))

    def update_time(self, *args):
        """
        Update the time label to show the current game time.
        """
        s = int(time.time() - self.start_time)
        self.time_label.text = str(datetime.timedelta(seconds=s))


class EngineWidget(Widget):
    """
    Manages all aspects of gameplay and game display.
    """
    score = NumericProperty(0)

    def __init__(self, settings, **kwargs):
        super(EngineWidget, self).__init__(**kwargs)
        # Register game-ending events.
        self.register_event_type('on_game_over')
        self.register_event_type('on_win')

        # Store some important values.
        self.win_score = settings['num_gold']
        self.start_time = time.time()

        # Create maze widget.
        maze = Maze(2 * settings['maze_width'] + 1,
                         2 * settings['maze_height'] + 1)
        maze.generate()
        self.maze_widget = MazeWidget(maze)
        self.add_widget(self.maze_widget, 1)


        # Get a cycling list of the empty cells in the maze in a random order;
        # this is used to place game objects in the maze so that they do not
        # overlap unless necessary.
        empty_cells = itertools.cycle(maze.get_empty_cells())

        # Create player widget.
        x,y = next(empty_cells)
        player = Player(x, y, maze)
        self.player_widget = PlayerWidget(player, self)
        self.add_widget(self.player_widget, 2)

        self.non_player_object_widgets =[]

        # Create enemy widgets.
        for i in range(0, settings['num_enemies']):
            x,y = next(empty_cells)
            enemy_widget = EnemyWidget(Enemy(x, y, maze),
                                       self,
                                       speed=settings['enemy_speed'])
            self.non_player_object_widgets.append(enemy_widget)
            self.add_widget(enemy_widget, 3)

        # Create gold widgets.
        for i in range(0, settings['num_gold']):
            x,y = next(empty_cells)
            gold_widget = GoldWidget(Gold(x, y, maze), self)
            self.non_player_object_widgets.append(gold_widget)
            self.add_widget(gold_widget, 4)

        # Create crystal widgets.
        for i in range(0, settings['num_crystals']):
            x,y = next(empty_cells)
            crystal_widget = CrystalWidget(Crystal(x, y, maze), self)
            self.non_player_object_widgets.append(crystal_widget)
            self.add_widget(crystal_widget, 5)


        # reposition player when window is resized
        self.center_player()
        self.bind(size=self.center_player)

        # bind relevant keyboard events
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
        
        self.maze_widget.x = self.player_widget.x - self.player_widget.rel_x
        self.maze_widget.y = self.player_widget.y - self.player_widget.rel_y
        self.maze_widget.redraw()

        for widget in self.non_player_object_widgets:
            widget.pos = (widget.rel_x + self.maze_widget.x,
                          widget.rel_y + self.maze_widget.y)

        self.check_collisions()
        self.player_widget.check_state()
        for widget in self.non_player_object_widgets:
            widget.check_state()

    def on_game_over(self, *args):
        print("you lose")
        self.update_event.cancel()

    def on_win(self, *args):
        self.update_event.cancel()

    def center_player(self, *args):
        self.player_widget.pos = (self.width / 2, self.height / 2)
        

class MazeWidget(Widget):
    """
    Widget for rendering an abstract maze object.
    """
    def __init__(self, maze, **kwargs):
        super(MazeWidget, self).__init__(**kwargs)
        self.maze = maze
        self.canvas_instructions = []
        with self.canvas:
                Color(rgb=(1,1,1,1))
                for segment in self.maze.get_wall_segments():
                    x1, y1, x2, y2 = tuple((val + 0.5) * CELL_WIDTH
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
    """
    A generic game item in a maze. Should be subclassed.
    """
    rel_x = NumericProperty(None)
    rel_y = NumericProperty(None)

    def __init__(self, game_object, engine, **kwargs):
        super(GameObjectWidget, self).__init__(**kwargs)
        self.game_object = game_object
        self.rel_x = CELL_WIDTH*(self.game_object.x + 0.5)
        self.rel_y = CELL_WIDTH*(self.game_object.y + 0.5)
        self.engine = engine
        self.animation_queue = []

    def check_state(self):
        if self.game_object.marked_for_removal:
            self.engine.remove_game_object(self)


class MovingGameObjectWidget(GameObjectWidget):
    """
    A game object that moves.
    """
    def __init__(self, game_object, engine, speed=10, **kwargs):
        super(MovingGameObjectWidget, self).__init__(game_object,
                                                     engine,
                                                     **kwargs)
        self.step_time = 0.6 - 0.05 * speed
        self.animating = False
        self.animation_queue = []
        

    def add_animation(self):
        animation = Animation(rel_x = CELL_WIDTH * (self.game_object.x + 0.5),
                              rel_y = CELL_WIDTH * (self.game_object.y + 0.5),
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
    """
    Represents the player in the maze.
    """
    def __init__(self, player, engine, **kwargs):
        super(PlayerWidget, self).__init__(player, engine, **kwargs)
        self.has_crystal = False
        self.gold = -1
        self.direction = set()
        self.move_event = Clock.schedule_interval(self.move, 0.01)

    def check_state(self):
        if self.game_object.marked_for_removal:
            self.engine.dispatch('on_game_over')
        if self.game_object.gold >= self.engine.win_score:
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
    """
    Represents an enemy monster.
    """
    def __init__(self, enemy, engine, speed=10, **kwargs):
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