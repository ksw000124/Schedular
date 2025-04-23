#-*- coding: utf-8 -*-

#############
### Input ###
#############

system = "window"  # "mac",  "window"

# 가능한 시간 입력 (시간,분 형식)
available_hours, available_minutes_part = 6, 0  

# 중요도 긴급도 임의 배치
random = True
raw_list = ["Daily 논문 읽기", 
            "PYP 리뷰논문 읽기", 
            "IM 논문 정리", 
            "IM 2023 앙상블 체크", 
            "MASH 논문 길게 읽기", 
            "MD basic", 
            "유기&일반화학 basic"]


##########################
### Input  (optional) ###
##########################

if random is not True:

    # 초기 데이터 직접 입력

    # 할 일 : { "중요도" : , "긴급도" : }
    # 중요도 : 1~5 (1: 중요하지 않음, 5: 매우 중요)
    # 긴급도 : 1~5 (1: 긴급하지 않음, 5: 매우 긴급)

    raw_dict = {
        "Daily 논문 읽기" : {"중요도": 3, "긴급도": 1},
        "PYP 리뷰논문 읽기": {"중요도": 5, "긴급도": 4},
        "IM 논문 정리" : {"중요도": 4, "긴급도": 4},
        "IM 2023 앙상블 체크": {"중요도": 3, "긴급도": 3},
        "MASH 논문 길게 읽기": {"중요도": 2, "긴급도": 5},
        "MD basic": {"중요도": 3, "긴급도": 1},
        "유기&일반화학 basic": {"중요도": 2, "긴급도": 1},
    }

####################
### Source Code  ###
####################

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm
from matplotlib.widgets import Slider

available_minutes = available_hours * 60 + available_minutes_part


if random:
    # 랜덤 데이터 생성 (중복되지 않게)
    import random
    task_input = []
    used_importance_urgency = set()
    for i in range(len(raw_list)):
        task_name = raw_list[i]
        while True:
            importance = random.randint(1, 5)
            urgency = random.randint(1, 5)
            if (importance, urgency) not in used_importance_urgency:
                used_importance_urgency.add((importance, urgency))
                break
        task_input.append({"할 일": task_name, "중요도": importance, "긴급도": urgency})
    raw_dict = {task["할 일"]: {"중요도": task["중요도"], "긴급도": task["긴급도"]} for task in task_input}


if system == "mac":
    # macOS에서 한글 폰트 설정
    plt.rcParams['font.family'] = 'AppleGothic'
elif system == "window":
    # Windows에서 한글 폰트 설정
    import matplotlib.font_manager as fm
    font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'  # 시스템에 설치된 한글 글꼴 경로
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()



# DataFrame 생성
task_input = [{"할 일": k, "중요도": v["중요도"], "긴급도": v["긴급도"]} for k, v in raw_dict.items()]
df = pd.DataFrame(task_input).reset_index(drop=True)

# 파스텔 색상
pastel_colors = [
    '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))
    for r, g, b, _ in [*map(cm.Pastel1, range(9)), *map(cm.Pastel2, range(8))]
]
###
# 색상 미리 설정
color_map = dict(zip(df["할 일"], pastel_colors[:len(df)]))

