#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
아이젠하워 매트릭스 앱 아이콘 생성기
"""

from PIL import Image, ImageDraw, ImageFont
import os

# 폴더가 없으면 생성
icon_dir = os.path.join('eisenhower', 'fonts')
os.makedirs(icon_dir, exist_ok=True)

# 아이콘 크기
width, height = 256, 256
image = Image.new('RGBA', (width, height), color=(255, 255, 255, 0))
draw = ImageDraw.Draw(image)

# 사분면 색상
colors = [
    (255, 179, 186, 180),  # 연한 빨강 (중요 & 긴급)
    (255, 223, 186, 180),  # 연한 주황 (중요 & 덜 긴급)
    (186, 255, 201, 180),  # 연한 초록 (덜 중요 & 긴급)
    (186, 225, 255, 180),  # 연한 파랑 (덜 중요 & 덜 긴급)
]

# 사분면 그리기
draw.rectangle([0, 0, width//2, height//2], fill=colors[0])        # 좌상
draw.rectangle([width//2, 0, width, height//2], fill=colors[1])    # 우상
draw.rectangle([0, height//2, width//2, height], fill=colors[2])   # 좌하
draw.rectangle([width//2, height//2, width, height], fill=colors[3])  # 우하

# 경계선 그리기
draw.line([(0, height//2), (width, height//2)], fill=(0, 0, 0, 200), width=3)
draw.line([(width//2, 0), (width//2, height)], fill=(0, 0, 0, 200), width=3)

# "E" 문자 추가
try:
    # 시스템에 맞는 기본 폰트 사용
    font = ImageFont.truetype("arial.ttf", 120)
except:
    # 폰트를 찾을 수 없으면 기본 폰트 사용
    font = ImageFont.load_default()

draw.text((width//2, height//2), "E",
          fill=(0, 0, 0, 255), font=font, anchor="mm")

# 아이콘 외곽선 그리기
draw.rectangle([0, 0, width-1, height-1], outline=(0, 0, 0, 200), width=7)

# .ico 파일로 저장
icon_path = os.path.join(icon_dir, 'app_icon.ico')
sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
image.save(icon_path, format='ICO', sizes=sizes)

print(f"아이콘이 생성되었습니다: {icon_path}")
