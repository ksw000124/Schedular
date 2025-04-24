import numpy as np


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


class Matrix:
    def __init__(self, ax, base_font_size):
        self.ax = ax
        self.base_font_size = base_font_size
        self.font_mult = 1.0
        self.points = []
        self._setup_quadrants()

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
                alpha=1.0
            )
            point.set_scatter(scatter)

            # 텍스트 추가
            hours = point.task.assigned_time // 60
            minutes = point.task.assigned_time % 60
            text = self.ax.text(
                point.task.urgency,
                point.task.importance + 0.2,
                f'{point.task.name}\n{hours}시간 {minutes}분',
                fontsize=self.base_font_size * self.font_mult,
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
        self.ax.set_xlabel(
            "긴급도", fontsize=self.base_font_size * self.font_mult)
        self.ax.set_ylabel(
            "중요도", fontsize=self.base_font_size * self.font_mult)
        self.ax.set_title(
            "할 일", fontsize=self.base_font_size * self.font_mult * 1.5)
        self.ax.set_xticks([1, 2, 3, 4, 5])
        self.ax.set_yticks([1, 2, 3, 4, 5])
        self.ax.grid(True, linestyle='--', alpha=0.3)

        # 사분면 그리기
        for (x, y), (ymin, ymax), label, color in self.quadrant_labels:
            self.ax.text(
                x, y, label,
                fontsize=self.base_font_size * self.font_mult,
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

    def update_font_size(self, font_mult):
        """폰트 크기 업데이트"""
        self.font_mult = font_mult
        self._setup_axes()
        for point in self.points:
            if point.text is not None:
                point.text.set_fontsize(self.base_font_size * self.font_mult)
