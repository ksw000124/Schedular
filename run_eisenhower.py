#!/usr/bin/env python
# -*- coding: utf-8 -*-

from eisenhower.task_manager import TaskManager
from eisenhower.visualizer import EisenhowerVisualizer


def main():
    # TaskManager 인스턴스 생성
    task_manager = TaskManager()

    # EisenhowerVisualizer 인스턴스 생성
    visualizer = EisenhowerVisualizer(task_manager)

    # 시각화 실행
    visualizer.show()


if __name__ == "__main__":
    main()
