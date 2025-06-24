# DART API 디버깅 도우미 스크립트
# 사용자가 DART API 연결 문제를 쉽게 진단할 수 있도록 도와주는 프로그램이에요

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta

import requests

# 환경변수 로드 시도
try:
    from dotenv import load_dotenv

    load_dotenv()  # .env 파일에서 환경변수 로드
    print("✅ .env 파일이 로드되었습니다.")
except ImportError:
    print("⚠️ python-dotenv가 설치되지 않음 - 시스템 환경변수만 사용")


class DartApiDebugger:
    """
    DART API 연결 및 데이터 조회를 테스트하는 디버깅 클래스

    사용자에게 쉽게 설명하면, DART 서버와의 연결 상태를 점검하고
    문제가 있는 부분을 찾아내는 진단 도구예요
    """

    def __init__(self):
        self.dart_api_key = os.getenv("DART_API_KEY")
        self.base_url = "https://opendart.fss.or.kr/api"
        self.test_results = {}

    def check_api_key(self):
        """API 키 설정 상태 확인"""
        print("🔑 1단계: DART API 키 확인")
        print("-" * 30)

        if not self.dart_api_key:
            print("❌ DART API 키가 설정되지 않았습니다!")
            print("💡 해결방법:")
            print("  1. python dart_api_setup.py 실행")
            print("  2. 또는 환경변수 DART_API_KEY 설정")
            self.test_results["api_key"] = False
            return False

        print(f"✅ API 키 설정됨: {self.dart_api_key[:10]}...{self.dart_api_key[-4:]}")
        print(f"📏 키 길이: {len(self.dart_api_key)}자 (정상: 40자)")

        if len(self.dart_api_key) != 40:
            print("⚠️ API 키 길이가 비정상적입니다!")
            self.test_results["api_key"] = False
            return False

        self.test_results["api_key"] = True
        return True

    def test_basic_connection(self):
        """기본 API 연결 테스트"""
        print("\n🌐 2단계: DART API 기본 연결 테스트")
        print("-" * 35)

        if not self.dart_api_key:
            print("❌ API 키가 없어서 연결 테스트를 할 수 없습니다.")
            self.test_results["connection"] = False
            return False

        try:
            # 기업 개황 조회로 연결 테스트 (삼성전자 사용)
            test_url = f"{self.base_url}/company.json"
            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": "00126380",  # 삼성전자
            }

            print("📡 테스트 요청 중...")
            response = requests.get(test_url, params=params, timeout=10)
            print(f"   - 응답 상태: {response.status_code}")
            print(f"   - 응답 시간: {response.elapsed.total_seconds():.2f}초")

            if response.status_code == 200:
                data = response.json()
                api_status = data.get("status", "알 수 없음")
                print(f"   - API 상태코드: {api_status}")

                if api_status == "000":
                    print("✅ DART API 연결 성공!")
                    company_name = data.get("corp_name", "정보없음")
                    print(f"   - 테스트 기업: {company_name}")
                    self.test_results["connection"] = True
                    return True
                else:
                    print(f"❌ API 오류: {data.get('message', '알 수 없는 오류')}")
                    self.test_results["connection"] = False
                    return False
            else:
                print(f"❌ HTTP 오류: {response.status_code}")
                self.test_results["connection"] = False
                return False

        except requests.exceptions.Timeout:
            print("❌ 연결 시간 초과 (10초)")
            self.test_results["connection"] = False
            return False
        except Exception as e:
            print(f"❌ 연결 오류: {e}")
            self.test_results["connection"] = False
            return False

    def test_business_report_search(
        self, corp_code="00126380", company_name="삼성전자"
    ):
        """사업보고서 검색 테스트"""
        print(f"\n📋 3단계: 사업보고서 검색 테스트 ({company_name})")
        print("-" * 40)

        if not self.test_results.get("connection"):
            print("❌ API 연결이 안 되어 있어서 테스트할 수 없습니다.")
            return False

        try:
            # 최근 3년간 사업보고서 검색
            current_year = datetime.now().year
            test_years = [str(current_year - i) for i in range(3)]

            for year in test_years:
                print(f"🔍 {year}년 사업보고서 검색 중...")

                params = {
                    "crtfc_key": self.dart_api_key,
                    "corp_code": corp_code,
                    "bsns_year": year,
                    "reprt_code": "11011",  # 사업보고서
                    "page_count": "1",
                }

                response = requests.get(f"{self.base_url}/list.json", params=params)

                if response.status_code == 200:
                    data = response.json()
                    api_status = data.get("status")
                    report_list = data.get("list", [])

                    print(f"   - API 상태: {api_status}")
                    print(f"   - 보고서 개수: {len(report_list)}개")

                    if api_status == "000" and report_list:
                        report = report_list[0]
                        print(f"   ✅ 발견: {report.get('report_nm', '제목없음')}")
                        print(f"      - 접수번호: {report.get('rcept_no', '없음')}")
                        print(f"      - 제출일: {report.get('flr_nm', '없음')}")
                        self.test_results["business_report"] = True
                        return True
                    else:
                        print(f"   ⚠️ {year}년 사업보고서 없음")
                else:
                    print(f"   ❌ HTTP 오류: {response.status_code}")

            print("❌ 최근 3년간 사업보고서를 찾을 수 없습니다.")
            self.test_results["business_report"] = False
            return False

        except Exception as e:
            print(f"❌ 사업보고서 검색 오류: {e}")
            self.test_results["business_report"] = False
            return False

    def test_quarterly_report_search(
        self, corp_code="00126380", company_name="삼성전자"
    ):
        """분기보고서 검색 테스트"""
        print(f"\n📈 4단계: 분기보고서 검색 테스트 ({company_name})")
        print("-" * 40)

        if not self.test_results.get("connection"):
            print("❌ API 연결이 안 되어 있어서 테스트할 수 없습니다.")
            return False

        try:
            # 현재 시점 기준 검색 전략
            current_month = datetime.now().month
            current_year = datetime.now().year

            if current_month <= 5:
                test_years = [str(current_year - 1), str(current_year)]
            else:
                test_years = [str(current_year), str(current_year - 1)]

            quarterly_codes = ["11014", "11012", "11013"]  # 3분기, 반기, 1분기
            quarterly_names = ["3분기", "반기", "1분기"]

            print(f"🗓️ 현재 {current_month}월 기준 검색 전략")
            print(f"   - 검색 연도: {', '.join(test_years)}")

            for year in test_years:
                print(f"\n📅 {year}년 분기보고서 검색 중...")

                for code, name in zip(quarterly_codes, quarterly_names):
                    params = {
                        "crtfc_key": self.dart_api_key,
                        "corp_code": corp_code,
                        "bsns_year": year,
                        "reprt_code": code,
                        "page_count": "1",
                    }

                    response = requests.get(f"{self.base_url}/list.json", params=params)

                    if response.status_code == 200:
                        data = response.json()
                        api_status = data.get("status")
                        report_list = data.get("list", [])

                        print(
                            f"   {name}보고서: 상태 {api_status}, {len(report_list)}개"
                        )

                        if api_status == "000" and report_list:
                            report = report_list[0]
                            print(f"   ✅ {year}년 {name}보고서 발견!")
                            print(
                                f"      - 제목: {report.get('report_nm', '제목없음')}"
                            )
                            print(f"      - 접수번호: {report.get('rcept_no', '없음')}")
                            self.test_results["quarterly_report"] = True
                            return True

            print("❌ 최근 2년간 분기보고서를 찾을 수 없습니다.")
            self.test_results["quarterly_report"] = False
            return False

        except Exception as e:
            print(f"❌ 분기보고서 검색 오류: {e}")
            self.test_results["quarterly_report"] = False
            return False

    def test_document_download(self, test_rcept_no=None):
        """보고서 원문 다운로드 테스트"""
        print("\n📄 5단계: 보고서 원문 다운로드 테스트")
        print("-" * 35)

        if not self.test_results.get("connection"):
            print("❌ API 연결이 안 되어 있어서 테스트할 수 없습니다.")
            return False

        # 테스트용 접수번호가 없으면 삼성전자 최신 보고서 찾기
        if not test_rcept_no:
            print("🔍 테스트용 보고서 접수번호 검색 중...")
            try:
                params = {
                    "crtfc_key": self.dart_api_key,
                    "corp_code": "00126380",  # 삼성전자
                    "bsns_year": str(datetime.now().year - 1),
                    "reprt_code": "11011",  # 사업보고서
                    "page_count": "1",
                }

                response = requests.get(f"{self.base_url}/list.json", params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "000" and data.get("list"):
                        test_rcept_no = data["list"][0].get("rcept_no")
                        print(f"   - 테스트용 접수번호: {test_rcept_no}")
            except:
                pass

        if not test_rcept_no:
            print("❌ 테스트용 보고서를 찾을 수 없습니다.")
            return False

        try:
            print(f"📥 보고서 원문 다운로드 시도: {test_rcept_no}")

            params = {"crtfc_key": self.dart_api_key, "rcept_no": test_rcept_no}

            response = requests.get(
                f"{self.base_url}/document.json", params=params, timeout=30
            )
            print(f"   - HTTP 상태: {response.status_code}")
            print(f"   - 응답 크기: {len(response.content):,} bytes")

            if response.status_code == 200:
                # JSON 응답인지 확인 (에러인 경우)
                try:
                    json_data = response.json()
                    if json_data.get("status") != "000":
                        print(f"❌ API 오류: {json_data.get('message')}")
                        return False
                except:
                    # JSON이 아니면 정상적인 원문 내용
                    pass

                content = response.text
                print(f"   - 내용 길이: {len(content):,}자")

                if len(content) > 1000:
                    print("✅ 보고서 원문 다운로드 성공!")
                    print(f"   - 내용 미리보기: {content[:100]}...")
                    self.test_results["document_download"] = True
                    return True
                else:
                    print("⚠️ 다운로드된 내용이 너무 짧습니다.")
                    self.test_results["document_download"] = False
                    return False
            else:
                print(f"❌ HTTP 오류: {response.status_code}")
                self.test_results["document_download"] = False
                return False

        except requests.exceptions.Timeout:
            print("❌ 다운로드 시간 초과 (30초)")
            self.test_results["document_download"] = False
            return False
        except Exception as e:
            print(f"❌ 다운로드 오류: {e}")
            self.test_results["document_download"] = False
            return False

    def print_summary(self):
        """테스트 결과 요약"""
        print("\n" + "=" * 50)
        print("🎯 DART API 진단 결과 요약")
        print("=" * 50)

        tests = [
            ("API 키 설정", "api_key"),
            ("기본 연결", "connection"),
            ("사업보고서 검색", "business_report"),
            ("분기보고서 검색", "quarterly_report"),
            ("원문 다운로드", "document_download"),
        ]

        passed = 0
        total = len(tests)

        for test_name, key in tests:
            result = self.test_results.get(key, False)
            status = "✅ 성공" if result else "❌ 실패"
            print(f"{test_name:<15}: {status}")
            if result:
                passed += 1

        print(f"\n📊 전체 결과: {passed}/{total} 테스트 통과")

        if passed == total:
            print("🎉 모든 테스트가 성공했습니다!")
            print("💡 DART API가 정상적으로 작동합니다.")
        else:
            print("\n🚨 문제가 발견되었습니다:")

            if not self.test_results.get("api_key"):
                print("   1. python dart_api_setup.py 실행하여 API 키 설정")

            if not self.test_results.get("connection"):
                print("   2. 네트워크 연결 및 방화벽 설정 확인")

            if not self.test_results.get("business_report"):
                print("   3. 해당 기업의 사업보고서 공시 여부 확인")

            if not self.test_results.get("quarterly_report"):
                print("   4. 해당 기업의 분기보고서 공시 여부 확인")

            if not self.test_results.get("document_download"):
                print("   5. DART 서버 상태 또는 대용량 파일 다운로드 설정 확인")


def main():
    """메인 함수"""
    print("🔍 DART API 종합 진단 도구")
    print("=" * 40)
    print("이 프로그램은 DART API 연결 문제를 진단해드려요!")
    print()

    # 사용자 입력
    print("📝 테스트할 기업 정보를 입력하세요:")
    corp_code = input("기업고유코드 (기본값: 00126380 - 삼성전자): ").strip()
    if not corp_code:
        corp_code = "00126380"

    company_name = input("회사명 (기본값: 삼성전자): ").strip()
    if not company_name:
        company_name = "삼성전자"

    print(f"\n🎯 테스트 대상: {company_name} ({corp_code})")
    print()

    # 진단 시작
    debugger = DartApiDebugger()

    # 1. API 키 확인
    debugger.check_api_key()

    # 2. 기본 연결 테스트
    debugger.test_basic_connection()

    # 3. 사업보고서 검색 테스트
    debugger.test_business_report_search(corp_code, company_name)

    # 4. 분기보고서 검색 테스트
    debugger.test_quarterly_report_search(corp_code, company_name)

    # 5. 원문 다운로드 테스트
    debugger.test_document_download()

    # 6. 결과 요약
    debugger.print_summary()


if __name__ == "__main__":
    main()
