#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔢 토큰 계산기 테스트 스크립트

PDF 섹션별 토큰 수 계산 기능을 테스트해보는 스크립트예요!
실제 사업보고서나 분기보고서와 비슷한 가상의 섹션들로 테스트해볼게요.
"""

import asyncio
import os
import sys

# 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.token_calculator import SectionTokenCalculator


def create_sample_pdf_sections():
    """
    실제 사업보고서와 비슷한 가상의 PDF 섹션들을 생성해요

    Returns:
        Dict[str, str]: 섹션명과 내용이 담긴 딕셔너리
    """
    sections = {
        "I. 회사의 개요": """
1. 회사의 개요
가. 회사의 명칭 등
(1) 회사명: 삼성전자주식회사
(2) 영문명: SAMSUNG ELECTRONICS CO., LTD.
(3) 설립일자: 1969년 1월 13일
(4) 본점 소재지: 경기도 수원시 영통구 삼성로 129
(5) 전화번호: 031-200-1114

나. 회사의 연혁
1969년 1월 삼성전자 설립
1970년 12월 TV 생산 시작
1974년 9월 반도체 사업 진출
1982년 12월 64K D-RAM 개발
1984년 6월 메모리 반도체 양산 시작
1988년 2월 휴대폰 사업 진출
1992년 4월 TFT-LCD 사업 진출

다. 자본금 변동사항
- 2023년: 778억 원
- 2022년: 778억 원
- 2021년: 778억 원

주요 변동 내역:
2010년 자기주식 소각으로 자본금 감소
2018년 주식분할로 발행주식수 증가
        """,
        "II. 사업의 내용": """
1. 사업의 개요
가. 업계현황
반도체 업계는 2023년 메모리 반도체 시장 침체로 어려움을 겪었습니다.
특히 PC 및 스마트폰 수요 감소로 D-RAM 및 낸드플래시 가격이 크게 하락했습니다.

나. 회사의 현황
(1) 영업현황
- DS(Device Solutions) 부문: 메모리 반도체, 시스템 LSI
- IM(IT & Mobile Communications) 부문: 스마트폰, 태블릿
- CE(Consumer Electronics) 부문: TV, 생활가전
- Harman 부문: 차량용 인포테인먼트

(2) 시장점유율
- 메모리 반도체: 글로벌 1위 (약 43%)
- 스마트폰: 글로벌 1위 (약 22%)
- TV: 글로벌 1위 (약 31%)

다. 주요제품 및 서비스
1) 메모리 반도체
   - D-RAM: DDR4, DDR5, LPDDR5
   - 낸드플래시: V-NAND, SSD
   - 기타: eUFS, eMCP

2) 시스템 LSI
   - 모바일 AP: Exynos 시리즈
   - 이미지센서: ISOCELL 시리즈
   - 파운드리: 3nm, 4nm, 5nm 공정
        """,
        "III. 재무에 관한 사항": """
1. 요약재무정보
(단위: 십억원, 연결기준)

가. 요약 대차대조표
                    2023년    2022년    2021년
자산총계           427,725   399,771   352,793
유동자산           195,866   173,915   157,884
비유동자산         231,859   225,856   194,909
부채총계           105,009    87,260    76,605
유동부채            61,176    54,704    59,748
비유동부채          43,833    32,556    16,857
자본총계           322,716   312,511   276,188

나. 요약 손익계산서
                    2023년    2022년    2021년
매출액             258,706   302,231   279,649
매출총이익          88,121   129,541   110,135
영업이익            15,136    43,376    51,628
당기순이익          15,445    44,206    51,635

다. 요약 현금흐름표
                    2023년    2022년    2021년
영업활동현금흐름     53,749    76,063    93,885
투자활동현금흐름    -31,162   -48,522   -38,239
재무활동현금흐름    -22,477   -28,112   -53,291

라. 주요 재무비율
                    2023년    2022년    2021년
유동비율(%)         320.2     318.0     264.2
부채비율(%)          32.5      27.9      27.7
ROE(%)               4.9      15.2      19.7
ROA(%)               3.7      11.8      15.7
        """,
        "IV. 이사의 경영진단 및 분석의견": """
1. 개요
2023년은 글로벌 경기 둔화와 높은 인플레이션의 영향으로 IT 제품 수요가 크게 위축되면서
메모리 반도체 업황이 급격히 악화된 한 해였습니다.

2. 영업실적 분석
가. 매출액 분석
- 전년 대비 14.4% 감소한 258.7조원 기록
- DS 부문: 메모리 가격 하락으로 큰 폭 감소
- IM 부문: 스마트폰 시장 침체로 매출 감소
- CE 부문: 프리미엄 제품 중심으로 안정적 성과

