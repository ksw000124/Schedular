# -*- coding: utf-8 -*-

import platform
import json
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from .components.pie_chart import PieChart
from .components.matrix import Matrix
from .components.time_control_panel import TimeControlPanel
from .components.font_control_panel import FontControlPanel
from .components.task_control_panel import TaskControlPanel


class EisenhowerVisualizer:
    def __init__(self, task_manager):
        self.task_manager = task_manager
        self.fig = None
        self.pie_chart = None
        self.matrix = None

        config_path = os.path.join(os.path.dirname(
            __file__), 'config', 'properties.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.base_font_size = config['font_size']

        self._setup_fonts()

    def _setup_fonts(self):
        extension = ".ttf" if platform.system() == "Windows" else ".otf"
        font_path = f"./eisenhower/fonts/Maplestory Light{extension}"
        fm.fontManager.addfont(font_path)
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
        plt.rcParams['font.size'] = self.base_font_size
        plt.rcParams['axes.unicode_minus'] = False

    def setup_initial_plot(self):
        self.fig, axes = plt.subplots(1, 2, figsize=(17, 10))

        self.pie_chart = PieChart(axes[0])
        self.matrix = Matrix(axes[1])
        self.matrix.setup_interaction(self.task_manager, self._update_plots)

        self._setup_control_panels()
        self._setup_layout()
        self._update_plots(self.task_manager.available_minutes)

    def _setup_control_panels(self):
        self.time_control = TimeControlPanel(
            self.fig,
            self.on_slider_changed,
            self.task_manager.available_minutes
        )

        self.font_control = FontControlPanel(
            self.fig,
            self._update_font_size,
            self.base_font_size
        )
        self.font_control.add_component(self.pie_chart)
        self.font_control.add_component(self.matrix)

        self.task_control = TaskControlPanel(
            self.fig,
            self.add_task,
            self.reset
        )

    def _setup_layout(self):
        plt.subplots_adjust(left=0.05, right=0.95,
                            top=0.95, bottom=0.25, wspace=0.2)

    def _update_plots(self, total_minutes):
        df_updated, sorted_colors = self.task_manager.recalculate_time(
            total_minutes)

        self.pie_chart.draw(
            self.task_manager.tasks,
            self.task_manager.available_hours,
            self.task_manager.available_minutes_part,
            sorted_colors
        )

        self.matrix.draw(self.task_manager.tasks, sorted_colors)
        self.fig.canvas.draw()

    def on_slider_changed(self, val):
        self._update_plots(val)
        self.pie_chart.ax.set_title(
            f"오늘의 일정 (총 {val//60}시간 {val%60}분)",
            fontsize=self.font_control.font_size * 1.5
        )
        self.fig.canvas.draw_idle()

    def _update_font_size(self, font_mult):
        plt.rcParams['font.size'] = self.base_font_size * font_mult
        self.fig.canvas.draw_idle()

    def add_task(self, task_data):
        self.task_manager.add_task(task_data)
        self._update_plots(self.task_manager.available_minutes)

    def reset(self):
        self.task_manager.reset()
        self._update_plots(self.task_manager.available_minutes)

    def show(self):
        self.setup_initial_plot()
        plt.show()
