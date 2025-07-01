#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로그 뷰어 도우미 스크립트
터미널에서 로그를 편리하게 보는 도구
"""

import argparse
import os
import sys
import time
from pathlib import Path


def view_latest_log(follow=False, lines=None):
    """
    최신 로그 파일을 봅니다

    Args:
        follow: 실시간으로 로그를 따라갈지 여부 (tail -f와 유사)
        lines: 마지막 몇 줄만 볼지 지정
    """
    log_dir = Path("logs")

    if not log_dir.exists():
        print("❌ logs 디렉토리가 없습니다!")
        return

    # 최신 로그 파일 찾기
    latest_log = log_dir / "latest.log"

    if latest_log.exists():
        log_file = latest_log
    else:
        # latest.log가 없으면 가장 최신 로그 파일 찾기
        log_files = list(log_dir.glob("openmanus_*.log"))
        if not log_files:
            print("❌ 로그 파일이 없습니다!")
            return
        log_file = max(log_files, key=lambda x: x.stat().st_mtime)

    print(f"📄 로그 파일: {log_file}")
    print("=" * 80)

    try:
        if follow:
            # 실시간 로그 따라가기 (tail -f 방식)
            print("🔄 실시간 로그 모니터링 중... (Ctrl+C로 종료)")
            print("-" * 80)

            with open(log_file, "r", encoding="utf-8") as f:
                # 파일 끝으로 이동
                f.seek(0, 2)

                while True:
                    line = f.readline()
                    if line:
                        print(line.rstrip())
                    else:
                        time.sleep(0.1)

        elif lines:
            # 마지막 N줄만 보기 (tail -n 방식)
            with open(log_file, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:]

                for line in last_lines:
                    print(line.rstrip())

        else:
            # 전체 파일 보기 (페이지 단위)
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()

                # Windows에서는 more 명령어 사용
                if os.name == "nt":
                    # 임시 파일에 저장 후 more로 보기
                    temp_file = "temp_log_view.txt"
                    with open(temp_file, "w", encoding="utf-8") as temp:
                        temp.write(content)

                    os.system(f"more {temp_file}")
                    os.remove(temp_file)
                else:
                    # Unix/Linux에서는 less 사용
                    import subprocess

                    subprocess.run(["less"], input=content, text=True)

    except KeyboardInterrupt:
        print("\n👋 로그 모니터링을 종료합니다.")
    except Exception as e:
        print(f"❌ 오류: {e}")


def list_log_files():
    """모든 로그 파일 목록을 보여줍니다"""
    log_dir = Path("logs")

    if not log_dir.exists():
        print("❌ logs 디렉토리가 없습니다!")
        return

    log_files = list(log_dir.glob("*.log"))

    if not log_files:
        print("❌ 로그 파일이 없습니다!")
        return

    print("📂 로그 파일 목록:")
    print("-" * 60)

    for log_file in sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True):
        stat = log_file.stat()
        size_mb = stat.st_size / (1024 * 1024)
        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))

        print(f"{log_file.name:30} | {size_mb:6.1f}MB | {mtime}")


def clean_old_logs(keep_days=7):
    """오래된 로그 파일들을 정리합니다"""
    log_dir = Path("logs")

    if not log_dir.exists():
        print("❌ logs 디렉토리가 없습니다!")
        return

    import time

    current_time = time.time()
    cutoff_time = current_time - (keep_days * 24 * 60 * 60)

    cleaned = 0
    for log_file in log_dir.glob("openmanus_*.log"):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                print(f"🗑️ 삭제: {log_file.name}")
                cleaned += 1
            except Exception as e:
                print(f"❌ 삭제 실패 {log_file.name}: {e}")

    print(f"✅ {cleaned}개 파일을 정리했습니다.")


def main():
    parser = argparse.ArgumentParser(description="OpenManus 로그 뷰어")

    # 서브커맨드 설정
    subparsers = parser.add_subparsers(dest="command", help="사용 가능한 명령어")

    # view 명령어
    view_parser = subparsers.add_parser("view", help="로그 파일 보기")
    view_parser.add_argument(
        "-f", "--follow", action="store_true", help="실시간으로 로그 따라가기 (tail -f)"
    )
    view_parser.add_argument(
        "-n", "--lines", type=int, help="마지막 N줄만 보기 (tail -n)"
    )

    # list 명령어
    subparsers.add_parser("list", help="로그 파일 목록 보기")

    # clean 명령어
    clean_parser = subparsers.add_parser("clean", help="오래된 로그 파일 정리")
    clean_parser.add_argument(
        "--days", type=int, default=7, help="몇 일 이전 로그를 삭제할지 (기본: 7일)"
    )

    args = parser.parse_args()

    if args.command == "view":
        view_latest_log(follow=args.follow, lines=args.lines)
    elif args.command == "list":
        list_log_files()
    elif args.command == "clean":
        clean_old_logs(keep_days=args.days)
    else:
        # 기본 동작: 최신 로그 보기
        print("🔍 사용법:")
        print("  python view_logs.py view          # 로그 전체 보기")
        print("  python view_logs.py view -f       # 실시간 로그 모니터링")
        print("  python view_logs.py view -n 50    # 마지막 50줄만 보기")
        print("  python view_logs.py list          # 로그 파일 목록")
        print("  python view_logs.py clean         # 오래된 로그 정리")
        print()
        print("🚀 빠른 시작: 최신 로그 보기")
        view_latest_log()


if __name__ == "__main__":
    main()
