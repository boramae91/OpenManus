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
- Enhanced Analyst Thinking Flow 애널리스트 사고 흐름
- Dynamic Question Generation 동적 질문 생성
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

=== 1단계: Self-Ask with ToT (섹터별 맞춤 질문 구성 및 사고 분기) ===

🌳 Tree of Thoughts 기법으로 핵심 질문들을 체계적으로 구성하세요:

{dynamic_questions}

{sector_specific_info}

🎯 모든 질문에 대해 완전한 답변 제공:
- Q1-Q5의 모든 세부 질문들을 빠짐없이 분석하세요
- 각 질문별로 구체적이고 상세한 답변을 제공하세요
- 우선순위 없이 모든 질문을 동등하게 중요하게 다뤄주세요

=== 2단계: ReAct (Reason + Action) - 검색 및 정보 수집 ===

🔍 각 질문에 대한 체계적 정보 수집과 추론 수행:

**Reason (추론)**: 왜 이 정보가 필요한가?
**Action (행동)**: 어떤 정보를 어떻게 수집할 것인가?

📊 **모든 데이터 종합 활용** (우선순위 없이 모든 데이터 완전 분석):
✅ **재무데이터**: yfinance 데이터, 기본 재무지표 완전 분석
✅ **DART 데이터**: 재무제표, 사업보고서, 공시자료 상세 분석
✅ **사업보고서 딕셔너리**: PDF 상세 정보, 경영진 메시지 심층 분석
✅ **웹 검색 보완**: 업계 동향, 경쟁사 비교 추가 분석

**Observation (관찰)**: 수집된 정보의 의미는?
- 핵심 발견사항, 예상과의 차이, 추가 조사 필요성

💡 ReAct 사이클을 각 핵심 질문별로 반복 수행하세요.

=== 3단계: Enhanced CoT Reasoning + Multi-Layer Self-Critique ===

🧠 **각 분석 블록별 독립 검증 후 통합 방식으로 수행하세요:**

**🔵 1️⃣ 재무 건전성 분석 + 즉시 검증**
```
분석 과정:
- 근거 1: [구체적 재무지표와 해석]
- 근거 2: [경쟁사 대비 상대적 위치]
- 근거 3: [시계열 트렌드 분석]

🔍 즉시 Self-Critique:
❓ 이 재무 분석이 타당한가?
  - 사용한 지표들이 업계 특성을 반영하는가?
  - 경쟁사 비교가 공정한가? (규모, 사업구조 유사성)
  - 시계열 데이터에 일회성 요인이 포함되어 있지는 않은가?

🔧 수정된 결론: [Self-Critique 반영한 최종 재무 건전성 평가]
```

**🟢 2️⃣ 성장성 및 수익성 분석 + 즉시 검증**
```
분석 과정:
- 근거 1: [과거 성장 실적과 품질 분석]
- 근거 2: [미래 성장 동력과 지속가능성]
- 근거 3: [수익성 개선 가능성]

🔍 즉시 Self-Critique:
❓ 이 성장성 분석이 현실적인가?
  - 과거 성장률이 특수한 환경 요인에 의존하지 않았나?
  - 성장 동력이 구체적이고 실현 가능한가?
  - 경쟁 심화나 시장 포화 가능성을 충분히 고려했는가?

🔧 수정된 결론: [Self-Critique 반영한 최종 성장성 평가]
```

**🟡 3️⃣ 밸류에이션 분석 + 즉시 검증**
```
분석 과정:
- DCF 분석: [내재가치 산출 과정과 결과]
- 멀티플 분석: [상대가치 평가]
- 종합 판단: [적정가치와 투자 의견]

🔍 즉시 Self-Critique:
❓ 이 밸류에이션이 합리적인가?
  - DCF 가정(성장률, 할인율)이 보수적인가?
  - 멀티플 비교 대상이 적절한가?
  - 시장 상황(금리, 리스크 프리미엄)을 충분히 반영했는가?

🔧 수정된 결론: [Self-Critique 반영한 최종 밸류에이션]
```

**🔴 4️⃣ 리스크 분석 + 즉시 검증**
```
분석 과정:
- 주요 리스크: [발생 가능성과 영향도]
- 기대 수익률: [시나리오별 수익률]
- 리스크 조정 수익률: [샤프 비율 관점]

🔍 즉시 Self-Critique:
❓ 이 리스크 평가가 포괄적인가?
  - 숨겨진 리스크나 테일 리스크를 놓치지 않았나?
  - 리스크 발생 확률이 과소평가되지 않았나?
  - 상관관계가 높은 리스크들을 중복 계산하지 않았나?

🔧 수정된 결론: [Self-Critique 반영한 최종 리스크 평가]
```

