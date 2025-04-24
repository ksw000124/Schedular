# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.patches import Circle, Rectangle
from matplotlib.animation import FuncAnimation
import time
from datetime import datetime, timedelta


class PieChart:
    def __init__(self, ax, base_font_size):
        self.ax = ax
        self.base_font_size = base_font_size
        self.font_mult = 1.0
        self.timer_running = False
        self.start_time = None
        self.total_minutes = 0
        self.timer_button = None
        self.reset_button = None
        self.timer_text = None
        self.timer_dot = None
        self.animation = None
        self.button_text = None
        self.reset_text = None
        self.paused_time = None

    def draw(self, tasks, available_hours, available_minutes_part, sorted_colors):
        """파이 차트 그리기"""
        self.ax.clear()

        if not tasks:
            # 작업이 없을 때는 빈 파이 차트만 표시
            self._set_title(available_hours, available_minutes_part)
            return

        # 할당 시간이 0보다 큰 작업만 선택
        visible_tasks = [(task, color) for task, color in zip(tasks, sorted_colors)
                         if task.assigned_time > 0]

        if not visible_tasks:
            # 할당 시간이 0인 작업만 있을 때
            self._set_title(available_hours, available_minutes_part)
            return

        # 파이 차트 데이터 준비
        times = [task.assigned_time for task, _ in visible_tasks]
        colors = [color for _, color in visible_tasks]

        # 총 시간 계산 (분 단위)
        self.total_minutes = sum(times)

        # 파이 차트 그리기
        wedges, _ = self.ax.pie(
            times,
            labels=None,
            colors=colors,
            startangle=90,
            radius=1.2
        )

        # 타이머 점 추가 (이미 존재하면 재사용)
        if self.timer_dot is None:
            self.timer_dot = Circle((0, 1.2), 0.03, color='#00A0A0')
            self.ax.add_patch(self.timer_dot)
        else:
            self.ax.add_patch(self.timer_dot)

        # 파이 차트에 텍스트 추가
        for i, (wedge, (task, _)) in enumerate(zip(wedges, visible_tasks)):
            angle = (wedge.theta2 + wedge.theta1) / 2
            x_pos = 0.7 * np.cos(np.radians(angle))
            y_pos = 0.7 * np.sin(np.radians(angle))
            hours = task.assigned_time // 60
            minutes = task.assigned_time % 60
            self.ax.text(
                x_pos, y_pos,
                f'{task.name}\n\n{hours}시간 {minutes}분',
                ha='center', va='center',
                fontsize=self.base_font_size * self.font_mult,
                color='black'
            )

        self._set_title(available_hours, available_minutes_part)

        # 타이머 텍스트 추가 (이미 존재하면 재사용)
        if self.timer_text is None:
            self.timer_text = self.ax.text(
                0, 0.2,
                '00:00:00',
                ha='center', va='center',
                fontsize=self.base_font_size * self.font_mult * 1.2,
                color='#00A0A0'
            )
        else:
            self.ax.add_artist(self.timer_text)

        # 타이머 버튼 추가 (이미 존재하면 재사용)
        if self.timer_button is None:
            self.timer_button = Circle((0, 0), 0.08, color='#00A0A0')
            self.ax.add_patch(self.timer_button)
            self.button_text = self.ax.text(
                0, 0,
                '시작',
                ha='center', va='center',
                fontsize=self.base_font_size * self.font_mult * 0.8,
                color='white'
            )
        else:
            self.ax.add_patch(self.timer_button)
            self.ax.add_artist(self.button_text)

        # 초기화 버튼 추가 (이미 존재하면 재사용)
        if self.reset_button is not None:
            self.ax.add_patch(self.reset_button)
            self.ax.add_artist(self.reset_text)

        # 클릭 이벤트 연결
        self.ax.figure.canvas.mpl_connect(
            'button_press_event', self.on_button_click)

    def on_button_click(self, event):
        """버튼 클릭 이벤트 처리"""
        if event.inaxes != self.ax:
            return

        # 버튼 영역 확인 (원형)
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return

        # 시작/정지 버튼 클릭 확인
        distance = np.sqrt(x**2 + y**2)
        if distance <= 0.08:  # 버튼 반경 내에서 클릭되었는지 확인
            if not self.timer_running:
                self.start_timer()
            else:
                self.stop_timer()

        # 초기화 버튼 클릭 확인
        if self.reset_button and -0.1 <= x <= 0.1 and -0.15 <= y <= -0.1:
            self.reset_timer()

    def start_timer(self):
        """타이머 시작"""
        self.timer_running = True
        if self.paused_time is not None:
            # 일시정지 후 재개
            self.start_time = datetime.now() - self.paused_time
            self.paused_time = None
        else:
            # 처음 시작
            self.start_time = datetime.now()

        self.button_text.set_text('정지')
        self.timer_button.set_color('#FF0000')  # 빨간색으로 변경

        # 초기화 버튼 제거
        if self.reset_button:
            self.reset_button.remove()
            self.reset_text.remove()
            self.reset_button = None
            self.reset_text = None

        # 애니메이션 시작
        self.animation = FuncAnimation(
            self.ax.figure,
            self.update_timer,
            interval=1000,  # 1초마다 업데이트
            blit=False,
            cache_frame_data=False  # 경고 해결
        )

    def stop_timer(self):
        """타이머 정지"""
        self.timer_running = False
        self.button_text.set_text('계속')
        self.timer_button.set_color('#00A0A0')  # 파란색으로 변경

        # 일시정지 시간 저장
        if self.start_time:
            self.paused_time = datetime.now() - self.start_time

        # 애니메이션 중지
        if self.animation:
            self.animation.event_source.stop()

        # 초기화 버튼 추가
        if not self.reset_button:
            self.reset_button = Rectangle(
                (-0.1, -0.15), 0.2, 0.05,
                color='#808080', alpha=0.8
            )
            self.ax.add_patch(self.reset_button)

            self.reset_text = self.ax.text(
                0, -0.125,
                '초기화',
                ha='center', va='center',
                fontsize=self.base_font_size * self.font_mult * 0.7,
                color='white'
            )

    def reset_timer(self):
        """타이머 초기화"""
        self.timer_running = False
        self.start_time = None
        self.paused_time = None
        self.button_text.set_text('시작')
        self.timer_button.set_color('#00A0A0')

        # 타이머 텍스트 초기화
        self.timer_text.set_text('00:00:00')

        # 타이머 점 초기화
        if self.timer_dot:
            self.timer_dot.center = (0, 1.2)

        # 초기화 버튼 제거
        if self.reset_button:
            self.reset_button.remove()
            self.reset_text.remove()
            self.reset_button = None
            self.reset_text = None

        # 애니메이션 중지
        if self.animation:
            self.animation.event_source.stop()

    def update_timer(self, frame):
        """타이머 업데이트"""
        if not self.timer_running:
            return

        elapsed = datetime.now() - self.start_time
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        # 타이머 텍스트 업데이트
        self.timer_text.set_text(f'{hours:02d}:{minutes:02d}:{seconds:02d}')

        # 타이머 점 위치 업데이트
        if self.timer_dot:
            # 전체 시간에 대한 진행률 계산
            if self.total_minutes == 0:
                return

            progress = total_seconds / (self.total_minutes * 60)
            if progress > 1.0:
                progress = 1.0

            # 각도 계산 (시계 방향으로 회전)
            angle = 90 - (progress * 360)
            radius = 1.2

            # 점의 위치 계산
            x = radius * np.cos(np.radians(angle))
            y = radius * np.sin(np.radians(angle))
            self.timer_dot.center = (x, y)

        return self.timer_text, self.timer_dot

    def _set_title(self, available_hours, available_minutes_part):
        """제목 설정"""
        self.ax.set_title(
            f"오늘의 일정 (총 {available_hours}시간 {available_minutes_part}분)",
            fontsize=self.base_font_size * self.font_mult * 1.5
        )

    def update_font_size(self, font_mult):
        """폰트 크기 업데이트"""
        self.font_mult = font_mult
        for text in self.ax.texts:
            text.set_fontsize(self.base_font_size * self.font_mult)
        self._set_title(
            self.ax.get_title().split('(')[1].split('시간')[0],
            self.ax.get_title().split('시간 ')[1].split('분')[0]
        )
