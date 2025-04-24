import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, TextBox


class TimeControlPanel:
    def __init__(self, fig, update_callback, initial_minutes=480):
        self.fig = fig
        self.update_callback = update_callback
        self.initial_minutes = initial_minutes
        self.last_update_time = 0
        self.update_interval = 0.05

        # 슬라이더 설정
        ax_slider = plt.axes([0.15, 0.1, 0.69, 0.05])
        self.slider = Slider(
            ax_slider,
            '총 시간 (분)',
            30, 600,
            valinit=initial_minutes,
            valstep=5,
            color='#00a0a0',
            initcolor='none'
        )
        self.slider.on_changed(self._on_slider_changed)

        # 시간 입력 필드 설정
        time_input_ax = plt.axes([0.85, 0.1, 0.1, 0.05])
        self.time_input = TextBox(
            time_input_ax,
            '',
            initial=str(initial_minutes),
            color='white',
            hovercolor='#f0f0f0'
        )
        self.time_input.on_submit(self._on_time_input_changed)

    def _on_slider_changed(self, val):
        """슬라이더 값 변경 시 호출"""
        import time
        current_time = time.time()

        if current_time - self.last_update_time > self.update_interval:
            self.last_update_time = current_time
            self.update_callback(val)
            self.time_input.set_val(str(int(val)))

    def _on_time_input_changed(self, text):
        """시간 입력 필드 값 변경 시 호출"""
        try:
            minutes = int(text)
            if 30 <= minutes <= 600:
                self.update_callback(minutes)
                self.slider.set_val(minutes)
        except ValueError:
            pass

    def update_minutes(self, minutes):
        """외부에서 시간 업데이트 시 호출"""
        self.slider.set_val(minutes)
        self.time_input.set_val(str(minutes))