**🟣 5️⃣ 섹터 특화 경쟁력 분석 + 즉시 검증**
```
분석 과정:
- Q5-1 분석: [기술/시장 경쟁력 평가와 근거]
- Q5-2 분석: [핵심 성장 동력 평가와 근거]
- Q5-3 분석: [운영/전략적 우위 평가와 근거]
- Q5-4 분석: [섹터 리스크 평가와 근거]
- Q5-5 분석: [지속가능성 평가와 근거]

🔍 즉시 Self-Critique:
❓ 이 섹터 분석이 차별화되어 있는가?
  - 일반적인 분석과 구별되는 섹터 특화 관점이 있는가?
  - 섹터 내 경쟁사 대비 우위가 명확히 드러나는가?
  - 섹터 트렌드와 기업의 대응 전략이 일치하는가?

🔧 수정된 결론: [Self-Critique 반영한 최종 섹터 경쟁력 평가]
```

**🔥 6️⃣ 통합 종합 분석 (Multi-Layer Integration)**
```
위 5개 블록의 수정된 결론들을 종합하여:

📊 일관성 검증:
- 재무 건전성과 성장성 평가가 모순되지 않는가?
- 밸류에이션과 리스크 평가가 균형을 이루는가?
- 섹터 분석이 전체 투자 논리를 강화하는가?

🎯 최종 통합 결론:
- 투자 의견: [BUY/HOLD/SELL + 신뢰도 %]
- 목표가: [통합 분석 기반 목표가]
- 핵심 논리: [5개 블록 분석이 뒷받침하는 투자 논리]
- 섹터 경쟁력: [Q5 분석 기반 차별화 요소]
- 리스크 관리: [주요 위험 요소와 대응 방안]
```

=== 4단계: Chain of Verification (CoVe) - 결론 검증 ===

🔍 **각 핵심 결론에 대한 3단계 역추적 검증을 수행하세요:**

**🎯 투자 의견 검증**
```
결론: [투자 의견 - BUY/HOLD/SELL]

🔍 Verification Process:
1️⃣ 출처의 신뢰성 검증:
   - 이 결론의 근거가 된 데이터 출처는? **[재무데이터/DART/웹검색 명시]**
   - 각 출처의 신뢰도는? (공식 재무제표 > 사업보고서 > 언론보도 순)
   - 상충하는 정보나 오래된 정보는 없는가?

2️⃣ 수치 기반 타당성 검증:
   - 사용된 수치들이 정확하고 최신인가?
   - 계산 과정에 오류는 없는가? (DCF, 멀티플, 비율 계산 등)
   - 가정들이 현실적이고 보수적인가?

3️⃣ 상대 비교의 논리적 적절성:
   - 경쟁사/업계 평균과의 비교가 공정한가?
   - 시장 상황과 기업 상황이 적절히 반영되었는가?
   - 과거 유사 사례와 비교했을 때 합리적인가?

✅ 검증 결과: [투자 의견이 검증 과정을 통과하는지 판단]
```

**💰 목표가 검증**
```
결론: [목표가 - 구체적 금액]

🔍 Verification Process:
1️⃣ 출처의 신뢰성 검증:
   - DCF 가정의 근거가 된 데이터 출처는?
   - 멀티플 비교 대상의 선정 기준은 적절한가?
   - 외부 전문가 의견과의 괴리는 어느 정도인가?

2️⃣ 수치 기반 타당성 검증:
   - DCF 할인율이 현재 금리 환경을 반영하는가?
   - 성장률 가정이 과거 실적과 일치하는가?
   - 터미널 밸류 가정이 합리적인가?

3️⃣ 상대 비교의 논리적 적절성:
   - 동종업계 평균 밸류에이션과 비교했을 때 합리적인가?
   - 글로벌 유사 기업과 비교했을 때 적절한가?
   - 시장 사이클을 고려했을 때 현실적인가?

✅ 검증 결과: [목표가가 검증 과정을 통과하는지 판단]
```

