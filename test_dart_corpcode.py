#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DART API 기업코드 검증 스크립트
삼성전자의 정확한 기업코드를 찾고 실제 보고서 존재 여부를 확인합니다.
"""

import json
import os
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime

import requests

# DART API 키를 환경변수에서 가져오기
DART_API_KEY = os.getenv("DART_API_KEY")
if not DART_API_KEY:
    print("❌ DART_API_KEY 환경변수가 설정되지 않았습니다!")
    exit(1)

BASE_URL = "https://opendart.fss.or.kr/api"


def get_corp_code_list():
    """기업코드 목록 다운로드 및 파싱"""
    print("🔍 1단계: DART 기업코드 목록 다운로드")

    url = f"{BASE_URL}/corpCode.xml"
    params = {"crtfc_key": DART_API_KEY}

    try:
        response = requests.get(url, params=params)
        print(f"   - HTTP 상태: {response.status_code}")

        if response.status_code != 200:
            print(f"   - 오류: HTTP {response.status_code}")
            return None

        # ZIP 파일로 저장
        with open("corpcode.zip", "wb") as f:
            f.write(response.content)

        # ZIP 파일 압축 해제
        with zipfile.ZipFile("corpcode.zip", "r") as zip_ref:
            zip_ref.extractall(".")

        # XML 파일 파싱
        tree = ET.parse("CORPCODE.xml")
        root = tree.getroot()

        corp_list = []
        for list_item in root.findall("list"):
            corp_code = (
                list_item.find("corp_code").text
                if list_item.find("corp_code") is not None
                else ""
            )
            corp_name = (
                list_item.find("corp_name").text
                if list_item.find("corp_name") is not None
                else ""
            )
            stock_code = (
                list_item.find("stock_code").text
                if list_item.find("stock_code") is not None
                else ""
            )
            modify_date = (
                list_item.find("modify_date").text
                if list_item.find("modify_date") is not None
                else ""
            )

            corp_list.append(
                {
                    "corp_code": corp_code,
                    "corp_name": corp_name,
                    "stock_code": stock_code,
                    "modify_date": modify_date,
                }
            )

        print(f"   ✅ 총 {len(corp_list)}개 기업 코드 다운로드 완료")
        return corp_list

    except Exception as e:
        print(f"   - 예외 발생: {e}")
        return None


def find_samsung_companies(corp_list):
    """삼성 관련 기업들 찾기"""
    print("\n🔍 2단계: 삼성 관련 기업 검색")

    samsung_corps = []
    for corp in corp_list:
        corp_name = corp.get("corp_name", "")
        if "삼성" in corp_name and corp.get("stock_code", "").strip():
            samsung_corps.append(corp)

    print(f"   ✅ 총 {len(samsung_corps)}개 삼성 관련 상장기업 발견")

    for i, corp in enumerate(samsung_corps[:10]):  # 최대 10개만 표시
        print(
            f"   [{i+1}] {corp['corp_name']} (기업코드: {corp['corp_code']}, 주식코드: {corp['stock_code']})"
        )

    return samsung_corps


def test_samsung_electronics(samsung_corps):
    """삼성전자 정확한 기업코드 찾기"""
    print("\n🔍 3단계: 삼성전자 정확한 기업코드 찾기")

    # 삼성전자 후보들 찾기
    samsung_electronics_candidates = []
    for corp in samsung_corps:
        corp_name = corp.get("corp_name", "")
        if "삼성전자" in corp_name:
            samsung_electronics_candidates.append(corp)

    print(f"   ✅ 삼성전자 후보 {len(samsung_electronics_candidates)}개 발견:")

    for candidate in samsung_electronics_candidates:
        print(
            f"   - {candidate['corp_name']} (기업코드: {candidate['corp_code']}, 주식코드: {candidate['stock_code']})"
        )

        # 각 후보에 대해 보고서 검색 테스트
        print(f"     보고서 검색 테스트:")
        success = test_reports_for_corp(candidate["corp_code"], candidate["corp_name"])
        if success:
            print(f"     ✅ {candidate['corp_name']} - 보고서 발견!")
            return candidate
        else:
            print(f"     ❌ {candidate['corp_name']} - 보고서 없음")

    return None


def test_reports_for_corp(corp_code, corp_name):
    """특정 기업의 보고서 존재 여부 확인"""
    url = f"{BASE_URL}/list.json"

    # 여러 연도와 보고서 타입 테스트
    test_cases = [
        (2023, "11011"),  # 2023년 사업보고서
        (2024, "11012"),  # 2024년 반기보고서
        (2024, "11013"),  # 2024년 1분기보고서
    ]

    for year, report_code in test_cases:
        params = {
            "crtfc_key": DART_API_KEY,
            "corp_code": corp_code,
            "bsns_year": str(year),
            "reprt_code": report_code,
            "page_count": "1",
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "000" and data.get("list"):
                    print(f"       ✓ {year}년 {report_code} 보고서 발견")
                    return True
        except:
            continue

    return False


def test_alternative_search():
    """대안적 검색 방법 - 주식코드로 검색"""
    print("\n🔍 4단계: 주식코드 005930으로 직접 검색")

    # 주식코드 005930 (삼성전자)으로 최근 공시 검색
    url = f"{BASE_URL}/list.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "bgn_de": "20240101",  # 2024년 1월 1일부터
        "end_de": "20241231",  # 2024년 12월 31일까지
        "page_count": "10",
    }

    try:
        response = requests.get(url, params=params)
        print(f"   - HTTP 상태: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   - API 상태: {data.get('status')}")

            if data.get("status") == "000":
                report_list = data.get("list", [])
                print(f"   - 총 {len(report_list)}건의 공시 발견")

                # 삼성전자 관련 공시 찾기
                samsung_reports = [
                    r for r in report_list if "삼성전자" in r.get("corp_name", "")
                ]
                print(f"   - 삼성전자 공시 {len(samsung_reports)}건")

                if samsung_reports:
                    print("   삼성전자 최근 공시:")
                    for i, report in enumerate(samsung_reports[:5]):
                        corp_code = report.get("corp_code", "N/A")
                        corp_name = report.get("corp_name", "N/A")
                        report_nm = report.get("report_nm", "N/A")
                        rcept_dt = report.get("rcept_dt", "N/A")
                        print(
                            f"   [{i+1}] {corp_name} ({corp_code}) - {report_nm} ({rcept_dt})"
                        )

                    return samsung_reports[0].get("corp_code")

        return None

    except Exception as e:
        print(f"   - 예외 발생: {e}")
        return None


def main():
    """메인 함수"""
    print("🚀 DART 기업코드 검증 스크립트 시작")
    print("=" * 60)

    # 1단계: 기업코드 목록 다운로드
    corp_list = get_corp_code_list()
    if not corp_list:
        print("❌ 기업코드 목록 다운로드 실패!")
        return

    # 2단계: 삼성 관련 기업 찾기
    samsung_corps = find_samsung_companies(corp_list)
    if not samsung_corps:
        print("❌ 삼성 관련 기업을 찾을 수 없습니다!")
        return

    # 3단계: 삼성전자 정확한 기업코드 찾기
    correct_samsung = test_samsung_electronics(samsung_corps)
    if correct_samsung:
        print(f"\n✅ 정확한 삼성전자 정보:")
        print(f"   - 회사명: {correct_samsung['corp_name']}")
        print(f"   - 기업코드: {correct_samsung['corp_code']}")
        print(f"   - 주식코드: {correct_samsung['stock_code']}")
    else:
        print("\n⚠️ 기업코드 목록에서 삼성전자 보고서를 찾지 못했습니다.")

        # 4단계: 대안적 검색
        alt_corp_code = test_alternative_search()
        if alt_corp_code:
            print(f"\n✅ 대안 검색으로 삼성전자 기업코드 발견: {alt_corp_code}")

    print("\n🎯 검증 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