# 시간 재계산 함수
def recalculate_time(df, total_minutes):
    df["우선순위"] = (df["중요도"] + df["긴급도"]) / 2 ** 2

    # 최소 할당 시간 30분 적용
    df["할당 시간 (분)"] = 30 

    df.loc[(df["중요도"] == 0) | (df["긴급도"] == 0), ["할당 시간 (분)", "우선순위"]] = 0
    df = df.loc[(df["중요도"] != 0) & (df["긴급도"] != 0)].reset_index(drop=False)

    # 남은 시간 계산
    remaining_minutes = total_minutes - df["할당 시간 (분)"].sum()

    # 우선순위에 따라 남은 시간을 분배
    if remaining_minutes > 0:
        weights = df["우선순위"] / df["우선순위"].sum()
        additional_time = (weights * remaining_minutes).astype(int)
        df["할당 시간 (분)"] += additional_time


    # 할당 시간(분)을 5의 배수로 조정
    df["할당 시간 (분)"] = df["할당 시간 (분)"].apply(lambda x: int(round(x / 5) * 5))



    # 우선순위 기준으로 정렬
    df_sorted = df.sort_values(by="우선순위", ascending=False).reset_index(drop=True)

    # 정렬된 데이터에 따라 색상 재정렬
    sorted_colors = df_sorted["할 일"].map(color_map)
    ###


    remaining_minutes = total_minutes - df_sorted["할당 시간 (분)"].sum()

    # 우선순위에 따라 남은 시간을 분배
    if remaining_minutes > 0:
        # 조정된 전체 할당 시간 계산
        adjusted_total = df_sorted["할당 시간 (분)"].sum()

        # 전체 시간이 available_minutes와 같아지도록 조정
        difference = total_minutes - adjusted_total

        if difference != 0:
            # 차이를 가장 우선순위가 높은 작업에 반영
            df_sorted.loc[0, "할당 시간 (분)"] += difference

    df["할당 시간 (분)"] = df["할당 시간 (분)"].apply(lambda x: int(round(x / 5) * 5))
    df["할당 시간"] = df["할당 시간 (분)"].apply(lambda x: f"{x//60}시간 {x%60}분")

    df_sorted["할당 시간 (분)"] = df_sorted["할당 시간 (분)"].apply(lambda x: int(round(x / 5) * 5))
    df_sorted["할당 시간"] = df_sorted["할당 시간 (분)"].apply(lambda x: f"{x//60}시간 {x%60}분")

    return df_sorted, sorted_colors

# 초기 재계산
df_sorted, sorted_colors = recalculate_time(df, available_minutes)

# 플롯 초기화
fig, axes = plt.subplots(1, 2, figsize=(17, 10))


# 순서 변경 파악
# updated_order = df_updated["할 일"].tolist()
original_order = df["할 일"].tolist()

df_sorted= df_sorted.set_index("할 일").reindex(original_order).reset_index()
sorted_colors = df_sorted["할 일"].map(color_map)


wedges, _ = axes[0].pie(
    df_sorted[df_sorted["할당 시간 (분)"] > 0]["할당 시간 (분)"],
    labels=None,
    colors=sorted_colors[df_sorted["할당 시간 (분)"] > 0],
    startangle=90,
    textprops={'fontsize': 12},
    radius=1.2  # 원 크기를 키우기 위해 radius 값을 증가
)

visible_tasks = df_sorted[df_sorted["할당 시간 (분)"] > 0].reset_index(drop=True)
for i, wedge in enumerate(wedges):
    if i < len(visible_tasks):
        angle = (wedge.theta2 + wedge.theta1) / 2
        x_pos = 0.7 * np.cos(np.radians(angle))
        y_pos = 0.7 * np.sin(np.radians(angle))
        axes[0].text(
            x_pos, y_pos,
            f'{visible_tasks.iloc[i]["할 일"]}\n\n{visible_tasks.iloc[i]["할당 시간"]}',
            ha='center', va='center', fontsize=10, color='black'
        )

axes[0].set_title(f"오늘의 일정 (총 {available_hours}시간 {available_minutes_part}분)", fontsize=14)


coords = df[["긴급도", "중요도"]].values

points = axes[1].scatter(coords[:, 0], coords[:, 1], s=df_sorted["할당 시간 (분)"] * 10,
                    color=sorted_colors, picker=True)

# 텍스트 생성
texts = []
for i, row in df_sorted.iterrows():
    txt = axes[1].text(row["긴급도"], row["중요도"] + 0.2,
                #   f'{row["할 일"]}\n{row["할당 시간"]} | {row["할당 시간 (분)"]} 분',
                  f'{row["할 일"]}\n{row["할당 시간"]}',                  
                  fontsize=9, ha='center')
    texts.append(txt)

# 인터랙션 콜백
selected_index = [None]
def on_pick(event):
    selected_index[0] = event.ind[0]