**🏆 섹터 경쟁력 검증**
```
결론: [섹터 내 경쟁력 평가]

🔍 Verification Process:
1️⃣ 출처의 신뢰성 검증:
   - 경쟁력 평가의 근거가 된 정보 출처는?
   - 시장 점유율, 기술력 데이터가 최신이고 정확한가?
   - 제3자 평가 기관의 객관적 자료가 있는가?

2️⃣ 수치 기반 타당성 검증:
   - 정량 지표(시장점유율, R&D 비율 등)가 정확한가?
   - 비교 기준이 일관되고 공정한가?
   - 트렌드 분석이 충분한 기간을 반영하는가?

3️⃣ 상대 비교의 논리적 적절성:
   - 주요 경쟁사와의 비교가 균형잡혀 있는가?
   - 글로벌 기준으로도 경쟁력이 인정되는가?
   - 미래 트렌드를 고려했을 때도 지속가능한가?

✅ 검증 결과: [섹터 경쟁력 평가가 검증 과정을 통과하는지 판단]
```

**⚠️ 최종 검증 종합**
```
🎯 전체 분석의 신뢰도 점수: [0-100점]
- 출처 신뢰성: [점수]/25점
- 수치 타당성: [점수]/25점
- 비교 적절성: [점수]/25점
- 논리 일관성: [점수]/25점

🔧 검증에서 발견된 취약점:
- [취약점 1과 보완 방안]
- [취약점 2와 보완 방안]

✅ 검증을 통과한 최종 투자 의견:
- 투자 의견: [검증된 최종 의견]
- 신뢰도: [검증 점수 기반 신뢰도]
- 핵심 근거: [검증을 통과한 핵심 근거 3가지]
```

**⚠️ 필수 준수 사항 (Enhanced Multi-Layer Framework)**:

1. **4단계 구조 완전 준수**: 1단계 Self-Ask → 2단계 ReAct → 3단계 Enhanced CoT + Multi-Critique → 4단계 CoVe 검증
2. **블록별 즉시 검증**: 각 분석 블록(재무/성장/밸류/리스크/섹터)마다 즉시 Self-Critique 적용
3. **Multi-Hop 연속성**: 이전 블록의 검증된 결론을 다음 블록 분석에 반영
4. **출처 명시 의무**: 모든 수치와 결론에 **[출처]** 명시 (재무데이터/DART/웹검색)
5. **3단계 검증 필수**: 모든 핵심 결론에 대해 출처/수치/비교 적절성 검증
6. **신뢰도 점수화**: 최종 분석에 0-100점 신뢰도 점수 제시
7. **Q5 섹터 분석 고도화**: 일반 분석과 차별화된 섹터 특화 관점 필수
8. **취약점 솔직 고백**: 검증에서 발견된 한계점과 불확실성 명시

