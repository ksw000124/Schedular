# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.patches import Circle, Rectangle
from matplotlib.animation import FuncAnimation
import time
from datetime import datetime, timedelta
import json
import os
from .base_component import BaseComponent


class PieChart(BaseComponent):
    def __init__(self, ax):
        config_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'config', 'properties.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        super().__init__(ax.figure, config['font_size'])
        self.set_axis(ax)
        self.available_hours = 0
        self.available_minutes_part = 0
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

    def draw(self, tasks, available_hours, available_minutes_part, colors):
        """파이 차트 그리기"""
        self.available_hours = available_hours
        self.available_minutes_part = available_minutes_part

        self.ax.clear()

        if not tasks:
            return

        # 파이 차트 데이터 준비
        sizes = [task.assigned_time for task in tasks]
        labels = [f"{task.name}\n{task.assigned_time//60}시간 {task.assigned_time%60}분"
                  for task in tasks]

        # 총 시간 계산
        self.total_minutes = sum(sizes)

        # 파이 차트 그리기
        wedges, texts, autotexts = self.ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='',
            startangle=90,
            counterclock=False,
            labeldistance=0.5,  # 텍스트를 원 안쪽으로 이동
            radius=1.2  # 파이 차트 크기 키우기
        )

        # 텍스트 스타일 설정
        for text in texts + autotexts:
            text.set_fontsize(self.font_size)

        # 제목 설정
        self.ax.set_title(
            f"오늘의 일정 (총 {available_hours}시간 {available_minutes_part}분)",
            fontsize=self.font_size * 1.5
        )

        # 타이머 텍스트 추가
        self.timer_text = self.ax.text(
            0, 0.2,
            '00:00:00',
            ha='center', va='center',
            fontsize=self.font_size * 1.2,
            color='#00A0A0'
        )

        # 타이머 버튼 추가
        self.timer_button = Circle((0, 0), 0.08, color='#00A0A0')
        self.ax.add_patch(self.timer_button)
        self.button_text = self.ax.text(
            0, 0,
            '시작',
            ha='center', va='center',
            fontsize=self.font_size * 0.8,
            color='white'
        )

        # 타이머 점 추가
        self.timer_dot = Circle((0, 1.2), 0.03, color='#00A0A0')
        self.ax.add_patch(self.timer_dot)

        # 클릭 이벤트 연결
        self.ax.figure.canvas.mpl_connect(
            'button_press_event', self.on_button_click)

    def on_button_click(self, event):
        """버튼 클릭 이벤트 처리"""
        if event.inaxes != self.ax:
            return

        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return

        # 시작/정지 버튼 클릭 확인
        distance = np.sqrt(x**2 + y**2)
        if distance <= 0.08:
            if not self.timer_running:
                self.start_timer()
                self.ax.figure.canvas.draw()  # 즉시 화면 업데이트
            else:
                self.stop_timer()
                self.ax.figure.canvas.draw()  # 즉시 화면 업데이트

        # 초기화 버튼 클릭 확인
        if self.reset_button and -0.1 <= x <= 0.1 and -0.15 <= y <= -0.1:
            self.reset_timer()
            self.ax.figure.canvas.draw()  # 즉시 화면 업데이트

    def start_timer(self):
        """타이머 시작"""
        self.timer_running = True
        if self.paused_time is not None:
            self.start_time = datetime.now() - self.paused_time
            self.paused_time = None
        else:
            self.start_time = datetime.now()

        self.button_text.set_text('정지')
        self.timer_button.set_color('#FF0000')

        if self.reset_button:
            self.reset_button.remove()
            self.reset_text.remove()
            self.reset_button = None
            self.reset_text = None

        # 즉시 첫 번째 업데이트 실행
        self.update_timer(None)

        # 애니메이션 시작
        self.animation = FuncAnimation(
            self.ax.figure,
            self.update_timer,
            interval=1000,
            blit=False,
            cache_frame_data=False
        )

    def stop_timer(self):
        """타이머 정지"""
        self.timer_running = False
        self.button_text.set_text('계속')
        self.timer_button.set_color('#00A0A0')

        if self.start_time:
            self.paused_time = datetime.now() - self.start_time

        if self.animation:
            self.animation.event_source.stop()

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
                fontsize=self.font_size * 0.7,
                color='white'
            )

    def reset_timer(self):
        """타이머 초기화"""
        self.timer_running = False
        self.start_time = None
        self.paused_time = None
        self.button_text.set_text('시작')
        self.timer_button.set_color('#00A0A0')

        self.timer_text.set_text('00:00:00')

        if self.timer_dot:
            self.timer_dot.center = (0, 1.2)

        if self.reset_button:
            self.reset_button.remove()
            self.reset_text.remove()
            self.reset_button = None
            self.reset_text = None

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

        self.timer_text.set_text(f'{hours:02d}:{minutes:02d}:{seconds:02d}')

        if self.timer_dot and self.total_minutes > 0:
            progress = min(total_seconds / (self.total_minutes * 60), 1.0)
            angle = 90 - (progress * 360)
            radius = 1.2

            x = radius * np.cos(np.radians(angle))
            y = radius * np.sin(np.radians(angle))

            # 현재 위치와 새로운 위치가 다를 때만 업데이트
            current_x, current_y = self.timer_dot.center
            if abs(current_x - x) > 0.01 or abs(current_y - y) > 0.01:
                self.timer_dot.center = (x, y)

        return self.timer_text, self.timer_dot

    def _update_text_sizes(self):
        """텍스트 크기 업데이트"""
        if self.ax is None:
            return

        # 모든 텍스트 요소 업데이트
        for text in self.ax.texts:
            text.set_fontsize(self.font_size)

        # 제목 업데이트
        self.ax.set_title(
            f"오늘의 일정 (총 {self.available_hours}시간 {self.available_minutes_part}분)",
            fontsize=self.font_size * 1.5
        )