def on_motion(event):

    if selected_index[0] is None or event.inaxes != axes[1] or event.xdata is None or event.ydata is None:
        return
    idx = selected_index[0]
    # df = pd.DataFrame(task_input).astype({"중요도": "float", "긴급도": "float"}).reset_index(drop=True)
    df.at[idx, "긴급도"] = int(event.xdata)
    df.at[idx, "중요도"] = int(event.ydata)

    df_updated, sorted_colors = recalculate_time(df.copy(), available_minutes)
    coords[idx] = [event.xdata, event.ydata]
    
    # 순서 변경 파악


    df_updated = df_updated.set_index("할 일").reindex(original_order).reset_index()
    sorted_colors = df_updated["할 일"].map(color_map)

    # reorder_indices = [original_order.index(task) for task in updated_order]

    # # points 순서 변경
    # sorted_offsets = coords[reorder_indices]
    points.set_offsets(coords)

    # 기존 points 객체 업데이트
    # points.set_offsets(coords)
    points.set_sizes((df_updated["할당 시간 (분)"] * 10).values)
    points.set_color(sorted_colors)


    # 텍스트 업데이트
    for i, txt in enumerate(texts):
        txt.set_position((df_updated.at[i, "긴급도"], df_updated.at[i, "중요도"] + 0.2))
        txt.set_text(f'{df_updated.at[i, "할 일"]}\n{df_updated.at[i, "할당 시간"]}')

    # points.set_sizes(df_updated["할당 시간 (분)"] )
    

    axes[0].cla()
    wedges, _ = axes[0].pie(
        df_updated[df_updated["할당 시간 (분)"] > 0]["할당 시간 (분)"],
        labels=None,
        colors=sorted_colors[df_updated["할당 시간 (분)"] > 0],
        startangle=90,
        textprops={'fontsize': 12},
        radius=1.2  # 원 크기를 키우기 위해 radius 값을 증가
    )
    visible_tasks = df_updated[df_updated["할당 시간 (분)"] > 0].reset_index(drop=True)
    for i, wedge in enumerate(wedges):
        if i < len(visible_tasks):
            angle = (wedge.theta2 + wedge.theta1) / 2
            x_pos = 0.7 * np.cos(np.radians(angle))
            y_pos = 0.7 * np.sin(np.radians(angle))
            axes[0].text(
                x_pos, y_pos,
                f'{visible_tasks.iloc[i]["할 일"]}\n\n{visible_tasks.iloc[i]["할당 시간"]}',
                ha='center', va='center', fontsize=10, color='black'
            )

    axes[0].set_title(f"오늘의 일정 (총 {available_hours}시간 {available_minutes_part}분)", fontsize=14)


    fig.canvas.draw_idle()




# 이벤트 바인딩
fig.canvas.mpl_connect('pick_event', on_pick)
fig.canvas.mpl_connect('motion_notify_event', on_motion)

# Ensure the on_release function is defined and connected properly
def on_release(event):
    if selected_index[0] is not None:
        selected_index[0] = None  # Clear the selected index to prevent dragging issues
    fig.canvas.draw_idle()  # Redraw the canvas to ensure the point is released visually

fig.canvas.mpl_connect('button_release_event', on_release)

ax_slider = plt.axes([0.15, 0.1, 0.7, 0.05])
slider = Slider(ax_slider, '총 시간 (분)', 30, 600, valinit=available_minutes, valstep=5)

