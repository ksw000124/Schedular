# -*- coding: utf-8 -*-

import pandas as pd
import json
import os
import random
import colorsys


class Task:
    def __init__(self, name, urgency=3, importance=3):
        self.name = name
        self.urgency = urgency
        self.importance = importance
        self.assigned_time = 0  # 할당 시간은 계산되는 값

    def to_dict(self):
        return {
            "할 일": self.name,
            "긴급도": self.urgency,
            "중요도": self.importance
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["할 일"],
            urgency=data["긴급도"],
            importance=data["중요도"]
        )


class TaskManager:
    def __init__(self):
        self.tasks = []
        self.available_minutes = 480  # 기본값 8시간
        self.available_hours = 8
        self.available_minutes_part = 0
        self._load_tasks()
        self.color_map = self._create_color_map()

    def _load_tasks(self):
        """JSON 파일에서 작업 목록 로드"""
        try:
            with open(os.path.join(os.path.dirname(__file__), 'tasks.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    # 총 시간 로드
                    self.available_minutes = data.get('total_minutes', 480)
                    self.available_hours = self.available_minutes // 60
                    self.available_minutes_part = self.available_minutes % 60
                    # 작업 목록 로드
                    tasks_data = data.get('tasks', [])
                    self.tasks = [Task.from_dict(task_data)
                                  for task_data in tasks_data]
                else:
                    self.tasks = [Task.from_dict(task_data)
                                  for task_data in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = []

    def _save_tasks(self):
        """작업 목록을 JSON 파일로 저장"""
        data = {
            'total_minutes': self.available_minutes,
            'tasks': [task.to_dict() for task in self.tasks]
        }
        with open(os.path.join(os.path.dirname(__file__), 'tasks.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _create_color_map(self):
        """각 작업에 대한 색상 맵 생성"""
        # 파스텔톤 색상 팔레트
        pastel_colors = [
            '#FFB3BA',  # 연한 빨강
            '#BAFFC9',  # 연한 초록
            '#BAE1FF',  # 연한 파랑
            '#FFFFBA',  # 연한 노랑
            '#FFB3F7',  # 연한 분홍
            '#B5EAD7',  # 연한 민트
            '#C7CEEA',  # 연한 하늘
            '#FFDAC1',  # 연한 주황
            '#E2BEF1',  # 연한 보라
            '#FF9AA2',  # 연한 코랄
            '#B5B9FF',  # 연한 라벤더
            '#AFF8DB',  # 연한 청록
        ]

        colors = {}
        for i, task in enumerate(self.tasks):
            colors[task.name] = pastel_colors[i % len(pastel_colors)]
        return colors

    def add_task(self, name, urgency=3, importance=3):
        """새로운 작업 추가"""
        task = Task(name=name, urgency=urgency, importance=importance)
        self.tasks.append(task)
        self._save_tasks()
        self.color_map = self._create_color_map()

    def remove_task(self, task_name):
        """작업 제거"""
        self.tasks = [task for task in self.tasks if task.name != task_name]
        self._save_tasks()
        self.color_map = self._create_color_map()

    def update_task_position(self, task_name, urgency, importance):
        """작업의 위치(긴급도, 중요도) 업데이트"""
        for task in self.tasks:
            if task.name == task_name:
                task.urgency = urgency
                task.importance = importance
                break
        self._save_tasks()

    def recalculate_time(self, total_minutes):
        """작업 시간 재계산"""
        self.available_minutes = total_minutes
        self.available_hours = total_minutes // 60
        self.available_minutes_part = total_minutes % 60
        self._save_tasks()  # 총 시간 변경 시 저장
        return self._calculate_time_distribution()

    def _calculate_time_distribution(self):
        """총 시간을 기준으로 각 작업의 시간 재계산"""
        if not self.tasks:
            return pd.DataFrame(columns=["할 일", "긴급도", "중요도", "할당 시간 (분)", "할당 시간"]), []

        # 우선순위 계산
        total_priority = sum(
            task.urgency * task.importance for task in self.tasks)

        # 시간 할당
        for task in self.tasks:
            if total_priority > 0:
                priority = task.urgency * task.importance
                task.assigned_time = int(
                    (priority / total_priority) * self.available_minutes)
            else:
                task.assigned_time = 0

        # DataFrame 생성
        df = pd.DataFrame([
            {
                "할 일": task.name,
                "긴급도": task.urgency,
                "중요도": task.importance,
                "할당 시간 (분)": task.assigned_time,
                "할당 시간": f"{task.assigned_time//60}시간 {task.assigned_time%60}분"
            }
            for task in self.tasks
        ])

        return df, [self.color_map[task.name] for task in self.tasks]
