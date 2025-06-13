# Python version check: 3.11-3.13
# 파이썬 버전을 확인하는 코드입니다
# 사용자의 컴퓨터에 설치된 파이썬 버전이 3.11에서 3.13 사이인지 확인해요
import sys

# 파이썬 버전이 3.11보다 낮거나 3.14보다 높으면 경고를 표시합니다
# (3.13.x는 모두 허용되도록 3.14로 변경)
if sys.version_info < (3, 11) or sys.version_info >= (3, 14):
    print(
        "Warning: Unsupported Python version {ver}, please use 3.11-3.13".format(
            ver=".".join(map(str, sys.version_info))
        )
    )
