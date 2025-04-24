import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from ..ui.task_input_dialog import TaskInputDialog, QDialog


class TaskControlPanel:
    def __init__(self, fig, add_task_callback, reset_callback):
        self.fig = fig
        self.add_task_callback = add_task_callback
        self.reset_callback = reset_callback

        # 할 일 추가 버튼 설정
        add_task_ax = plt.axes([0.5, 0.02, 0.1, 0.05])
        self.add_task_button = Button(
            add_task_ax,
            '할 일 추가',
            color='#f0f0f0',
            hovercolor='#d0f0f0'
        )
        self.add_task_button.on_clicked(self._add_task)

        # 리셋 버튼 설정
        reset_ax = plt.axes([0.85, 0.02, 0.1, 0.05])
        self.reset_button = Button(
            reset_ax,
            'Reset',
            color='#f0f0f0',
            hovercolor='#d0f0f0'
        )
        self.reset_button.on_clicked(self._reset)

    def _add_task(self, event):
        """할 일 추가 다이얼로그 표시"""
        dialog = TaskInputDialog()
        if dialog.exec_() == QDialog.Accepted:
            task_data = dialog.get_task_data()
            self.add_task_callback(task_data)

    def _reset(self, event):
        """리셋 버튼 클릭 시 호출"""
        self.reset_callback()
