from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
import time
import datetime
import pdb
from engine import EngineWidget, StatusBarWidget
from screens import WelcomeWidget, SettingsScreenWidget,\
    WinWidget, GameOverWidget


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
        
        status_bar.update_score(engine)
        self.clear_widgets()
        self.add_widget(status_bar, 0 )
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
        settings_widget = SettingsScreenWidget(self.settings)
        settings_widget.return_btn.bind(on_release=self.load_welcome_screen)
        self.add_widget(settings_widget)
        

class EzamApp(App):
    def build(self):
        return GameWidget()


if __name__ == '__main__':
    EzamApp().run()