def update_plot(new_total):
    df_updated, sorted_color = recalculate_time(df.copy(), new_total)

    original_order = df["할 일"].tolist()
    df_updated = df_updated.set_index("할 일").reindex(original_order).reset_index()
    sorted_colors = df_updated["할 일"].map(color_map)

    coords[:, 0] = df_updated["긴급도"]
    coords[:, 1] = df_updated["중요도"]
    points.set_offsets(coords)
    points.set_sizes(df_updated["할당 시간 (분)"] * 10)

    for i, txt in enumerate(texts):
        txt.set_position((df_updated.at[i, "긴급도"], df_updated.at[i, "중요도"] + 0.2))
        # txt.set_text(f'{df_updated.at[i, "할 일"]}\n{df_updated.at[i, "할당 시간"]}  | {df_updated.at[i,"할당 시간 (분)"]} 분')
        txt.set_text(f'{df_updated.at[i, "할 일"]}\n{df_updated.at[i, "할당 시간"]}')        

    axes[0].cla()
    # wedges, _ = axes[0].pie(
    #     df_updated[df_updated["할당 시간 (분)"] > 0]["할당 시간 (분)"],
    #     labels=None,
    #     colors=sorted_colors[df_updated["할당 시간 (분)"] > 0],
    #     startangle=90,
    #     textprops={'fontsize': 12}
    # )
    # for i, wedge in enumerate(wedges):
    #     angle = (wedge.theta2 + wedge.theta1) / 2
    #     x_pos = 0.7 * np.cos(np.radians(angle))
    #     y_pos = 0.7 * np.sin(np.radians(angle))
    #     axes[0].text(
    #         x_pos, y_pos,
    #         f'{df_updated.iloc[i]["할 일"]}\n\n{df_updated.iloc[i]["할당 시간"]}',
    #         ha='center', va='center', fontsize=10, color='black'
    #     )
    # axes[0].set_title(f"오늘의 일정 (총 {available_hours}시간 {available_minutes_part}분)", fontsize=14)

    wedges, _ = axes[0].pie(
        df_updated[df_updated["할당 시간 (분)"] > 0]["할당 시간 (분)"],
        labels=None,
        colors=sorted_colors[df_updated["할당 시간 (분)"] > 0],
        startangle=90,
        textprops={'fontsize': 12},
        radius=1.2  # 원 크기를 키우기 위해 radius 값을 증가
    )
    visible_tasks = df_updated[df_updated["할당 시간 (분)"] > 0].reset_index(drop=True)
    for i, wedge in enumerate(wedges):
        if i < len(visible_tasks):
            angle = (wedge.theta2 + wedge.theta1) / 2
            x_pos = 0.7 * np.cos(np.radians(angle))
            y_pos = 0.7 * np.sin(np.radians(angle))
            axes[0].text(
                x_pos, y_pos,
                f'{visible_tasks.iloc[i]["할 일"]}\n\n{visible_tasks.iloc[i]["할당 시간"]}',
                ha='center', va='center', fontsize=10, color='black'
            )

    # axes[0].set_title(f"오늘의 일정 (총 {available_hours}시간 {available_minutes_part}분)", fontsize=14)    


    

    global available_minutes
    global available_hours
    global available_minutes_part

    available_minutes = df_updated["할당 시간 (분)"].sum()
    available_hours = available_minutes // 60
    available_minutes_part = available_minutes % 60
    
    # axes[0].set_title(f"오늘의 일정 (총 {available_hours}시간 {available_minutes_part}분 | 총 {available_minutes} 분 )", fontsize=14)
    axes[0].set_title(f"오늘의 일정 (총 {available_hours}시간 {available_minutes_part}분)", fontsize=14)    


    #axes_title.set_text(f"총 {int(new_total)//60}시간 {int(new_total)%60}분 기준 자동 시간 분배")
    fig.canvas.draw_idle()

    



# 축 설정
axes[1].set_xlim(0, 6)
axes[1].set_ylim(0, 6)
axes[1].set_xlabel("긴급도")
axes[1].set_ylabel("중요도")
axes_title = axes[1].set_title("할 일")
# 사분면 설명 텍스트 (가장자리로 이동)
axes[1].text(5.5, 5.7, "긴급 & 중요", fontsize=10, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7))
axes[1].text(0.7, 5.7, "중요하지만 덜 긴급", fontsize=10, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7))
axes[1].text(5.3, 0.3, "긴급하지만 덜 중요", fontsize=10, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7))
axes[1].text(0.7, 0.3, "덜 중요 & 덜 긴급", fontsize=10, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7))


# 두 번째 플롯: 아이젠하워 매트릭스
# 각 사분면에 색상 추가
axes[1].axhspan(3, 6, xmin=0.5, xmax=1, color='#FFB3BA', alpha=0.3, label="긴급 & 중요")  # 1사분면
axes[1].axhspan(3, 6, xmin=0, xmax=0.5, color='#FFDFBA', alpha=0.3, label="중요하지만 덜 긴급")  # 2사분면
axes[1].axhspan(0, 3, xmin=0.5, xmax=1, color='#BAFFC9', alpha=0.3, label="긴급하지만 덜 중요")  # 3사분면
axes[1].axhspan(0, 3, xmin=0, xmax=0.5, color='#BAE1FF', alpha=0.3, label="덜 중요 & 덜 긴급")  # 4사분면

slider.on_changed(update_plot)

# Reset 버튼 추가
reset_ax = plt.axes([0.85, 0.02, 0.1, 0.05])
reset_button = plt.Button(reset_ax, 'Reset')

def reset(event):
    global df, coords, available_minutes, available_hours, available_minutes_part
    # 초기 데이터로 복원
    df = pd.DataFrame([{"할 일": k, "중요도": v["중요도"], "긴급도": v["긴급도"]} for k, v in raw_dict.items()]).reset_index(drop=True)
    coords = df[["긴급도", "중요도"]].values
    available_minutes = available_hours * 60 + available_minutes_part

    # 플롯 업데이트
    update_plot(available_minutes)

reset_button.on_clicked(reset)

#plt.tight_layout()
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.25, wspace=0.2)

plt.show()

