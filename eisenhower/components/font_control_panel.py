import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from .base_component import BaseComponent


class FontControlPanel (BaseComponent):
    def __init__(self, fig, update_callback, base_font_size=12):
        super().__init__(fig, base_font_size)
        self.update_callback = update_callback
        self.components = []

        # 폰트 크기 버튼 설정
        font_size_increase_ax = plt.axes([0.6, 0.02, 0.1, 0.05])
        self.font_size_increase_button = Button(
            font_size_increase_ax,
            '폰트 크기 +',
            color='#f0f0f0',
            hovercolor='#d0f0f0'
        )
        self.font_size_increase_button.on_clicked(self._increase_font_size)

        font_size_decrease_ax = plt.axes([0.7, 0.02, 0.1, 0.05])
        self.font_size_decrease_button = Button(
            font_size_decrease_ax,
            '폰트 크기 -',
            color='#f0f0f0',
            hovercolor='#d0f0f0'
        )
        self.font_size_decrease_button.on_clicked(self._decrease_font_size)

    def add_component(self, component):
        """컴포넌트 추가"""
        self.components.append(component)

    def _increase_font_size(self, event):
        """폰트 크기 증가"""
        self.font_size = min(24, self.font_size + 1)
        self._update_font_size()

    def _decrease_font_size(self, event):
        """폰트 크기 감소"""
        self.font_size = max(8, self.font_size - 1)
        self._update_font_size()

    def _update_font_size(self):
        """폰트 크기 업데이트"""
        plt.rcParams['font.size'] = self.font_size
        for component in self.components:
            component.update_font_size(self.font_size)
        self.update_callback(self.font_size)
        self.fig.canvas.draw_idle()

    def _update_text_sizes(self):
        """텍스트 크기 업데이트"""
        pass  # FontControlPanel은 텍스트를 직접 관리하지 않음

    def get_font_size(self):
        """현재 폰트 크기 반환"""
        return self.base_font_size * self.font_size
