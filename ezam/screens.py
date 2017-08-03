from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty

class GameOverWidget(Widget):
    return_btn = ObjectProperty(None)


class WelcomeWidget(Widget):
    new_game_btn = ObjectProperty(None)


class WinWidget(Widget):
    return_btn = ObjectProperty(None)
    time_label = ObjectProperty(None)
    def __init__(self, total_time, **kwargs):
        super(WinWidget, self).__init__(**kwargs)
        self.time_label.text = "You completed the maze in {}"\
                               .format(total_time)


class SettingsScreenWidget(Widget):
    return_btn = ObjectProperty(None)
    settings_box = ObjectProperty(None)

    def __init__(self, settings,**kwargs):
        super(SettingsScreenWidget,self).__init__(**kwargs)

        widget = SettingWidget('maze_width', 'maze width:', 5, 50, 
                               settings['maze_width'], settings)
        self.settings_box.add_widget(widget)

        widget = SettingWidget('maze_height', 'maze height:', 5, 50,
                               settings['maze_height'], settings)
        self.settings_box.add_widget(widget)

        widget = SettingWidget('num_enemies', 'number of enemies:', 0, 50,
                               settings['num_enemies'], settings)
        self.settings_box.add_widget(widget)

        widget = SettingWidget('num_gold', 'number of gold coins:', 1, 50,
                               settings['num_gold'], settings)
        self.settings_box.add_widget(widget)

        widget = SettingWidget('num_crystals', 'number of crystals:', 0, 50,
                               settings['num_crystals'], settings)
        self.settings_box.add_widget(widget)

        widget = SettingWidget('enemy_speed', 'enemy speed:', 1, 10,
                               settings['enemy_speed'], settings)
        self.settings_box.add_widget(widget)

        self.return_btn = Button(text="Done", size=(170,40),
                                 size_hint=(None, None),
                                 pos_hint = {'center_x':0.5})
        self.settings_box.add_widget(self.return_btn)


class SettingWidget(BoxLayout):
    slider = ObjectProperty(None)
    desc_label = ObjectProperty(None)
    val_label = ObjectProperty(None)

    def __init__(self, field_name, desc,
                 min_val, max_val, default,
                 settings, **kwargs):
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