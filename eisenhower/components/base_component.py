import matplotlib.pyplot as plt


class BaseComponent:
    def __init__(self, fig, base_font_size=12):
        self.fig = fig
        self.font_size = base_font_size
        self.ax = None

    def update_font_size(self, font_size):
        """폰트 크기 업데이트"""
        self.font_size = font_size
        if self.ax is not None:
            self._update_text_sizes()

    def _update_text_sizes(self):
        """텍스트 크기 업데이트 (하위 클래스에서 구현)"""
        raise NotImplementedError("하위 클래스에서 구현해야 합니다.")

    def set_axis(self, ax):
        """축 설정"""
        self.ax = ax