나. 수익성 분석
- 영업이익률: 5.8% (전년 14.4% → 5.8%)
- 메모리 사업 적자 전환이 주요 요인
- 원가절감 및 효율성 개선 노력 지속

3. 재무상태 분석
가. 자산 현황
- 총자산 427.7조원으로 전년 대비 7.0% 증가
- 현금 및 현금성자산 29.0조원 보유

나. 부채 및 자본 현황
- 부채비율 32.5%로 양호한 재무구조 유지
- 자기자본비율 75.4%로 안정적

4. 향후 전망
메모리 시장은 2024년 하반기부터 점진적 회복 예상
AI 및 서버 수요 증가로 HBM 등 고부가가치 제품 성장 기대
        """,
        "V. 회계감사인의 감사의견 등": """
1. 회계감사인의 명칭 및 감사의견
가. 회계감사인의 명칭: 삼일회계법인
나. 감사의견: 적정(무한정 적정의견)

다. 핵심감사사항
(1) 반도체 사업부문 재고자산의 평가
반도체 시장의 급격한 변화로 인한 재고자산 평가손실 위험

(2) 지적재산권의 손상평가
기술 변화가 빠른 IT 업계 특성상 지적재산권의 손상 위험

(3) 수익인식
복잡한 제품 포트폴리오와 글로벌 영업 구조로 인한 수익인식 복잡성

2. 감사용역 체결현황
구분           감사법인        보수(백만원)
당기           삼일           2,950
전기           삼일           2,850
전전기         삼일           2,750

3. 회계법인과의 비감사용역 계약체결 현황
- 세무자문: 150백만원
- 기타 자문: 50백만원
        """,
        "[주석] 1. 일반사항": """
1.1 지배기업의 개요
삼성전자주식회사(이하 "회사")는 1969년 1월 13일에 설립되어 반도체, 휴대폰,
TV 등을 제조 및 판매하는 기업입니다.

1.2 연결대상 종속기업 현황
연결재무제표에 포함된 종속기업은 다음과 같습니다:
- 삼성디스플레이(주): 100%
- 삼성SDI(주): 19.6%
- 삼성전기(주): 25.9%
- 삼성SDS(주): 64.6%

1.3 연결재무제표 작성기준
본 연결재무제표는 한국채택국제회계기준(K-IFRS)에 따라 작성되었습니다.

1.4 기능통화와 표시통화
회사의 기능통화는 원화이며, 연결재무제표는 원화로 표시되었습니다.
        """,
        "[주석] 15. 재고자산": """
15.1 재고자산의 구성
(단위: 십억원)
                     2023년      2022년
제품                 28,445      25,387
반제품               15,233      13,892
원재료               8,967       7,543
저장품               1,455       1,289
평가손실충당금       (2,100)     (1,111)
합계                 52,000      47,000

15.2 재고자산평가손실
당기 중 인식한 재고자산평가손실은 다음과 같습니다:
- 메모리 반도체: 1,500십억원
- 시스템 LSI: 400십억원
- 기타: 200십억원

15.3 재고자산 담보제공
당기말 현재 담보로 제공된 재고자산은 없습니다.