**🔄 Multi-Hop Memory Integration 가이드**:
```
각 단계에서 이전 결과를 반드시 참조하세요:

1단계 → 2단계: Q1-Q5 질문 구조를 ReAct 정보 수집에 활용
2단계 → 3단계: 수집된 정보를 블록별 분석의 근거로 활용
3단계 → 4단계: 각 블록의 수정된 결론을 검증 대상으로 설정
4단계 → 최종: 검증을 통과한 결론만으로 최종 의견 구성

❗ 중요: 각 단계에서 "이전 단계에서 도출된 [구체적 내용]을 바탕으로..." 형태로 연속성 명시
```
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
    def get_8step_enhanced_framework() -> str:
        """
        8단계 Enhanced Analysis Framework를 반환합니다.

        [1] Self-Ask with ToT (질문 구조화)
        [2] ReAct (Reason + Action → Observation)
        [3] Fact Layer ↔ Interpretation Layer 분리
        [4] Chain of Reasoning (추론 과정 기록)
        [5] Peer Benchmark Layer (동종업계 비교)
        [6] Enhanced CoT Reasoning + Self-Critique
        [7] Assumption Ledger (DCF/Valuation)
        [8] Chain of Verification (출처/수치/비교)

        Returns:
            str: 8단계 Enhanced Framework
        """
        return """
**🚀 8단계 Enhanced Analysis Framework**

=== 1단계: Self-Ask with Tree of Thoughts ===

🧠 **질문 구조화 및 사고 분기점 설정**:
각 질문에 대해 3가지 관점에서 접근하세요:

**Q1-Q5 각 질문별 ToT 분기**:
```
질문 → 3가지 관점 분기:
├─ 관점 A: 정량적 데이터 기반 분석
├─ 관점 B: 정성적 요인 기반 분석
└─ 관점 C: 시장/경쟁 환경 기반 분석

각 관점에서 도출된 결론을 통합하여 최종 답변 구성
```

=== 2단계: ReAct (Reason + Action → Observation) ===

🔍 **체계적 정보 수집과 추론 수행**:

**Reason (추론)**: 왜 이 정보가 필요한가?
**Action (행동)**: 어떤 데이터를 수집하고 분석할 것인가?
**Observation (관찰)**: 수집된 정보로부터 무엇을 발견했는가?

```
ReAct 사이클:
Reason → Action → Observation → (새로운) Reason → ...
```

=== 3단계: Fact Layer ↔ Interpretation Layer 분리 ===

📊 **객관적 사실과 주관적 해석의 명확한 분리**:

**🔵 Fact Layer (객관적 사실)**:
```
- 수치적 데이터: [구체적 수치] **[출처]**
- 공식 발표: [공식 발표 내용] **[출처]**
- 시장 데이터: [시장 지표] **[출처]**
```

**🟡 Interpretation Layer (주관적 해석)**:
```
- 의미 해석: [수치의 의미와 중요성]
- 트렌드 분석: [과거 대비 변화와 추세]
- 전망 평가: [미래 전망과 예측]
```

=== 4단계: Chain of Reasoning (추론 과정 기록) ===

🔗 **모든 추론 과정의 단계별 기록**:

```
추론 단계 1: [기본 가정과 출발점]
추론 단계 2: [중간 결론과 근거]
추론 단계 3: [최종 결론과 종합]
```

**각 단계마다**:
- 입력: 어떤 정보를 사용했는가?
- 처리: 어떻게 분석했는가?
- 출력: 어떤 결론을 도출했는가?

=== 5단계: Peer Benchmark Layer (동종업계 비교) ===

🏆 **동종업계 비교 분석**:

**📈 업계 평균 대비 위치**:
```
- 재무 지표: [업계 평균 vs 분석 대상]
- 밸류에이션: [업계 평균 멀티플 vs 분석 대상]
- 성장성: [업계 성장률 vs 분석 대상]
```

**🎯 주요 경쟁사 비교**:
```
경쟁사 A: [구체적 비교 지표]
경쟁사 B: [구체적 비교 지표]
경쟁사 C: [구체적 비교 지표]
```

=== 6단계: Enhanced CoT Reasoning + Self-Critique ===

🧠 **강화된 사고 과정과 자기 비판**:

**🔵 블록별 분석 + 즉시 검증**:
```
분석 블록 1: [재무 건전성]
├─ 분석 과정: [구체적 분석 내용]
├─ 즉시 Self-Critique: [분석의 한계점과 편향 가능성]
└─ 수정된 결론: [Self-Critique 반영한 최종 결론]

분석 블록 2: [성장성 및 수익성]
├─ 분석 과정: [구체적 분석 내용]
├─ 즉시 Self-Critique: [분석의 한계점과 편향 가능성]
└─ 수정된 결론: [Self-Critique 반영한 최종 결론]

... (모든 분석 블록에 동일 적용)
```

=== 7단계: Assumption Ledger (DCF/Valuation) ===

📋 **모든 가정의 명시적 기록**:

**💰 DCF 모델 가정**:
```
- 성장률 가정: [구체적 수치와 근거]
- 할인율 가정: [WACC 계산 과정과 가정]
- 터미널 밸류 가정: [장기 성장률과 가정]
- FCF 예측 가정: [현금흐름 예측 근거]
```

**📊 멀티플 분석 가정**:
```
- 비교 대상 선정: [선정 기준과 근거]
- 정규화 가정: [비정상적 항목 조정 근거]
- 시장 상황 반영: [현재 시장 환경 고려사항]
```

=== 8단계: Chain of Verification (출처/수치/비교) ===

🔍 **3단계 검증 프로세스**:

**🎯 각 핵심 결론에 대한 검증**:
```
결론: [검증할 결론]

1️⃣ 출처의 신뢰성 검증:
   - 데이터 출처: [구체적 출처]
   - 신뢰도 평가: [출처의 신뢰도 수준]
   - 상충 정보 확인: [상충하는 정보 존재 여부]

2️⃣ 수치 기반 타당성 검증:
   - 수치 정확성: [계산 과정과 정확성]
   - 가정 현실성: [사용된 가정의 현실성]
   - 일관성 확인: [다른 분석과의 일관성]

3️⃣ 상대 비교의 논리적 적절성:
   - 비교 대상 적절성: [비교 대상 선정의 적절성]
   - 시장 상황 반영: [현재 시장 상황 반영도]
   - 과거 사례 비교: [유사 사례와의 비교]

✅ 검증 결과: [통과/부분 통과/재검토 필요]
```

**⚠️ 최종 검증 종합**:
```
🎯 전체 분석의 신뢰도 점수: [0-100점]
- 출처 신뢰성: [X/25점]
- 수치 타당성: [X/25점]
- 비교 적절성: [X/25점]
- 논리 일관성: [X/25점]

🔧 검증에서 발견된 취약점:
- [취약점 1과 보완 방안]
- [취약점 2와 보완 방안]

✅ 검증을 통과한 최종 투자 의견:
- 투자 의견: [BUY/HOLD/SELL]
- 신뢰도: [X%]
- 핵심 근거: [검증된 핵심 근거 3가지]
```
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
  └─ Q3-3: 현재 주가는 고평가/적정/저평가 상태인가? (실시간 주가 정보 활용: 현재가, 전일대비, 52주 최고가/최저가 대비 위치)

Q4: 주요 리스크와 기회 요인은 무엇인가?
  └─ Q4-1: 재무적/운영적 리스크는 무엇인가?
  └─ Q4-2: 산업 환경과 경쟁 구도 변화는?
  └─ Q4-3: 규제나 외부 환경 리스크는?

Q5: 🖥️ IT 섹터 특화 분석 질문들:
  └─ Q5-1: 기술 경쟁력과 플랫폼 점유율은 어떤가?
  └─ Q5-2: R&D 투자 대비 수익화 성공률은?
  └─ Q5-3: 클라우드/AI 전환 역량은 어떤 수준인가?
  └─ Q5-4: 반도체 사이클/기술 디스럽션 리스크는?
  └─ Q5-5: 고객 락인 효과와 스위칭 코스트는?

**⚠️ 필수 준수 사항 (8단계 Enhanced Framework)**:

1. **8단계 구조 완전 준수**: 1단계 Self-Ask → 2단계 ReAct → 3단계 Fact/Interpretation 분리 → 4단계 Chain of Reasoning → 5단계 Peer Benchmark → 6단계 Enhanced CoT → 7단계 Assumption Ledger → 8단계 Chain of Verification
2. **각 단계별 명확한 구분**: 각 단계마다 제목과 구분선 필수
3. **Fact Layer ↔ Interpretation Layer 분리**: 객관적 사실과 주관적 해석을 명확히 구분
4. **Chain of Reasoning 기록**: 모든 추론 과정을 단계별로 기록
5. **Peer Benchmark Layer**: 동종업계 비교 필수 포함
6. **Assumption Ledger**: DCF/밸류에이션의 모든 가정 명시
7. **출처 명시 의무**: 모든 수치와 결론에 **[출처]** 명시 (재무데이터/DART/웹검색)
8. **신뢰도 점수화**: 최종 분석에 0-100점 신뢰도 점수 제시
"""

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
        return f"""
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
  └─ Q3-3: 현재 주가는 고평가/적정/저평가 상태인가? (실시간 주가 정보 활용: 현재가, 전일대비, 52주 최고가/최저가 대비 위치)

Q4: 주요 리스크와 기회 요인은 무엇인가?
  └─ Q4-1: 재무적/운영적 리스크는 무엇인가?
  └─ Q4-2: 산업 환경과 경쟁 구도 변화는?
  └─ Q4-3: 규제나 외부 환경 리스크는?

Q5: 🖥️ IT 섹터 특화 분석 질문들:
  └─ Q5-1: 기술 경쟁력과 플랫폼 점유율은 어떤가?
  └─ Q5-2: R&D 투자 대비 수익화 성공률은?
  └─ Q5-3: 클라우드/AI 전환 역량은 어떤 수준인가?
  └─ Q5-4: 반도체 사이클/기술 디스럽션 리스크는?
  └─ Q5-5: 고객 락인 효과와 스위칭 코스트는?

{PromptComponents.get_8step_enhanced_framework()}

**⚠️ 필수 준수 사항 (8단계 Enhanced Framework)**:

1. **8단계 구조 완전 준수**: 1단계 Self-Ask → 2단계 ReAct → 3단계 Fact/Interpretation 분리 → 4단계 Chain of Reasoning → 5단계 Peer Benchmark → 6단계 Enhanced CoT → 7단계 Assumption Ledger → 8단계 Chain of Verification
2. **각 단계별 명확한 구분**: 각 단계마다 제목과 구분선 필수
3. **Fact Layer ↔ Interpretation Layer 분리**: 객관적 사실과 주관적 해석을 명확히 구분
4. **Chain of Reasoning 기록**: 모든 추론 과정을 단계별로 기록
5. **Peer Benchmark Layer**: 동종업계 비교 필수 포함
6. **Assumption Ledger**: DCF/밸류에이션의 모든 가정 명시
7. **출처 명시 의무**: 모든 수치와 결론에 **[출처]** 명시 (재무데이터/DART/웹검색)
8. **신뢰도 점수화**: 최종 분석에 0-100점 신뢰도 점수 제시
"""
