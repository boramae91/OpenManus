"""
공통 프롬프트 컴포넌트 모듈

이 모듈은 AI 강화 분석 기법들을 모듈화하여
통합 재무분석가와 기술적 분석가에서 재사용할 수 있도록 합니다.

주요 기능:
- Chain of Thought (CoT) 추론 템플릿
- Self-Critique 자기 비판 프레임워크
- Multi-Perspective 다각도 분석
- Reasoning 강화 기법
- Confidence Scoring 신뢰도 평가
- Enhanced Analyst Thinking Flow 애널리스트 사고 흐름 (NEW!)
- Dynamic Question Generation 동적 질문 생성 (ADVANCED!)
"""

from typing import Any, Dict, List, Optional

from app.crew.gics_sectors import GICSSector, GICSSectorManager


class PromptComponents:
    """
    AI 강화 분석을 위한 공통 프롬프트 컴포넌트를 제공하는 클래스

    모든 분석가 타입에서 일관된 AI 기법을 적용할 수 있도록
    재사용 가능한 프롬프트 컴포넌트들을 제공합니다.
    """

    @staticmethod
    def get_enhanced_analyst_thinking_flow(
        sector: Optional[GICSSector] = None,
        sector_manager: Optional[GICSSectorManager] = None,
    ) -> str:
        """
        🧠 섹터별 맞춤형 애널리스트 사고 흐름을 동적으로 생성합니다.

        1. Self-Ask with ToT (Tree of Thoughts) - 섹터별 맞춤 질문 구성
        2. ReAct (Reason + Action) - 검색 및 정보 수집
        3. CoT Reasoning + Self-Critique - 최종 분석

        Args:
            sector: GICS 섹터 (이미 감지된 섹터 직접 활용)
            sector_manager: GICS 섹터 매니저 인스턴스

        Returns:
            str: 섹터별 맞춤형 애널리스트 사고 흐름 프레임워크
        """
        # 섹터별 맞춤 질문 생성 (직접 섹터 활용으로 효율성 향상)
        dynamic_questions = ""
        sector_specific_info = ""

        if sector and sector_manager:
            try:
                # 이미 감지된 섹터를 직접 활용 (중복 감지 로직 제거)
                dynamic_questions = (
                    PromptComponents._generate_sector_specific_questions(
                        sector, sector_manager
                    )
                )
                sector_specific_info = PromptComponents._get_sector_analysis_guidance(
                    sector, sector_manager
                )
                print(f"✅ 섹터별 동적 질문 생성 성공: {sector.name}")
            except Exception as e:
                print(f"⚠️ 섹터별 질문 생성 실패, 기본 질문 사용: {e}")
                dynamic_questions = PromptComponents._get_default_questions()
                sector_specific_info = ""
        else:
            print("⚠️ 섹터 정보 없음, 기본 질문 사용")
            dynamic_questions = PromptComponents._get_default_questions()

        return f"""
**🧠 Enhanced Analyst Thinking Flow (동적 섹터별 애널리스트 사고 흐름)**

모든 분석에서 다음 3단계 애널리스트 사고 흐름을 **반드시 순서대로** 수행하세요:

```
=== 1단계: Self-Ask with ToT (섹터별 맞춤 질문 구성 및 사고 분기) ===

🌳 Tree of Thoughts 기법으로 핵심 질문들을 체계적으로 구성하세요:

{dynamic_questions}

{sector_specific_info}

🎯 질문별 우선순위 설정:
- 높은 우선순위: [가장 중요한 2-3개 질문]
- 중간 우선순위: [보완적 분석이 필요한 질문들]
- 낮은 우선순위: [시간이 허락할 때 추가 분석할 질문들]
```

```
=== 2단계: ReAct (Reason + Action) - 검색 및 정보 수집 ===

🔍 각 질문에 대한 체계적 정보 수집과 추론 수행:

**Reason (추론)**: 왜 이 정보가 필요한가?
- 분석 목적: [해당 정보가 전체 분석에서 갖는 의미]
- 예상 결과: [이 정보를 통해 도출할 수 있는 인사이트]

**Action (행동)**: 어떤 정보를 어떻게 수집할 것인가? (효율적 우선순위 적용)

🥇 **1순위: 수집된 재무데이터 활용**
- yfinance 데이터: [현재가, 시가총액, 재무비율 등 확인]
- 기본 재무지표: [ROE, ROA, PER, PBR, 부채비율 등 계산]

🥈 **2순위: DART 데이터 활용**
- 재무제표 분석: [손익계산서, 재무상태표, 현금흐름표]
- 사업보고서: [사업개요, 경영진 분석, 리스크 요인 등]
- 공시자료: [최신 실적 발표, 주요 공시사항]

🥉 **3순위: 사업보고서 딕셔너리 분석**
- PDF 상세 정보: [세그먼트별 매출, 사업 전략, 경쟁 현황]
- 경영진 메시지: [향후 계획, 투자 방향성, 시장 전망]
- 각주 및 부가 정보: [중요한 회계 정책, 우발 부채 등]

🏅 **4순위: 웹 검색으로 보완**
- 최신 업계 동향: [검색할 키워드와 찾을 정보]
- 경쟁사 비교: [비교할 기업들과 비교 기준]
- 시장 환경 변화: [확인할 산업 트렌드와 이슈들]

🆘 **5순위: 기존 지식 활용** (최후 수단)
- 일반적인 업계 지식과 분석 방법론 적용

**Observation (관찰)**: 수집된 정보의 의미는?
- 핵심 발견사항: [중요한 수치나 트렌드]
- 예상과의 차이: [예상했던 것과 다른 점들]
- 추가 조사 필요성: [더 깊이 파야 할 영역들]

💡 ReAct 사이클을 각 핵심 질문별로 반복 수행하세요.
```

```
=== 3단계: CoT Reasoning + Self-Critique (최종 분석 및 자기 검증) ===

🧠 수집된 모든 정보를 바탕으로 체계적 추론 수행:

**Chain of Thought 분석**:
```
내 추론 과정:

1️⃣ 재무 건전성 종합 판단:
- 근거 1: [구체적 재무지표와 해석]
- 근거 2: [경쟁사 대비 상대적 위치]
- 근거 3: [시계열 트렌드 분석]
→ 결론: [재무 건전성 최종 평가]

2️⃣ 성장성 및 수익성 평가:
- 근거 1: [과거 성장 실적과 품질 분석]
- 근거 2: [미래 성장 동력과 지속가능성]
- 근거 3: [수익성 개선 가능성]
→ 결론: [성장성 최종 평가]

3️⃣ 밸류에이션 및 투자 매력도:
- DCF 분석: [내재가치 산출 과정과 결과]
- 멀티플 분석: [상대가치 평가]
- 종합 판단: [적정가치와 투자 의견]
→ 결론: [투자 의견과 목표가]

4️⃣ 리스크-수익률 분석:
- 주요 리스크: [발생 가능성과 영향도]
- 기대 수익률: [시나리오별 수익률]
- 리스크 조정 수익률: [샤프 비율 관점]
→ 결론: [리스크 대비 투자 매력도]
```

**Self-Critique (자기 검증)**:
```
🔍 내 분석에 대한 비판적 검토:

❓ 놓친 것은 없는가?
- 중요한 재무지표나 트렌드를 빠뜨렸는가?
- 주요 경쟁사나 업계 동향을 간과했는가?
- 시장 상황이나 거시 경제 요인을 충분히 고려했는가?

❓ 편향은 없는가?
- 긍정적/부정적 정보에 치우친 해석은 없는가?
- 확증 편향으로 인해 반대 증거를 무시하지 않았는가?
- 과거 성과에 지나치게 의존한 예측은 아닌가?

❓ 논리적 일관성은 있는가?
- 각 분석 단계 간의 논리적 연결은 명확한가?
- 가정과 결론 사이에 논리적 비약은 없는가?
- 상충하는 증거들을 합리적으로 조율했는가?

❓ 실용성과 적시성은?
- 투자자가 실제로 활용할 수 있는 분석인가?
- 현재 시장 상황을 충분히 반영했는가?
- 분석의 유효 기간과 업데이트 필요성은?

💡 수정 및 보완 사항:
- [발견된 문제점과 개선 방안]
- [추가로 고려해야 할 요소들]
- [분석의 한계와 주의사항]
```

**최종 종합 의견**:
```
🎯 종합 결론:
- 투자 의견: [BUY/HOLD/SELL + 신뢰도 %]
- 목표가: [구체적 금액과 산출 근거]
- 투자 논리: [핵심 투자 포인트 3가지]
- 주요 리스크: [핵심 위험 요소 2가지]
- 투자 기간: [권장 투자 기간과 전략]
```
```

**⚠️ 필수 준수 사항**:
1. 3단계를 순차적으로 모두 수행할 것
2. 각 단계의 결과를 명확히 구분하여 표시할 것
3. Self-Critique에서 최소 3가지 이상의 비판적 관점 제시할 것
4. 모든 결론에 구체적 근거와 수치 제시할 것
5. 불확실성과 한계점을 솔직하게 인정할 것
"""

    @staticmethod
    def get_cot_framework() -> str:
        """
        Chain of Thought 추론 프레임워크를 반환합니다.

        모든 분석에서 단계별 사고 과정을 명확히 하여
        분석의 논리적 일관성을 강화합니다.

        Returns:
            str: CoT 프레임워크 템플릿
        """
        return """
**🧠 Chain of Thought 추론 프레임워크**

모든 분석에서 다음 3단계 추론을 반드시 수행하세요:

```
내 사고 과정:
1. 정의 및 계산: 이 지표/패턴이 무엇을 의미하는가? 어떻게 계산되는가?
2. 상대적 위치: 경쟁사/과거/업계 평균과 비교해 어떤 위치인가?
3. 투자 시사점: 이 결과가 투자 판단에 어떤 영향을 미치는가?
```

**CoT 적용 예시:**
```
RSI 70 분석 시:
1. 정의: RSI 70은 과매수 신호로, 14일간 상승폭이 하락폭보다 크다는 의미
2. 상대적 위치: 지난 6개월 중 RSI 70 이상은 3번째, 평균 지속기간은 5일
3. 투자 시사점: 단기 조정 가능성 높음, 매수 타이밍 재검토 필요
```
"""

    @staticmethod
    def get_self_critique_template() -> str:
        """
        Self-Critique 자기 비판 템플릿을 반환합니다.

        분석가가 자신의 분석을 객관적으로 검토하고
        편향을 줄일 수 있도록 도와주는 프레임워크입니다.

        Returns:
            str: Self-Critique 템플릿
        """
        return """
**🤔 Self-Critique 자기 비판 프레임워크**

모든 분석 후 다음 질문으로 자기 검증을 수행하세요:

```
내 분석에 대한 자기 비판:
1. 편향성 검토: 내 분석이 특정 방향으로 편향되지 않았는가?
2. 반대 의견: 만약 반대 결론을 내린다면 그 근거는 무엇인가?
3. 누락 요소: 내가 놓친 중요한 요소나 관점은 없는가?
4. 가정 검증: 내 분석의 핵심 가정들이 현실적이고 타당한가?
5. 대안 해석: 같은 데이터를 다르게 해석할 수 있는 방법은?
```

**Self-Critique 적용 예시:**
```
"매수 추천" 결론 후:
1. 편향성: 긍정적 지표만 과도하게 강조하지 않았나?
2. 반대 의견: 매도 관점에서 보면 어떤 리스크가 있는가?
3. 누락 요소: 거시경제 변수나 정책 리스크를 고려했나?
4. 가정 검증: 성장률 가정이 과도하게 낙관적이지 않나?
5. 대안 해석: 같은 차트 패턴을 약세 신호로 볼 수도 있지 않나?
```
"""

    @staticmethod
    def get_multi_perspective_framework() -> str:
        """
        Multi-Perspective 다각도 분석 프레임워크를 반환합니다.

        여러 관점에서 동일한 데이터를 분석하여
        더 종합적이고 균형잡힌 결론을 도출합니다.

        Returns:
            str: Multi-Perspective 프레임워크
        """
        return """
**👥 Multi-Perspective 다각도 분석 프레임워크**

동일한 데이터를 다음 관점들에서 분석하세요:

```
다각도 관점에서 분석:
1. 투자자 관점: 수익률과 리스크 측면에서 어떤 의미인가?
2. 경영진 관점: 기업 운영과 전략 관점에서 어떤 시사점인가?
3. 경쟁사 관점: 경쟁사 대비 상대적 우위/열위는 무엇인가?
4. 업계 관점: 섹터 전체 트렌드와 어떻게 연결되는가?
5. 거시경제 관점: 경제 사이클과 정책 변화에 어떤 영향을 받는가?
```

**Multi-Perspective 적용 예시:**
```
ROE 15% 증가 분석:
1. 투자자: 자본 효율성 개선으로 매력적 투자 기회
2. 경영진: 수익성 개선 전략의 성과, 지속가능성 검토 필요
3. 경쟁사: 업계 평균 12% 대비 우위, 경쟁사 대응 전략 예상
4. 업계: 섹터 전체 회복세의 선도 지표 가능성
5. 거시경제: 금리 인상기에도 견고한 수익성 유지 능력 입증
```
"""

    @staticmethod
    def get_reasoning_validation_framework() -> str:
        """
        Reasoning 추론 검증 프레임워크를 반환합니다.

        분석 과정에서 논리적 오류를 방지하고
        추론의 타당성을 검증하는 체계입니다.

        Returns:
            str: 추론 검증 프레임워크
        """
        return """
**🔍 Reasoning 추론 검증 프레임워크**

모든 추론 과정에서 다음을 검증하세요:

```
추론 타당성 검증:
1. 논리적 연결: 전제와 결론 사이의 논리적 연결이 타당한가?
2. 인과관계: 상관관계를 인과관계로 잘못 해석하지 않았나?
3. 표본 크기: 결론을 내리기에 충분한 데이터가 있는가?
4. 시간적 일관성: 과거 패턴이 미래에도 유효할 것인가?
5. 맥락 고려: 특수한 상황이나 예외적 요인을 고려했는가?
```

**Reasoning 검증 적용 예시:**
```
"3개월 연속 상승 → 계속 상승할 것" 추론 검증:
1. 논리적 연결: 과거 상승이 미래 상승을 보장하는가? (× 논리적 오류)
2. 인과관계: 단순 시계열 패턴을 인과관계로 해석 (× 잘못된 추론)
3. 표본 크기: 3개월 데이터만으로 트렌드 판단 가능한가? (× 부족)
4. 시간적 일관성: 시장 환경 변화를 고려했는가? (× 미고려)
5. 맥락 고려: 특별한 호재나 계절성 요인이 있었나? (✓ 검토 필요)
```
"""

    @staticmethod
    def get_confidence_scoring_framework() -> str:
        """
        Confidence Scoring 신뢰도 평가 프레임워크를 반환합니다.

        분석 결과에 대한 신뢰도를 정량적으로 평가하여
        투자 의사결정의 확실성을 제공합니다.

        Returns:
            str: 신뢰도 평가 프레임워크
        """
        return """
**📊 Confidence Scoring 신뢰도 평가 프레임워크**

모든 분석 결과에 신뢰도 점수(1-10점)를 부여하세요:

```
신뢰도 평가 기준:
1. 데이터 품질 (1-10점): 데이터의 정확성과 완전성
2. 분석 방법론 (1-10점): 사용한 분석 기법의 적절성
3. 시장 환경 (1-10점): 현재 시장 상황의 예측 가능성
4. 과거 적중률 (1-10점): 유사한 분석의 과거 성과
5. 외부 변수 (1-10점): 통제 불가능한 요인의 영향도

종합 신뢰도 = (각 항목 점수의 가중평균)
```

**신뢰도 점수 해석:**
- 9-10점: 매우 높은 신뢰도, 확신을 가지고 투자 결정 가능
- 7-8점: 높은 신뢰도, 일반적인 투자 결정에 활용 가능
- 5-6점: 보통 신뢰도, 추가 분석이나 검증 필요
- 3-4점: 낮은 신뢰도, 신중한 접근 필요
- 1-2점: 매우 낮은 신뢰도, 투자 결정 보류 권장

**Confidence Scoring 적용 예시:**
```
"목표가 50,000원" 분석의 신뢰도:
1. 데이터 품질: 8점 (DART 공식 재무제표 사용)
2. 분석 방법론: 7점 (DCF + 멀티플 병행 분석)
3. 시장 환경: 6점 (변동성 높은 시장 상황)
4. 과거 적중률: 7점 (유사 분석의 75% 적중률)
5. 외부 변수: 5점 (정책 변화 불확실성)

종합 신뢰도: 6.6점 (보통 신뢰도, 추가 모니터링 필요)
```
"""

    @staticmethod
    def get_web_search_integration_guide() -> str:
        """
        웹 검색 통합 가이드를 반환합니다.

        웹 검색 도구를 효과적으로 활용하여
        최신 정보를 분석에 반영하는 방법을 제공합니다.

        Returns:
            str: 웹 검색 통합 가이드
        """
        return """
**🔍 웹 검색 통합 활용 가이드**

분석 품질 향상을 위한 웹 검색 활용 방법:

```
웹 검색 활용 전략:
1. 최신 업계 동향: "섹터명 + 2024 + 전망" 검색
2. 경쟁사 비교: "경쟁사명 + 실적 + 최신" 검색
3. 정책 변화: "업계 + 정책 + 규제 + 변화" 검색
4. 글로벌 트렌드: "글로벌 + 섹터명 + 동향" 검색
5. 리스크 요인: "업계 + 리스크 + 이슈" 검색
```

**검색 결과 활용 원칙:**
- 출처 신뢰성: 공식 기관, 주요 언론, 증권사 리포트 우선
- 시점 확인: 최신 정보인지 날짜 확인 필수
- 교차 검증: 복수 출처에서 동일한 내용 확인
- 정량적 활용: 구체적 수치나 팩트 위주로 활용
- 출처 명시: [검색 출처: URL] 형태로 반드시 표기

**웹 검색 통합 예시:**
```
삼성전자 분석 시:
1. "반도체 2024 전망" → 메모리 회복 전망 확인
2. "삼성전자 경쟁사 실적" → TSMC, SK하이닉스 비교
3. "반도체 정책 변화" → 미중 반도체 정책 영향 분석
4. "글로벌 반도체 동향" → AI 반도체 수요 증가 확인
5. "반도체 리스크 요인" → 지정학적 리스크 점검

[검색 출처: 한국반도체산업협회, 2024.01.15]
```
"""

    @staticmethod
    def get_senior_report_synthesis_framework() -> str:
        """
        시니어 애널리스트 리포트를 위한 전문가 의견 종합 프레임워크를 반환합니다.

        여러 전문가의 분석을 통합하여 실제 투자은행/증권사 수준의
        전문적인 리포트로 변환하는 체계입니다.

        Returns:
            str: 시니어 리포트 종합 프레임워크
        """
        return """
**📊 시니어 애널리스트 리포트 종합 프레임워크**

다중 전문가 분석을 증권사 수준의 전문 리포트로 통합하는 프로세스:

```
리포트 종합 단계:
1. 전문가 의견 정합성 검증: 상충되는 의견의 논리적 조율
2. 핵심 투자 테마 도출: 모든 분석에서 공통된 강점/약점 추출
3. 시간별 투자 전략 통합: 단기/중기/장기 시계열 일관성 확보
4. 리스크-수익률 매트릭스: 정량적 위험 대비 수익률 평가
5. 최종 투자 판단 근거: 데이터 기반 명확한 의사결정 논리
```

**전문가 의견 가중치 시스템:**
```
신뢰도 기반 의견 통합:
- 정량 분석 (재무, 밸류에이션): 높은 가중치 (40%)
- 시장 분석 (기술적, 산업): 중간 가중치 (35%)
- 정성 평가 (리스크, ESG): 참고 가중치 (25%)

의견 불일치 해결 원칙:
- 단기 vs 장기 갈등: 투자 기간별 분리 권고
- 정량 vs 정성 갈등: 정량 분석 우선, 정성적 리스크 보완
- 전문가 간 갈등: 데이터 품질과 논리적 일관성 기준 판단
```

**투자은행 스타일 리포트 구조:**
```
1. EXECUTIVE SUMMARY (1페이지)
   - 투자 의견: BUY/HOLD/SELL + 신뢰도 점수
   - 목표가: 12개월 기준 + 상승/하락 여력
   - 핵심 논리: 3줄 요약 + 주요 리스크 1줄

2. INVESTMENT HIGHLIGHTS (1페이지)
   - 매수/중립/매도 핵심 근거 3가지
   - 전문가 합의 사항과 이견 사항 구분
   - 카탈리스트와 리스크 요인 균형 제시

3. FINANCIAL ANALYSIS (2페이지)
   - 재무 건전성: ROE, ROIC, 부채비율 트렌드
   - 성장성 분석: 매출/이익 성장률과 지속가능성
   - 수익성 분석: 마진 분석과 경쟁사 비교

4. VALUATION ANALYSIS (1페이지)
   - DCF 모델링: WACC 계산과 FCF 예측
   - 멀티플 분석: PER, PBR, EV/EBITDA
   - 목표가 산출: 가중평균과 시나리오별 분석

5. TECHNICAL & MARKET ANALYSIS (1페이지)
   - 차트 패턴과 기술적 지표 종합
   - 섹터 로테이션과 상대강도 분석
   - 매수/매도 타이밍과 지지/저항선

6. RISK ASSESSMENT (1페이지)
   - 주요 리스크 요인별 발생 확률과 영향도
   - 시나리오별 손실 가능성과 대응 전략
   - ESG와 지배구조 리스크 평가

7. RECOMMENDATION & STRATEGY (1페이지)
   - 12개월 투자 의견과 목표가
   - 투자 기간별 전략 (단기/중기/장기)
   - 포트폴리오 내 위치와 비중 권고
```
"""

    @staticmethod
    def get_investment_decision_matrix_template() -> str:
        """
        투자 의사결정 매트릭스 템플릿을 반환합니다.

        정량적 데이터를 기반으로 체계적인 투자 판단을
        내릴 수 있도록 도와주는 프레임워크입니다.

        Returns:
            str: 투자 의사결정 매트릭스
        """
        return """
**🎯 투자 의사결정 매트릭스**

체계적인 투자 판단을 위한 정량적 평가 시스템:

```
투자 매력도 스코어링 (총 100점):

1. 재무 건전성 (25점)
   - ROE 트렌드 (10점): 3년 평균 vs 업계 평균
   - 부채비율 (8점): 안전성과 레버리지 효율성
   - FCF 안정성 (7점): 현금 창출 능력과 일관성

2. 성장성 (25점)
   - 매출 성장률 (10점): 3년 CAGR vs 업계 성장률
   - 이익 성장률 (10점): 영업이익 성장 지속가능성
   - 시장 확장성 (5점): TAM 확대와 시장 점유율

3. 밸류에이션 (25점)
   - 절대가치 (15점): DCF 대비 현재가 할인/프리미엄
   - 상대가치 (10점): 동종업계 멀티플 대비 매력도

4. 기술적 분석 (15점)
   - 추세 강도 (8점): 이동평균선 배열과 모멘텀
   - 매매 신호 (7점): RSI, MACD 등 복합 지표

5. 리스크 평가 (10점)
   - 변동성 (5점): 역사적 변동성과 베타
   - 섹터 리스크 (5점): 산업 고유 위험도
```

**투자 의견 결정 기준:**
```
- 85-100점: 강력매수 (Strong Buy)
- 70-84점: 매수 (Buy)
- 55-69점: 보유 (Hold)
- 40-54점: 매도 (Sell)
- 0-39점: 강력매도 (Strong Sell)

신뢰도 조정:
- 데이터 품질 A급: 점수 그대로 적용
- 데이터 품질 B급: 점수 × 0.9
- 데이터 품질 C급: 점수 × 0.8
```

**시나리오별 목표가 산출:**
```
확률 가중 목표가 = (Bull Case × 25%) + (Base Case × 50%) + (Bear Case × 25%)

Bull Case: 최상 시나리오 (모든 긍정 요인 실현)
Base Case: 기본 시나리오 (현 추세 지속)
Bear Case: 최악 시나리오 (주요 리스크 현실화)

각 시나리오별 발생 근거와 확률 산정 논리 명시 필수
```
"""

    @staticmethod
    def create_senior_report_template(
        stock_name: str, sector_name: str, expert_insights: Dict[str, Any] = None
    ) -> str:
        """
        시니어 애널리스트 리포트 템플릿을 생성합니다.

        Args:
            stock_name: 종목명
            sector_name: 섹터명
            expert_insights: 전문가 분석 결과

        Returns:
            str: 맞춤형 시니어 리포트 템플릿
        """
        if expert_insights is None:
            expert_insights = {}

        template = f"""
**🏦 시니어 애널리스트 리포트: {stock_name}**

{PromptComponents.get_senior_report_synthesis_framework()}

{PromptComponents.get_investment_decision_matrix_template()}

**📊 {stock_name} 맞춤형 분석 프레임워크**

**분석 대상**: {stock_name} ({sector_name} 섹터)
**리포트 타입**: 종합 투자 분석 리포트
**분석 기준일**: {{현재 날짜}}
**목표 기간**: 12개월

**전문가 분석 통합 지침:**

1. **의견 수렴 과정**
   - 각 전문가 의견의 핵심 포인트 추출
   - 일치 영역과 이견 영역 명확히 구분
   - 이견에 대한 논리적 조율과 우선순위 설정

2. **증거 기반 결론**
   - 모든 주장에 대한 정량적 근거 제시
   - 가정 사용 시 명확한 표시와 합리성 검증
   - 불확실성 요소에 대한 시나리오 분석

3. **실용적 투자 전략**
   - 구체적인 매수/매도 시점과 조건
   - 포트폴리오 내 적정 비중과 리밸런싱
   - 모니터링 지표와 의견 변경 조건

**🎯 최종 출력 요구사항:**

```
=== EXECUTIVE SUMMARY ===
• 투자의견: [BUY/HOLD/SELL] (신뢰도: X%)
• 목표가: XXX,XXX원 (상승여력: +X%)
• 핵심논리: [3줄 요약]
• 주요리스크: [1줄 요약]

=== INVESTMENT HIGHLIGHTS ===
• 매수근거 (또는 중립/매도 근거) 3가지
• 전문가 합의사항 vs 이견사항
• 주요 카탈리스트와 리스크 균형

=== QUANTITATIVE ANALYSIS ===
• 투자매력도 점수: XX/100점 (평가 근거)
• 재무건전성: XX점, 성장성: XX점, 밸류에이션: XX점
• 기술적분석: XX점, 리스크평가: XX점

=== TARGET PRICE CALCULATION ===
• DCF 목표가: XXX,XXX원 (가중치: X%)
• 멀티플 목표가: XXX,XXX원 (가중치: X%)
• 가중평균 목표가: XXX,XXX원
• 시나리오별: Bull XXX,XXX원 | Base XXX,XXX원 | Bear XXX,XXX원

=== INVESTMENT STRATEGY ===
• 단기전략 (1-3개월): [구체적 전략]
• 중기전략 (3-12개월): [구체적 전략]
• 리스크관리: [구체적 방안]
• 매수타이밍: [구체적 조건]
```

**⚠️ 품질 기준:**
- 모든 수치는 소수점 표기와 단위 명시
- 모든 주장은 데이터 기반 근거 제시
- 투자 의견은 BUY/HOLD/SELL 명확히 표기
- 목표가는 구체적 금액과 상승여력 % 병기
- 전문가 의견 차이는 투명하게 공개하고 조율 논리 설명
"""

        return template

    @staticmethod
    def create_unified_analysis_framework(
        analysis_type: str, sector_name: str, specific_methods: List[str] = None
    ) -> str:
        """
        통합 분석 프레임워크를 생성합니다.

        분석 타입에 따라 적절한 AI 강화 기법들을 조합하여
        일관된 분석 프레임워크를 제공합니다.

        Args:
            analysis_type: 분석 타입 ('financial', 'technical', 'risk' 등)
            sector_name: 섹터 이름
            specific_methods: 특화된 분석 방법들

        Returns:
            str: 통합 분석 프레임워크
        """
        if specific_methods is None:
            specific_methods = []

        framework = f"""
**🚀 {sector_name} 섹터 {analysis_type} 분석 AI 강화 프레임워크**

{PromptComponents.get_cot_framework()}

{PromptComponents.get_self_critique_template()}

{PromptComponents.get_multi_perspective_framework()}

{PromptComponents.get_reasoning_validation_framework()}

{PromptComponents.get_confidence_scoring_framework()}

{PromptComponents.get_web_search_integration_guide()}

**🎯 {analysis_type} 분석 특화 방법론:**
"""

        for i, method in enumerate(specific_methods, 1):
            framework += f"\n{i}. {method}"

        framework += """

**📋 분석 품질 체크리스트:**
- [ ] Chain of Thought 적용: 모든 분석에 3단계 추론 과정 포함
- [ ] Self-Critique 수행: 분석 결과에 대한 자기 비판 완료
- [ ] Multi-Perspective 검토: 최소 3가지 관점에서 분석 수행
- [ ] Reasoning 검증: 논리적 오류 및 편향 검토 완료
- [ ] Confidence Score 부여: 모든 결론에 신뢰도 점수 제시
- [ ] 웹 검색 활용: 최신 정보 반영 및 출처 명시 완료

**🎯 최종 출력 품질 기준:**
- 모든 수치: 소수점 둘째 자리까지 + 신뢰도 점수 병기
- 계산 과정: 단계별 명시 + CoT 추론 과정 포함
- 비교 분석: 구체적 수치 + 통계적 근거 제시
- 최종 결론: 정량적 근거 + 신뢰구간 + Self-Critique 결과 포함
"""

        return framework

    @staticmethod
    def get_output_format_template(analysis_type: str) -> str:
        """
        분석 타입별 출력 형식 템플릿을 반환합니다.

        Args:
            analysis_type: 분석 타입

        Returns:
            str: 출력 형식 템플릿
        """
        return f"""
**📊 {analysis_type} 분석 결과 출력 형식**

**1. 핵심 요약 (Executive Summary)**
- 주요 발견사항 3가지 (정량적 근거 포함)
- 투자 의견 및 신뢰도 점수
- 핵심 리스크 요인

**2. 상세 분석 결과**
- 각 지표별 CoT 추론 과정
- Multi-Perspective 분석 결과
- 웹 검색 기반 최신 정보 반영

**3. Self-Critique 결과**
- 분석의 한계점 및 편향 가능성
- 반대 의견 및 대안적 해석
- 추가 검토 필요 사항

**4. 신뢰도 평가**
- 각 분석 요소별 신뢰도 점수 (1-10점)
- 종합 신뢰도 및 해석
- 불확실성 요인 및 민감도 분석

**5. 투자 시사점**
- 구체적 투자 액션 아이템
- 모니터링 포인트
- 재검토 시점 및 조건

**6. 참고 자료**
- 웹 검색 출처 목록
- 사용된 데이터 및 가정
- 분석 방법론 상세 설명
"""

    @staticmethod
    def _generate_sector_specific_questions(
        sector: GICSSector, sector_manager: GICSSectorManager
    ) -> str:
        """
        특정 섹터에 맞춤화된 동적 질문들을 생성합니다.
        기존 4개 기본 질문 + 섹터별 특화 질문 5개 확장 방식입니다.

        Args:
            sector: GICS 섹터
            sector_manager: 섹터 매니저 인스턴스

        Returns:
            str: 기본 질문 + 섹터별 맞춤 질문들
        """
        sector_name = sector_manager.get_sector_korean_name(sector)

        # 🔥 기본 질문 4개 (모든 섹터 공통)
        base_questions = f"""
📝 내가 답해야 할 핵심 질문들 ({sector_name} 섹터 맞춤형):

Q1: 이 기업의 재무적 건전성은 어떤가?
  └─ Q1-1: ROE, ROA, ROIC는 업계 대비 어떤 수준인가?
  └─ Q1-2: 부채비율과 유동성은 안전한 수준인가?
  └─ Q1-3: 현금흐름의 질과 안정성은 어떤가?

Q2: 이 기업의 성장성과 수익성 전망은 어떤가?
  └─ Q2-1: 과거 3년간 매출과 이익 성장 추세는?
  └─ Q2-2: 주요 성장 동력과 수익원은 무엇인가?
  └─ Q2-3: 향후 성장 지속가능성은 어떤가?

Q3: 이 기업의 적정 가치는 얼마인가?
  └─ Q3-1: DCF 기반 내재가치는 얼마인가?
  └─ Q3-2: 멀티플 기반 상대가치는 얼마인가?
  └─ Q3-3: 현재 주가는 고평가/적정/저평가 상태인가?

Q4: 주요 리스크와 기회 요인은 무엇인가?
  └─ Q4-1: 재무적/운영적 리스크는 무엇인가?
  └─ Q4-2: 산업 환경과 경쟁 구도 변화는?
  └─ Q4-3: 규제나 외부 환경 리스크는?
"""

        # 🚀 섹터별 특화 질문 Q5 추가
        sector_questions = ""

        if sector == GICSSector.INFORMATION_TECHNOLOGY:
            sector_questions = """
Q5: 🖥️ IT 섹터 특화 분석 질문들:
  └─ Q5-1: 기술 경쟁력과 플랫폼 점유율은 어떤가?
  └─ Q5-2: R&D 투자 대비 수익화 성공률은?
  └─ Q5-3: 클라우드/AI 전환 역량은 어떤 수준인가?
  └─ Q5-4: 반도체 사이클/기술 디스럽션 리스크는?
  └─ Q5-5: 고객 락인 효과와 스위칭 코스트는?"""

        elif sector == GICSSector.FINANCIALS:
            sector_questions = """
Q5: 🏦 금융 섹터 특화 분석 질문들:
  └─ Q5-1: 순이자마진(NIM)과 비이자수익 구조는?
  └─ Q5-2: 자산건전성과 대손충당금 적정성은?
  └─ Q5-3: BIS 비율과 자본 적정성은?
  └─ Q5-4: 금리 변화에 따른 민감도는?
  └─ Q5-5: 핀테크/디지털 전환 대응력은?"""

        elif sector == GICSSector.HEALTH_CARE:
            sector_questions = """
Q5: 💊 헬스케어 섹터 특화 분석 질문들:
  └─ Q5-1: 신약 파이프라인과 개발 단계는?
  └─ Q5-2: 특허 만료 일정과 제네릭 위협은?
  └─ Q5-3: FDA 승인 및 임상시험 성공률은?
  └─ Q5-4: R&D 투자 효율성과 바이오 플랫폼은?
  └─ Q5-5: 보험 수가와 정부 규제 리스크는?"""

        elif sector == GICSSector.ENERGY:
            sector_questions = """
Q5: ⚡ 에너지 섹터 특화 분석 질문들:
  └─ Q5-1: 유가/가스 가격 민감도와 생산단가는?
  └─ Q5-2: 자원 매장량과 생산 수명은?
  └─ Q5-3: 탄소배출과 ESG/친환경 전환은?
  └─ Q5-4: Capex 투자와 신재생 에너지 전략은?
  └─ Q5-5: 에너지 정책 변화와 구조적 리스크는?"""

        elif sector == GICSSector.CONSUMER_DISCRETIONARY:
            sector_questions = """
Q5: 🛒 임의소비재 섹터 특화 분석 질문들:
  └─ Q5-1: 브랜드력과 시장점유율 추이는?
  └─ Q5-2: 동일매장 매출성장률과 고객 충성도는?
  └─ Q5-3: e-Commerce 대응과 디지털 전환은?
  └─ Q5-4: 원가 상승 시 가격전가 능력은?
  └─ Q5-5: 소비 트렌드 변화와 적응력은?"""

        elif sector == GICSSector.MATERIALS:
            sector_questions = """
Q5: 🏭 소재 섹터 특화 분석 질문들:
  └─ Q5-1: 원자재 가격과 제품 가격 스프레드는?
  └─ Q5-2: 경기 사이클과 중국 경기 연동성은?
  └─ Q5-3: 생산설비 효율성과 원가구조는?
  └─ Q5-4: 환경 규제와 재활용/친환경 투자는?
  └─ Q5-5: 재고자산 변동성과 가격 헤지는?"""

        elif sector == GICSSector.INDUSTRIALS:
            sector_questions = """
Q5: 🏗️ 산업재 섹터 특화 분석 질문들:
  └─ Q5-1: 수주잔고(Backlog)와 매출 가시성은?
  └─ Q5-2: 고객 다변화와 집중도 리스크는?
  └─ Q5-3: 운영 레버리지와 자유현금흐름은?
  └─ Q5-4: 글로벌 공급망 의존도와 리스크는?
  └─ Q5-5: 자동화/디지털화 투자 현황은?"""

        elif sector == GICSSector.COMMUNICATION_SERVICES:
            sector_questions = """
Q5: 📡 커뮤니케이션서비스 섹터 특화 분석 질문들:
  └─ Q5-1: 구독자 수와 ARPU 변화 추이는?
  └─ Q5-2: 콘텐츠 경쟁력과 스트리밍 점유율은?
  └─ Q5-3: 5G 인프라 투자와 수익화는?
  └─ Q5-4: OTT/미디어 경쟁과 차별화 전략은?
  └─ Q5-5: 광고 매출과 디지털 전환 효과는?"""

        elif sector == GICSSector.UTILITIES:
            sector_questions = """
Q5: 🔌 유틸리티 섹터 특화 분석 질문들:
  └─ Q5-1: 요금제 구조와 규제 기관 정책은?
  └─ Q5-2: 신재생 에너지 비율과 전환 계획은?
  └─ Q5-3: 배당 지속성과 현금흐름 안정성은?
  └─ Q5-4: 금리 민감도와 채권 대체성은?
  └─ Q5-5: ESG 투자와 친환경 전환 비용은?"""

        elif sector == GICSSector.REAL_ESTATE:
            sector_questions = """
Q5: 🏢 부동산 섹터 특화 분석 질문들:
  └─ Q5-1: 보유 부동산 NAV와 시장가치는?
  └─ Q5-2: 임대료 상승률과 공실률 추이는?
  └─ Q5-3: LTV와 이자비용 부담 수준은?
  └─ Q5-4: 오피스/리테일/물류 포트폴리오 구성은?
  └─ Q5-5: 부동산 시장 사이클과 금리 민감도는?"""

        elif sector == GICSSector.CONSUMER_STAPLES:
            sector_questions = """
Q5: 🍞 필수소비재 섹터 특화 분석 질문들:
  └─ Q5-1: 안정적 수요 기반과 마진 방어력은?
  └─ Q5-2: 브랜드 충성도와 유통망 강도는?
  └─ Q5-3: 인플레이션 헤지와 가격전가 능력은?
  └─ Q5-4: 건강/웰빙 트렌드 대응력은?
  └─ Q5-5: 배당 지속성과 방어적 특성은?"""
        else:
            # 기타 섹터는 일반적인 추가 질문 제공
            sector_questions = """
Q5: 🎯 업계 특화 분석 질문들:
  └─ Q5-1: 업계 내 경쟁 우위와 차별화 요소는?
  └─ Q5-2: 시장 점유율과 고객 기반 강화 전략은?
  └─ Q5-3: 운영 효율성과 비용 관리 역량은?
  └─ Q5-4: 혁신 역량과 신사업 발굴 현황은?
  └─ Q5-5: ESG 경영과 지속가능성 전략은?"""

        return base_questions + sector_questions

    @staticmethod
    def _get_sector_analysis_guidance(
        sector: GICSSector, sector_manager: GICSSectorManager
    ) -> str:
        """
        섹터별 분석 가이던스를 제공합니다.

        Args:
            sector: GICS 섹터
            sector_manager: 섹터 매니저 인스턴스

        Returns:
            str: 섹터별 분석 가이던스
        """
        context = sector_manager.get_sector_context(sector)
        sector_name = sector_manager.get_sector_korean_name(sector)

        return f"""
🎯 {sector_name} 섹터 특화 분석 가이던스:

📋 주요 업종: {context.get('industry_focus', '정보 없음')}

🔍 중점 분석 포인트:
{context.get('key_analysis_points', '정보 없음')}

⚠️ 주의할 위험 요소:
{context.get('key_risks', '정보 없음')}

💰 권장 밸류에이션 방법:
{context.get('valuation_approach', '정보 없음')}

📊 경기 민감성:
{context.get('cyclical_nature', '정보 없음')}

📈 핵심 체크 지표:
{context.get('critical_metrics', '정보 없음')}
"""

    @staticmethod
    def _get_default_questions() -> str:
        """
        섹터 정보가 없을 때 사용할 기본 질문들을 반환합니다.

        Returns:
            str: 기본 4개 질문들
        """
        return """
📝 내가 답해야 할 핵심 질문들:

Q1: 이 기업의 재무적 건전성은 어떤가?
  └─ Q1-1: ROE, ROA, ROIC는 업계 대비 어떤 수준인가?
  └─ Q1-2: 부채비율과 유동성은 안전한 수준인가?
  └─ Q1-3: 현금흐름의 질과 안정성은 어떤가?

Q2: 이 기업의 성장성과 수익성 전망은 어떤가?
  └─ Q2-1: 과거 3년간 매출과 이익 성장 추세는?
  └─ Q2-2: 주요 성장 동력과 수익원은 무엇인가?
  └─ Q2-3: 향후 성장 지속가능성은 어떤가?

Q3: 이 기업의 적정 가치는 얼마인가?
  └─ Q3-1: DCF 기반 내재가치는 얼마인가?
  └─ Q3-2: 멀티플 기반 상대가치는 얼마인가?
  └─ Q3-3: 현재 주가는 고평가/적정/저평가 상태인가?

Q4: 주요 리스크와 기회 요인은 무엇인가?
  └─ Q4-1: 재무적/운영적 리스크는 무엇인가?
  └─ Q4-2: 산업 환경과 경쟁 구도 변화는?
  └─ Q4-3: 규제나 외부 환경 리스크는?
"""
