# -*- coding: utf-8 -*-


import random
import platform
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.widgets import Button, Slider, TextBox

from .ui.task_input_dialog import TaskInputDialog, QDialog
from .components.pie_chart import PieChart
from .components.matrix import Matrix


class EisenhowerVisualizer:
    def __init__(self, task_manager):
        self.task_manager = task_manager
        self.fig = None
        self.pie_chart = None
        self.matrix = None
        self.selected_point = None
        self.is_dragging = False
        self.last_update_time = 0
        self.update_interval = 0.05
        self.base_font_size = 12
        self.font_mult = 1.0
        self.background = None  # blit을 위한 배경 저장

        # 폰트 설정
        self._setup_fonts()

    def _setup_fonts(self):
        # Maplestory 폰트 로드
        extension = ".ttf" if platform.system() == "Windows" else ".otf"
        font_path = f"./eisenhower/fonts/Maplestory Light{extension}"
        fm.fontManager.addfont(font_path)
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
        plt.rcParams['font.size'] = self.base_font_size * self.font_mult
        plt.rcParams['axes.unicode_minus'] = False

    def setup_initial_plot(self):
        # 그림과 축 설정
        self.fig, axes = plt.subplots(1, 2, figsize=(17, 10))

        # 파이 차트와 매트릭스 초기화
        self.pie_chart = PieChart(axes[0], self.base_font_size)
        self.matrix = Matrix(axes[1], self.base_font_size)

        # 초기 데이터로 그리기
        self._update_plots(self.task_manager.available_minutes)

        # 레이아웃 조정
        plt.subplots_adjust(left=0.05, right=0.95,
                            top=0.95, bottom=0.25, wspace=0.2)

        # 인터랙션 설정
        self.setup_interaction()

        # 배경 저장 (점을 그리기 전에)
        self.fig.canvas.draw()
        self.background = self.fig.canvas.copy_from_bbox(self.matrix.ax.bbox)

        # 점 그리기
        _, sorted_colors = self.task_manager.recalculate_time(
            self.task_manager.available_minutes)
        self.matrix.draw(self.task_manager.tasks, sorted_colors)

    def _update_plots(self, total_minutes):
        """플롯 업데이트"""
        # 시간 재계산
        df_updated, sorted_colors = self.task_manager.recalculate_time(
            total_minutes)

        # 파이 차트 업데이트
        self.pie_chart.draw(
            self.task_manager.tasks,
            self.task_manager.available_hours,
            self.task_manager.available_minutes_part,
            sorted_colors
        )

        # 매트릭스 업데이트
        self.matrix.draw(self.task_manager.tasks, sorted_colors)

        # 폰트 크기 설정 유지
        plt.rcParams['font.size'] = self.base_font_size * self.font_mult
        self.update_all_text_sizes()

        # 배경 업데이트
        self.fig.canvas.draw()
        self.background = self.fig.canvas.copy_from_bbox(self.matrix.ax.bbox)

    def setup_interaction(self):
        # 이벤트 핸들러 연결
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)

        # 슬라이더 설정
        ax_slider = plt.axes([0.15, 0.1, 0.69, 0.05])
        self.slider = Slider(
            ax_slider,
            '총 시간 (분)',
            30, 600,
            valinit=self.task_manager.available_minutes,
            valstep=5,
            color='#00a0a0',
            initcolor='none'
        )
        self.slider.on_changed(self.on_slider_changed)

        # 시간 입력 필드 설정
        time_input_ax = plt.axes([0.85, 0.1, 0.1, 0.05])
        self.time_input = TextBox(
            time_input_ax,
            '',
            initial=str(self.task_manager.available_minutes),
            color='white',
            hovercolor='#f0f0f0'
        )
        self.time_input.on_submit(self.on_time_input_changed)

        # 리셋 버튼 설정
        reset_ax = plt.axes([0.85, 0.02, 0.1, 0.05])
        self.reset_button = Button(
            reset_ax,
            'Reset',
            color='#f0f0f0',
            hovercolor='#d0f0f0'
        )
        self.reset_button.on_clicked(self.reset)

        # 폰트 크기 버튼 설정
        font_size_increase_ax = plt.axes([0.6, 0.02, 0.1, 0.05])
        self.font_size_increase_button = Button(
            font_size_increase_ax,
            '폰트 크기 +',
            color='#f0f0f0',
            hovercolor='#d0f0f0'
        )
        self.font_size_increase_button.on_clicked(self.increase_font_size)

        font_size_decrease_ax = plt.axes([0.7, 0.02, 0.1, 0.05])
        self.font_size_decrease_button = Button(
            font_size_decrease_ax,
            '폰트 크기 -',
            color='#f0f0f0',
            hovercolor='#d0f0f0'
        )
        self.font_size_decrease_button.on_clicked(self.decrease_font_size)

        # 할 일 추가 버튼 설정
        add_task_ax = plt.axes([0.5, 0.02, 0.1, 0.05])
        self.add_task_button = Button(
            add_task_ax,
            '할 일 추가',
            color='#f0f0f0',
            hovercolor='#d0f0f0'
        )
        self.add_task_button.on_clicked(self.add_task)

    def on_slider_changed(self, val):
        # 슬라이더 값 변경 시 호출 - 부드러운 업데이트
        import time
        current_time = time.time()

        # 업데이트 간격 조절 (throttling)
        if current_time - self.last_update_time > self.update_interval:
            self.last_update_time = current_time
            self._update_plots(val)
            # 입력 필드 값도 업데이트
            self.time_input.set_val(str(int(val)))
            # 파이 차트 제목 업데이트
            self.pie_chart.ax.set_title(
                f"오늘의 일정 (총 {val//60}시간 {val%60}분)",
                fontsize=self.base_font_size * self.font_mult * 1.5
            )
            self.fig.canvas.draw_idle()

    def on_time_input_changed(self, text):
        """시간 입력 필드 값 변경 시 호출"""
        try:
            minutes = int(text)
            if 30 <= minutes <= 600:
                self.task_manager.available_minutes = minutes
                self._update_plots(minutes)
                # 슬라이더 값도 업데이트
                self.slider.set_val(minutes)
                # 파이 차트 제목 업데이트
                self.pie_chart.ax.set_title(
                    f"오늘의 일정 (총 {minutes//60}시간 {minutes%60}분)",
                    fontsize=self.base_font_size * self.font_mult * 1.5
                )
                self.fig.canvas.draw_idle()
        except ValueError:
            # 유효하지 않은 입력은 무시
            pass

    def on_press(self, event):
        if event.inaxes != self.matrix.ax:
            return

        # 클릭한 위치에서 가장 가까운 점 찾기
        point = self.matrix.get_point_at_position(event.xdata, event.ydata)
        if point is not None:
            self.selected_point = point
            self.is_dragging = True
            point.highlight(True)

            # 선택된 점을 제외한 배경 저장
            if self.selected_point.scatter is not None:
                self.selected_point.scatter.remove()
            if self.selected_point.text is not None:
                self.selected_point.text.remove()

            self.fig.canvas.draw()
            self.background = self.fig.canvas.copy_from_bbox(
                self.matrix.ax.bbox)

            # 선택된 점 다시 추가
            self.selected_point.scatter = self.matrix.ax.scatter(
                event.xdata,
                event.ydata,
                s=self.selected_point.task.assigned_time * 10,
                color=self.selected_point.color,
                alpha=1.0,
                edgecolors='black',
                linewidths=1
            )
            hours = self.selected_point.task.assigned_time // 60
            minutes = self.selected_point.task.assigned_time % 60
            self.selected_point.text = self.matrix.ax.text(
                event.xdata,
                event.ydata + 0.2,
                f'{self.selected_point.task.name}\n{hours}시간 {minutes}분',
                fontsize=self.base_font_size * self.font_mult,
                ha='center'
            )

            # 변경된 영역만 업데이트
            self.fig.canvas.blit(self.matrix.ax.bbox)

    def on_motion(self, event):
        if not self.is_dragging or self.selected_point is None or event.inaxes != self.matrix.ax:
            return

        if event.xdata is None or event.ydata is None:
            return

        # 범위 제한 (0.5 ~ 5.5)
        x_val = min(max(event.xdata, 0.5), 5.5)
        y_val = min(max(event.ydata, 0.5), 5.5)

        # 점 위치 업데이트
        self.selected_point.update_position(x_val, y_val)

        # 배경 복원
        self.fig.canvas.restore_region(self.background)

        # 점 위치 업데이트
        self.selected_point.scatter.set_offsets([[x_val, y_val]])
        if self.selected_point.text is not None:
            self.selected_point.text.set_position((x_val, y_val + 0.2))

        # 변경된 점만 다시 그리기
        self.matrix.ax.draw_artist(self.selected_point.scatter)
        if self.selected_point.text is not None:
            self.matrix.ax.draw_artist(self.selected_point.text)

        # 변경된 영역만 업데이트
        self.fig.canvas.blit(self.matrix.ax.bbox)

    def on_release(self, event):
        if self.selected_point is not None:
            # 가장 가까운 그리드 좌표 계산
            x_val = round(self.selected_point.task.urgency)
            y_val = round(self.selected_point.task.importance)

            # 범위 제한 (1 ~ 5)
            x_val = min(max(x_val, 1), 5)
            y_val = min(max(y_val, 1), 5)

            # 긴급도가 0이면 작업 제거
            if x_val == 0:
                task_name = self.selected_point.task.name
                self.task_manager.remove_task(task_name)
            else:
                # 점 위치 업데이트
                self.selected_point.update_position(x_val, y_val)
                self.task_manager.update_task_position(
                    self.selected_point.task.name,
                    x_val,
                    y_val
                )

            self.selected_point.highlight(False)
            self._update_plots(self.task_manager.available_minutes)

            # 배경 업데이트
            self.fig.canvas.draw()
            self.background = self.fig.canvas.copy_from_bbox(
                self.matrix.ax.bbox)

            self.selected_point = None
            self.is_dragging = False

    def reset(self, event):
        # 리셋 버튼 클릭 시 호출
        self.task_manager.tasks = []
        self.task_manager._save_tasks()
        self._update_plots(self.task_manager.available_hours *
                           60 + self.task_manager.available_minutes_part)

    def increase_font_size(self, event):
        # 폰트 크기 배수 증가
        self.font_mult = min(2.0, self.font_mult + 0.1)
        plt.rcParams['font.size'] = self.base_font_size * self.font_mult

        # 모든 텍스트 요소 업데이트
        self.update_all_text_sizes()
        self.fig.canvas.draw_idle()

    def decrease_font_size(self, event):
        # 폰트 크기 배수 감소
        self.font_mult = max(0.1, self.font_mult - 0.1)
        plt.rcParams['font.size'] = self.base_font_size * self.font_mult

        # 모든 텍스트 요소 업데이트
        self.update_all_text_sizes()
        self.fig.canvas.draw_idle()

    def update_all_text_sizes(self):
        # 파이 차트 텍스트 업데이트
        for text in self.pie_chart.ax.texts:
            text.set_fontsize(self.base_font_size * self.font_mult)

        # 매트릭스 텍스트 업데이트
        for text in self.matrix.ax.texts:
            text.set_fontsize(self.base_font_size * self.font_mult)

        # 축 라벨과 제목 업데이트
        self.pie_chart.ax.set_title(
            f"오늘의 일정 (총 {self.task_manager.available_hours}시간 {self.task_manager.available_minutes_part}분)",
            fontsize=self.base_font_size * self.font_mult * 1.5
        )
        self.matrix.ax.set_title(
            "할 일",
            fontsize=self.base_font_size * self.font_mult * 1.5
        )
        self.matrix.ax.set_xlabel(
            "긴급도",
            fontsize=self.base_font_size * self.font_mult
        )
        self.matrix.ax.set_ylabel(
            "중요도",
            fontsize=self.base_font_size * self.font_mult
        )

        # 눈금 라벨 업데이트
        self.matrix.ax.tick_params(
            axis='both',
            which='major',
            labelsize=self.base_font_size * self.font_mult
        )

    def add_task(self, event):
        # 할 일 입력 다이얼로그 표시
        dialog = TaskInputDialog()
        if dialog.exec_() == QDialog.Accepted:
            task_name = dialog.input_field.text().strip()
            if task_name:
                # 랜덤 위치 생성 (1-5 사이)
                urgency = random.randint(1, 5)
                importance = random.randint(1, 5)

                # 새로운 작업 추가
                self.task_manager.add_task(task_name, urgency, importance)
                self._update_plots(self.task_manager.available_minutes)

    def show(self):
        # 플롯 표시
        self.setup_initial_plot()
        plt.show()