15.4 재고자산회전율
재고자산회전율: 5.2회 (전년 6.4회)
재고자산회전기간: 70일 (전년 57일)
        """,
    }

    return sections


def create_expert_section_mapping():
    """
    전문가별로 필요한 섹션들을 매핑해요

    Returns:
        Dict[str, List[str]]: 전문가별 섹션 리스트
    """
    return {
        # "fundamental_analyst": [  # 🚫 비활성화 (통합 재무분석가로 대체)
        #     "III. 재무에 관한 사항",
        #     "[주석] 15. 재고자산",
        #     "IV. 이사의 경영진단 및 분석의견",
        # ],
        # "industry_analyst": [  # 🚫 비활성화 (개발 시간 절약)
        #     "II. 사업의 내용",
        #     "I. 회사의 개요",
        #     "IV. 이사의 경영진단 및 분석의견",
        # ],
        # "risk_assessor": [  # 🚫 비활성화 (개발 시간 절약)
        #     "V. 회계감사인의 감사의견 등",
        #     "[주석] 1. 일반사항",
        #     "III. 재무에 관한 사항",
        # ],
        # "valuation_expert": [  # 🚫 비활성화 (통합 재무분석가로 대체)
        #     "III. 재무에 관한 사항",
        #     "IV. 이사의 경영진단 및 분석의견",
        #     "II. 사업의 내용",
        # ],
        # "footnote_specialist": ["[주석] 1. 일반사항", "[주석] 15. 재고자산"],  # 🚫 비활성화 (개발 시간 절약)
    }


async def test_token_calculator():
    """토큰 계산기 기능을 테스트해요"""
    print("🔢 토큰 계산기 테스트 시작!")
    print("=" * 60)

    # 토큰 계산기 초기화
    calculator = SectionTokenCalculator(model_name="gpt-4o")

    # 샘플 PDF 섹션들 생성
    print("\n📄 샘플 PDF 섹션 생성...")
    sections = create_sample_pdf_sections()
    print(f"✅ {len(sections)}개 섹션 생성됨")

    # 전체 섹션 토큰 분석
    print("\n🔍 전체 섹션 토큰 분석...")
    analysis = calculator.analyze_sections_tokens(sections)

    print(f"📊 전체 분석 결과:")
    print(f"   • 총 섹션 수: {analysis['total_sections']:,}개")
    print(f"   • 총 토큰 수: {analysis['total_tokens']:,}토큰")
    print(f"   • 총 글자 수: {analysis['total_characters']:,}자")
    print(
        f"   • 평균 토큰/섹션: {analysis['statistics']['avg_tokens_per_section']:,.0f}토큰"
    )
    print(
        f"   • 최대 토큰/섹션: {analysis['statistics']['max_tokens_per_section']:,}토큰"
    )
    print(
        f"   • 모델 제한 적합성: {'✅ 적합' if analysis['model_limits']['can_fit_all_sections'] else '❌ 초과'}"
    )

    # 섹션별 상세 토큰 수 출력
    print(f"\n📋 섹션별 토큰 수 (토큰 수 기준 정렬):")
    sorted_sections = sorted(
        analysis["section_details"].items(),
        key=lambda x: x[1]["token_count"],
        reverse=True,
    )

    for i, (name, info) in enumerate(sorted_sections, 1):
        percentage = (info["token_count"] / analysis["total_tokens"]) * 100
        print(f"{i:2d}. {name}")
        print(f"    • 토큰: {info['token_count']:,}개 ({percentage:.1f}%)")
        print(f"    • 글자: {info['character_count']:,}자")
        print(f"    • 비율: {info['tokens_per_char']:.3f}토큰/글자")
        print()

    # 전문가별 토큰 분석
    print("\n👨‍💼 전문가별 토큰 분석...")
    expert_sections = create_expert_section_mapping()
    expert_analysis = calculator.calculate_expert_tokens(expert_sections, sections)

    print(f"📊 전문가별 토큰 수:")
    for expert_name, analysis_data in expert_analysis.items():
        status = "✅ 적합" if analysis_data["can_fit_in_context"] else "❌ 초과"
        print(
            f"   • {expert_name}: {analysis_data['total_tokens']:,}토큰 ({analysis_data['section_count']}개 섹션) {status}"
        )
        print(f"     - 사용률: {analysis_data['token_usage_percentage']:.1f}%")

    # 토큰 제한 초과 시 최적화 제안
    if not analysis["model_limits"]["can_fit_all_sections"]:
        print("\n💡 토큰 최적화 제안...")
        optimal_combination = calculator.find_optimal_section_combination(sections)

        print(f"🎯 최적 조합:")
        print(f"   • 선택된 섹션: {optimal_combination['total_selected_sections']}개")
        print(f"   • 총 토큰: {optimal_combination['total_selected_tokens']:,}토큰")
        print(f"   • 활용률: {optimal_combination['token_utilization']:.1f}%")

        print(f"\n📋 선택된 섹션들:")
        for i, section in enumerate(optimal_combination["selected_sections"], 1):
            truncated = " (일부 생략)" if section.get("truncated") else ""
            print(f"{i:2d}. {section['name']}: {section['tokens']:,}토큰{truncated}")

        if optimal_combination["excluded_sections"]:
            print(f"\n❌ 제외된 섹션들:")
            for section in optimal_combination["excluded_sections"]:
                print(f"   • {section['name']}: {section['tokens']:,}토큰")

    # 요약 보고서 생성
    print("\n📋 토큰 분석 요약 보고서 생성...")
    report = calculator.create_section_summary_report(sections)

    # 보고서를 파일로 저장
    report_filename = "token_analysis_report.txt"
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ 보고서가 '{report_filename}' 파일로 저장되었습니다!")

    print("\n" + "=" * 60)
    print("🎉 토큰 계산기 테스트 완료!")

    return analysis, expert_analysis


def test_real_dart_data_simulation():
    """실제 DART 데이터 크기를 시뮬레이션하여 토큰 사용량을 계산해요"""
    print("\n" + "=" * 60)
    print("🔍 실제 DART 데이터 토큰 사용량 시뮬레이션")
    print("=" * 60)

    calculator = SectionTokenCalculator()

    # 실제 DART 데이터 크기 시뮬레이션
    dart_data_sizes = {
        "사업보고서_기본": 50000,  # 5만자 (기본 사업보고서)
        "사업보고서_상세": 200000,  # 20만자 (상세 사업보고서)
        "분기보고서_기본": 100000,  # 10만자 (기본 분기보고서)
        "분기보고서_상세": 500000,  # 50만자 (상세 분기보고서)
        "분기보고서_최대": 2000000,  # 200만자 (최대 분기보고서)
    }

    # yfinance 데이터 크기
    yfinance_data_size = 15000  # 1.5만자 (yfinance 기본 데이터)

    # 웹 검색 결과 크기
    web_search_size = 25000  # 2.5만자 (웹 검색 결과)

    print("📊 데이터 소스별 토큰 사용량:")
    print("-" * 40)

    total_tokens = 0

    for data_type, char_count in dart_data_sizes.items():
        tokens = calculator.count_tokens("A" * char_count)  # 시뮬레이션용 텍스트
        total_tokens += tokens
        print(f"• {data_type}: {char_count:,}자 → {tokens:,}토큰")

    yfinance_tokens = calculator.count_tokens("A" * yfinance_data_size)
    web_search_tokens = calculator.count_tokens("A" * web_search_size)
    total_tokens += yfinance_tokens + web_search_tokens

    print(f"• yfinance 데이터: {yfinance_data_size:,}자 → {yfinance_tokens:,}토큰")
    print(f"• 웹 검색 결과: {web_search_size:,}자 → {web_search_tokens:,}토큰")

    print("\n📈 토큰 사용량 분석:")
    print("-" * 40)
    print(f"• 총 토큰 수: {total_tokens:,}토큰")
    print(f"• GPT-4o 최대: {calculator.get_max_tokens():,}토큰")
    print(f"• 사용 가능: {calculator.get_available_tokens():,}토큰")
    print(f"• 사용률: {(total_tokens/calculator.get_available_tokens())*100:.1f}%")

    # 2명 체제에서 각 전문가별 토큰 분배
    print("\n👥 2명 체제 전문가별 토큰 분배:")
    print("-" * 40)

    # 통합 재무분석가 (펀더멘털 + 밸류에이션)
    fundamental_tokens = total_tokens * 0.6  # 60% (더 많은 데이터 처리)
    technical_tokens = total_tokens * 0.4  # 40%

    print(f"• 통합 재무분석가: {fundamental_tokens:,.0f}토큰 (60%)")
    print(f"• 기술적 분석가: {technical_tokens:,.0f}토큰 (40%)")

    # LangChain Chain max_tokens=8,000 검증
    print("\n🔍 LangChain Chain 토큰 제한 검증:")
    print("-" * 40)

    chain_max_tokens = 8000
    print(f"• Chain max_tokens: {chain_max_tokens:,}토큰")
    print(f"• 통합 재무분석가 입력: {fundamental_tokens:,.0f}토큰")
    print(f"• 기술적 분석가 입력: {technical_tokens:,.0f}토큰")

    if fundamental_tokens > chain_max_tokens:
        print("⚠️ 통합 재무분석가: 입력 토큰이 Chain 제한을 초과합니다!")
        print(f"   초과량: {fundamental_tokens - chain_max_tokens:,.0f}토큰")
    else:
        print("✅ 통합 재무분석가: Chain 제한 내에서 처리 가능")

    if technical_tokens > chain_max_tokens:
        print("⚠️ 기술적 분석가: 입력 토큰이 Chain 제한을 초과합니다!")
        print(f"   초과량: {technical_tokens - chain_max_tokens:,.0f}토큰")
    else:
        print("✅ 기술적 분석가: Chain 제한 내에서 처리 가능")

    # 최적화 제안
    print("\n💡 최적화 제안:")
    print("-" * 40)

    if fundamental_tokens > chain_max_tokens or technical_tokens > chain_max_tokens:
        print("🚨 문제: 입력 토큰이 Chain 제한을 초과합니다!")
        print("🔧 해결방안:")
        print("1. LangChain Chain의 max_tokens를 입력 토큰에 맞게 조정")
        print("2. 데이터 압축 및 요약 강화")
        print("3. 전문가별 데이터 분할 최적화")
        print("4. 토큰 계산기 기반 동적 조정")
    else:
        print("✅ 현재 설정으로 충분히 처리 가능합니다!")
        print("📝 추가 최적화:")
        print("1. 토큰 사용량 모니터링")
        print("2. 데이터 품질과 양의 균형 조정")


if __name__ == "__main__":
    # 비동기 실행
    asyncio.run(test_token_calculator())
    test_real_dart_data_simulation()
