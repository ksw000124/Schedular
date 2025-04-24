import numpy as np
import json
import os
from .base_component import BaseComponent


class MatrixPoint:
    def __init__(self, task, color):
        self.task = task
        self.color = color
        self.text = None
        self.scatter = None
        self.is_selected = False
        self.dragged_pos = [task.urgency, task.importance]

    def update_position(self, urgency, importance):
        """위치 업데이트"""
        self.task.urgency = urgency
        self.task.importance = importance
        self.dragged_pos = [urgency, importance]
        if self.scatter is not None:
            self.scatter.set_offsets([[urgency, importance]])
        if self.text is not None:
            self.text.set_position((urgency, importance + 0.2))

    def set_text(self, text):
        """텍스트 설정"""
        self.text = text

    def set_scatter(self, scatter):
        """산점도 점 설정"""
        self.scatter = scatter

    def highlight(self, highlight=True):
        """점 강조/해제"""
        if self.scatter is not None:
            size = self.scatter.get_sizes()[0]
            self.scatter.set_sizes([size * 1.2 if highlight else size / 1.2])
        self.is_selected = highlight


class Matrix(BaseComponent):
    def __init__(self, ax):
        config_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'config', 'properties.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        super().__init__(ax.figure, config['font_size'])
        self.set_axis(ax)
        self.points = []
        self.selected_point = None
        self.is_dragging = False
        self.background = None
        self.task_manager = None
        self.update_plots_callback = None
        self._setup_quadrants()

    def setup_interaction(self, task_manager, update_plots_callback):
        """인터랙션 설정"""
        self.task_manager = task_manager
        self.update_plots_callback = update_plots_callback
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)

    def on_press(self, event):
        """마우스 버튼 누를 때"""
        if event.inaxes != self.ax:
            return

        point = self.get_point_at_position(event.xdata, event.ydata)
        if point is not None:
            self.selected_point = point
            self.is_dragging = True
            self._toggle_point_visibility(False)
            self._update_background()
            self._toggle_point_visibility(True)

    def on_motion(self, event):
        """마우스 이동 시"""
        if not self._is_valid_drag(event):
            return

        x_val, y_val = self._constrain_coordinates(event.xdata, event.ydata)
        self._update_point_position(x_val, y_val)

    def on_release(self, event):
        """마우스 버튼 놓을 때"""
        if self.selected_point is None:
            return

        x_val, y_val = self._get_final_coordinates()
        self._handle_final_position(x_val, y_val)
        self._reset_state()

    def _toggle_point_visibility(self, visible):
        """점의 가시성 토글"""
        if self.selected_point.scatter is not None:
            self.selected_point.scatter.set_visible(visible)
        if self.selected_point.text is not None:
            self.selected_point.text.set_visible(visible)

    def _update_background(self):
        """배경 업데이트"""
        # 선택된 포인트를 숨기고 배경 캡처
        if self.selected_point is not None:
            self._toggle_point_visibility(False)

        self.fig.canvas.draw()
        self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)

        # 선택된 포인트를 다시 표시
        if self.selected_point is not None:
            self._toggle_point_visibility(True)

    def _is_valid_drag(self, event):
        """드래그 유효성 검사"""
        return (self.is_dragging and
                self.selected_point is not None and
                event.inaxes == self.ax and
                event.xdata is not None and
                event.ydata is not None)

    def _constrain_coordinates(self, x, y):
        """좌표 제한"""
        return min(max(x, 0.5), 5.5), min(max(y, 0.5), 5.5)

    def _update_point_position(self, x_val, y_val):
        """점 위치 업데이트"""
        if self.selected_point is None:
            return

        # figure가 None이면 ax에서 가져옴
        if self.fig is None:
            self.fig = self.ax.figure

        self.selected_point.update_position(x_val, y_val)

        # 배경 복원 전에 현재 포인트 위치 저장
        current_pos = self.selected_point.scatter.get_offsets()[0]

        self.fig.canvas.restore_region(self.background)

        # 포인트 위치 업데이트
        self.selected_point.scatter.set_offsets([[x_val, y_val]])
        if self.selected_point.text is not None:
            self.selected_point.text.set_position((x_val, y_val + 0.2))

        # 포인트와 텍스트 다시 그리기
        self.ax.draw_artist(self.selected_point.scatter)
        if self.selected_point.text is not None:
            self.ax.draw_artist(self.selected_point.text)

        # 캔버스 업데이트
        self.fig.canvas.blit(self.ax.bbox)

    def _get_final_coordinates(self):
        """최종 좌표 계산"""
        x_val = round(self.selected_point.task.urgency)
        y_val = round(self.selected_point.task.importance)
        return min(max(x_val, 1), 5), min(max(y_val, 1), 5)

    def _handle_final_position(self, x_val, y_val):
        """최종 위치 처리"""
        if x_val == 0:
            self.task_manager.remove_task(self.selected_point.task.name)
        else:
            self.selected_point.update_position(x_val, y_val)
            self.task_manager.update_task_position(
                self.selected_point.task.name,
                x_val,
                y_val
            )
        self.update_plots_callback(self.task_manager.available_minutes)
        self._update_background()

    def _reset_state(self):
        """상태 초기화"""
        self.selected_point = None
        self.is_dragging = False

    def draw(self, tasks, sorted_colors):
        """매트릭스 그리기"""
        # 기존 점들 제거
        for point in self.points:
            if point.scatter is not None:
                point.scatter.remove()
            if point.text is not None:
                point.text.remove()
        self.points.clear()

        # 축 설정
        self._setup_axes()

        if not tasks:
            return

        # 새로운 점들 생성
        self.points = [MatrixPoint(task, color)
                       for task, color in zip(tasks, sorted_colors)]

        # 점 그리기
        for point in self.points:
            scatter = self.ax.scatter(
                point.task.urgency,
                point.task.importance,
                s=point.task.assigned_time * 10,
                color=point.color,
                picker=10,
                alpha=1.0,
                edgecolors='black',
                linewidths=1
            )
            point.set_scatter(scatter)

            # 텍스트 추가
            hours = point.task.assigned_time // 60
            minutes = point.task.assigned_time % 60
            text = self.ax.text(
                point.task.urgency,
                point.task.importance + 0.2,
                f'{point.task.name}\n{hours}시간 {minutes}분',
                fontsize=self.font_size,
                ha='center'
            )
            point.set_text(text)

    def _setup_quadrants(self):
        """사분면 설정"""
        self.quadrant_colors = {
            'urgent_important': '#FFB3BA',     # 연한 빨강
            'important': '#FFDFBA',            # 연한 주황
            'urgent': '#BAFFC9',               # 연한 초록
            'neither': '#BAE1FF'               # 연한 파랑
        }

        self.quadrant_labels = [
            ((5.5, 5.7), (3, 6), "긴급 & 중요",
             self.quadrant_colors['urgent_important']),
            ((0.7, 5.7), (3, 6), "중요하지만 덜 긴급",
             self.quadrant_colors['important']),
            ((5.3, 0.3), (0, 3), "긴급하지만 덜 중요", self.quadrant_colors['urgent']),
            ((0.7, 0.3), (0, 3), "덜 중요 & 덜 긴급",
             self.quadrant_colors['neither']),
        ]

    def _setup_axes(self):
        """축 설정"""
        self.ax.clear()
        self.ax.set_xlim(0, 6)
        self.ax.set_ylim(0, 6)
        self.ax.set_xlabel("긴급도", fontsize=self.font_size)
        self.ax.set_ylabel("중요도", fontsize=self.font_size)
        self.ax.set_title("할 일", fontsize=self.font_size * 1.5)
        self.ax.set_xticks([1, 2, 3, 4, 5])
        self.ax.set_yticks([1, 2, 3, 4, 5])
        self.ax.grid(True, linestyle='--', alpha=0.3)

        # 사분면 그리기
        for (x, y), (ymin, ymax), label, color in self.quadrant_labels:
            self.ax.text(
                x, y, label,
                fontsize=self.font_size,
                ha='center', va='center',
                bbox={"facecolor": "white", "alpha": 0.7}
            )
            if x > 3:  # 오른쪽 영역
                self.ax.axhspan(ymin, ymax, xmin=0.5, xmax=1.0,
                                color=color, alpha=0.3)
            else:  # 왼쪽 영역
                self.ax.axhspan(ymin, ymax, xmin=0.0, xmax=0.5,
                                color=color, alpha=0.3)

    def get_point_at_position(self, x, y):
        """주어진 위치에서 가장 가까운 점 찾기"""
        if not self.points:
            return None

        distances = [
            (point, np.sqrt((point.task.urgency - x)
             ** 2 + (point.task.importance - y)**2))
            for point in self.points
        ]
        closest_point, min_distance = min(distances, key=lambda x: x[1])
        return closest_point if min_distance < 0.5 else None

    def _update_text_sizes(self):
        """텍스트 크기 업데이트"""
        if self.ax is None:
            return

        # 모든 텍스트 요소 업데이트
        for text in self.ax.texts:
            text.set_fontsize(self.font_size)

        # 축 라벨과 제목 업데이트
        self.ax.set_xlabel("긴급도", fontsize=self.font_size)
        self.ax.set_ylabel("중요도", fontsize=self.font_size)
        self.ax.set_title("할 일", fontsize=self.font_size * 1.5)

        # 눈금 라벨 업데이트
        self.ax.tick_params(
            axis='both',
            which='major',
            labelsize=self.font_size
        )
