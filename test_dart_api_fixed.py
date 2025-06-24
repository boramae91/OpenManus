#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수정된 DART API 문서 다운로드 테스트
"""

import json
import os
from datetime import datetime

import requests

# DART API 키
DART_API_KEY = os.getenv("DART_API_KEY")
BASE_URL = "https://opendart.fss.or.kr/api"


def test_document_download():
    """수정된 문서 다운로드 엔드포인트 테스트"""
    print("🚀 수정된 DART API 문서 다운로드 테스트")
    print("=" * 50)

    if not DART_API_KEY:
        print("❌ DART_API_KEY 환경변수가 설정되지 않았습니다!")
        return False

    # 1단계: 삼성전자 최신 사업보고서 찾기
    print("📋 1단계: 삼성전자 최신 사업보고서 검색...")

    list_params = {
        "crtfc_key": DART_API_KEY,
        "corp_code": "00126380",  # 삼성전자
        "bgn_de": "20250301",  # 2025년 3월부터 (사업보고서는 다음해 3-5월 제출)
        "end_de": "20250531",  # 2025년 5월까지
        "pblntf_detail_ty": "A001",  # 사업보고서
        "page_count": "1",
    }

    try:
        response = requests.get(f"{BASE_URL}/list.json", params=list_params)
        print(f"   - HTTP 상태: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   - API 상태: {data.get('status')}")
            print(f"   - API 메시지: {data.get('message')}")

            if data.get("status") == "000" and data.get("list"):
                report = data["list"][0]
                rcept_no = report.get("rcept_no")
                report_name = report.get("report_nm")

                print(f"   ✅ 사업보고서 발견!")
                print(f"      - 보고서명: {report_name}")
                print(f"      - 접수번호: {rcept_no}")

                # 2단계: 수정된 엔드포인트로 문서 다운로드
                print(f"\n📄 2단계: 수정된 엔드포인트로 문서 다운로드...")
                return test_document_download_with_endpoint(rcept_no, "/document.xml")
            else:
                print("   ❌ 사업보고서를 찾을 수 없습니다")
                return False
        else:
            print(f"   ❌ HTTP 오류: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ 예외 발생: {e}")
        return False


def test_document_download_with_endpoint(rcept_no: str, endpoint: str):
    """특정 엔드포인트로 문서 다운로드 테스트"""
    print(f"📥 문서 다운로드 테스트: {endpoint}")

    params = {"crtfc_key": DART_API_KEY, "rcept_no": rcept_no}

    try:
        response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        print(f"   - HTTP 상태: {response.status_code}")
        print(f"   - 응답 크기: {len(response.content):,} bytes")
        print(f"   - Content-Type: {response.headers.get('content-type', 'Unknown')}")

        if response.status_code == 200:
            content = response.text
            print(f"   - 내용 길이: {len(content):,}자")

            # XML 오류 응답 확인
            if "<?xml" in content and ("status" in content or "error" in content):
                try:
                    import xml.etree.ElementTree as ET

                    root = ET.fromstring(content)

                    error_msg = root.find(".//message")
                    if error_msg is not None:
                        print(f"   ❌ API 오류: {error_msg.text}")
                        return False
                except:
                    pass

            # 내용 미리보기
            if len(content) > 500:
                preview = content[:500].replace("\n", " ")
                print(f"   - 내용 미리보기: {preview}...")
                print("   ✅ 문서 다운로드 성공!")
                return True
            else:
                print(f"   ⚠️ 내용이 너무 짧습니다: {len(content)}자")
                print(f"   - 전체 내용: {content}")
                return False
        else:
            print(f"   ❌ HTTP 오류: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ 예외 발생: {e}")
        return False


if __name__ == "__main__":
    success = test_document_download()

    print(f"\n🎯 테스트 결과: {'성공' if success else '실패'}")

    if not success:
        print("\n💡 해결 방법:")
        print("1. DART API 키 확인")
        print("2. 네트워크 연결 확인")
        print("3. DART 서버 상태 확인")
        print("4. 접수번호 유효성 확인")
