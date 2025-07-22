"""
간단하고 실용적인 8단계 분석 프레임워크
모듈화된 프롬프트 컴포넌트로 중복 제거
"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class PromptComponents:
    # ===== 공통 프롬프트 컴포넌트 =====

    @staticmethod
    def get_8step_checklist() -> str:
        """8단계 실행 체크리스트를 반환합니다."""
        return """
**📋 8단계 실행 체크리스트:**
- [ ] 1단계: Self-Ask (핵심 질문 구성)
- [ ] 2단계: ReAct (정보 수집 및 추론)
- [ ] 3단계: Fact Layer (객관적 사실 분리)
- [ ] 4단계: Interpretation Layer (주관적 해석)
- [ ] 5단계: Chain of Reasoning (추론 과정)
- [ ] 6단계: Peer Benchmark (동종업계 비교)
- [ ] 7단계: Assumption Ledger (가정 명시)
- [ ] 8단계: Chain of Verification (결론 검증)
    """

    @staticmethod
    def get_8step_structure() -> str:
        """8단계 구조 설명을 반환합니다."""
        return """
**8단계 구조 완전 준수**:
1단계 Self-Ask → 2단계 ReAct → 3단계 Fact Layer → 4단계 Interpretation Layer →
5단계 Chain of Reasoning → 6단계 Peer Benchmark → 7단계 Assumption Ledger → 8단계 Chain of Verification
"""

    @staticmethod
    def get_layer_separation_rule() -> str:
        """Fact Layer와 Interpretation Layer 분리 규칙을 반환합니다."""
        return """
**Fact Layer ↔ Interpretation Layer 분리**:
객관적 사실과 주관적 해석을 명확히 구분
- Fact Layer: 순수 사실만 기록, 모든 수치에 [출처] 명시
- Interpretation Layer: Fact Layer 기반 해석, 트렌드와 패턴 분석
"""

    @staticmethod
    def get_data_sources_guide() -> str:
        """데이터 소스 활용 가이드를 반환합니다."""
        return """
📊 **모든 데이터 종합 활용**:
✅ **재무데이터**: yfinance 데이터, 기본 재무지표 완전 분석
✅ **DART 데이터**: 재무제표, 사업보고서, 공시자료 상세 분석
✅ **사업보고서 딕셔너리**: PDF 상세 정보, 경영진 메시지 심층 분석
✅ **웹 검색 보완**: 업계 동향, 경쟁사 비교 추가 분석
"""

    @staticmethod
    def get_output_format() -> str:
        """최종 출력 형식을 반환합니다."""
        return """
**최종 출력 형식**:
- 투자 의견: BUY/HOLD/SELL
- 목표가: 구체적 금액과 산출 근거
- 핵심 근거: 3가지 이내
- 주요 리스크: 2가지 이내
"""

    @staticmethod
    def get_critical_warnings() -> str:
        """중요한 경고 메시지를 반환합니다."""
        return """
**⚠️ 필수 준수 사항 (8단계 Enhanced Framework)**:

🚨 **절대 금지**: 3단계에서 멈추지 마세요! 8단계를 모두 완료해야 합니다!

1. **8단계 구조 완전 준수**: {structure}
2. **각 단계별 명확한 구분**: 각 단계마다 "### **N단계: 제목**" 형식으로 제목 필수
3. **Fact Layer ↔ Interpretation Layer 분리**: {layer_rule}
4. **Chain of Reasoning 기록**: 모든 추론 과정을 단계별로 기록
5. **Peer Benchmark Layer**: 동종업계 비교 필수 포함
6. **Assumption Ledger**: DCF/밸류에이션의 모든 가정 명시
7. **출처 명시 의무**: 모든 수치와 결론에 **[출처]** 명시 (재무데이터/DART/웹검색)
8. **신뢰도 점수화**: 최종 분석에 0-100점 신뢰도 점수 제시

**✅ 성공 기준**: 위의 8단계를 모두 완료하고 최종 투자 의견을 제시해야 합니다!
""".format(
            structure=PromptComponents.get_8step_structure(),
            layer_rule=PromptComponents.get_layer_separation_rule(),
        )

    # ===== 8단계별 상세 설명 =====

    @staticmethod
    def get_step1_self_ask() -> str:
        """1단계 Self-Ask 설명을 반환합니다."""
        return """
### **1단계: Self-Ask (핵심 질문 구성)**

🎯 각 분석 영역별 핵심 질문을 체계적으로 구성하세요:
"""

    @staticmethod
    def get_step2_react() -> str:
        """2단계 ReAct 설명을 반환합니다."""
        return """
### **2단계: ReAct (Reason + Action) - 정보 수집**

🔍 각 질문에 대한 체계적 정보 수집과 추론 수행:

**Reason (추론)**: 왜 이 정보가 필요한가?
**Action (행동)**: 어떤 정보를 어떻게 수집할 것인가?

{data_sources}

**Observation (관찰)**: 수집된 정보의 의미는?
- 핵심 발견사항, 예상과의 차이, 추가 조사 필요성
""".format(
            data_sources=PromptComponents.get_data_sources_guide()
        )

    @staticmethod
    def get_step3_fact_layer() -> str:
        """3단계 Fact Layer 설명을 반환합니다."""
        return """
### **3단계: Fact Layer (객관적 사실 분리)**

📊 **모든 객관적 사실을 출처와 함께 명시**:
- 재무지표, 시장 데이터, 공시 정보 등
- 모든 수치에 **[출처]** 명시 필수
- 해석이나 추론 없이 순수 사실만 기록
"""

    @staticmethod
    def get_step4_interpretation_layer() -> str:
        """4단계 Interpretation Layer 설명을 반환합니다."""
        return """
### **4단계: Interpretation Layer (주관적 해석)**

🧠 **Fact Layer의 데이터를 바탕으로 한 해석**:
- 데이터의 의미와 시사점
- 트렌드 분석과 패턴 인식
- 업계 특성을 고려한 해석
"""

    @staticmethod
    def get_step5_chain_of_reasoning() -> str:
        """5단계 Chain of Reasoning 설명을 반환합니다."""
        return """
### **5단계: Chain of Reasoning (추론 과정)**

🔗 **모든 결론의 논리적 추론 과정을 단계별로 기록**:
- A → B → C 형태의 명확한 논리 체인
- 각 단계별 근거와 가정 명시
- 대안적 시나리오 고려
"""

    @staticmethod
    def get_step6_peer_benchmark() -> str:
        """6단계 Peer Benchmark 설명을 반환합니다."""
        return """
### **6단계: Peer Benchmark (동종업계 비교)**

📈 **업계 평균 및 경쟁사 대비 위치 분석**:
- 동종업계 평균과의 비교
- 주요 경쟁사 대비 상대적 위치
- 글로벌 기준 비교 (해당 시)
"""

    @staticmethod
    def get_step7_assumption_ledger() -> str:
        """7단계 Assumption Ledger 설명을 반환합니다."""
        return """
### **7단계: Assumption Ledger (가정 명시)**

📝 **모든 분석에서 사용된 가정을 명시**:
- DCF 모델의 가정 (성장률, 할인율 등)
- 멀티플 비교의 기준
- 리스크 평가의 가정
"""

    @staticmethod
    def get_step8_chain_of_verification() -> str:
        """8단계 Chain of Verification 설명을 반환합니다."""
        return """
### **8단계: Chain of Verification (결론 검증)**

✅ **각 핵심 결론에 대한 검증 수행**:
- 출처의 신뢰성 검증
- 수치 기반 타당성 검증
- 상대 비교의 논리적 적절성 검증
"""

    # ===== 메인 프롬프트 생성 메서드 =====

    @staticmethod
    def get_enhanced_analyst_thinking_flow(
        sector=None,
        sector_manager=None,
    ) -> str:
        """
        8단계 체계적 분석 프레임워크를 반환합니다.
        모듈화된 컴포넌트를 조합하여 중복 없는 프롬프트를 생성합니다.
        """

        dynamic_questions = PromptComponents._get_default_questions(
            sector, sector_manager
        )
        sector_specific_info = ""

        if sector and sector_manager:
            sector_specific_info = PromptComponents._get_sector_analysis_guidance(
                sector, sector_manager
            )

        return f"""
**🧠 Enhanced Analyst Thinking Flow (8단계 체계적 분석 프레임워크)**

⚠️ **중요**: 다음 8단계를 **반드시 순서대로 모두 수행**하세요. 3단계에서 멈추지 마세요!

{PromptComponents.get_8step_checklist()}

---

{PromptComponents.get_step1_self_ask()}

{dynamic_questions}

{sector_specific_info}

---

{PromptComponents.get_step2_react()}

---

{PromptComponents.get_step3_fact_layer()}

---

{PromptComponents.get_step4_interpretation_layer()}

---

{PromptComponents.get_step5_chain_of_reasoning()}

---

{PromptComponents.get_step6_peer_benchmark()}

---

{PromptComponents.get_step7_assumption_ledger()}

---

{PromptComponents.get_step8_chain_of_verification()}

---

{PromptComponents.get_output_format()}

{PromptComponents.get_critical_warnings()}
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

{PromptComponents.get_enhanced_analyst_thinking_flow()}

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
- [ ] 8단계 Enhanced Framework 적용: 모든 단계 순서대로 수행
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
    def get_cot_framework() -> str:
        """Chain of Thought 프레임워크를 반환합니다."""
        return """
**🔗 Chain of Thought (CoT) 프레임워크**

모든 분석에서 다음 3단계 추론 과정을 반드시 수행하세요:

**1단계: 문제 정의 (Problem Definition)**
- 분석 목표와 범위 명확화
- 필요한 정보와 데이터 소스 식별
- 분석 방법론 선택 및 근거 제시

**2단계: 논리적 추론 (Logical Reasoning)**
- 단계별 계산 과정 명시
- 가정과 전제 조건 명확화
- 중간 결론 도출 과정 기록

**3단계: 결론 검증 (Conclusion Validation)**
- 결과의 타당성 검토
- 대안적 해석 고려
- 한계점과 불확실성 명시
"""

    @staticmethod
    def get_self_critique_template() -> str:
        """Self-Critique 템플릿을 반환합니다."""
        return """
**🔍 Self-Critique 템플릿**

분석 완료 후 다음 항목들을 반드시 검토하세요:

**1. 분석의 한계점**
- 사용된 데이터의 한계
- 가정의 현실성
- 모델의 제약사항

**2. 편향 가능성**
- 확인 편향 (Confirmation Bias)
- 앵커링 편향 (Anchoring Bias)
- 과신 편향 (Overconfidence Bias)

**3. 대안적 해석**
- 반대 관점에서의 해석
- 다른 가정 하에서의 결과
- 경쟁적 가설 검토

**4. 추가 검토 필요사항**
- 추가 데이터 수집 필요성
- 더 정교한 모델 적용 가능성
- 외부 전문가 검토 필요성
"""

    @staticmethod
    def get_multi_perspective_framework() -> str:
        """Multi-Perspective 프레임워크를 반환합니다."""
        return """
**👥 Multi-Perspective 분석 프레임워크**

최소 3가지 관점에서 분석을 수행하세요:

**1. 낙관적 관점 (Optimistic View)**
- 최선의 시나리오 가정
- 긍정적 요인들의 최대 영향
- 상승 가능성 분석

**2. 보수적 관점 (Conservative View)**
- 최악의 시나리오 가정
- 부정적 요인들의 최대 영향
- 하락 가능성 분석

**3. 중립적 관점 (Neutral View)**
- 가장 현실적인 시나리오
- 균형잡힌 가정과 예측
- 객관적 근거 기반 분석

**4. 전문가 관점 (Expert View)**
- 업계 전문가들의 일반적 견해
- 학술적 연구 결과 반영
- 베스트 프랙티스 적용
"""

    @staticmethod
    def get_reasoning_validation_framework() -> str:
        """추론 검증 프레임워크를 반환합니다."""
        return """
**✅ 추론 검증 프레임워크**

모든 추론 과정에서 다음 검증을 수행하세요:

**1. 논리적 일관성 검증**
- 전제와 결론의 논리적 연결
- 모순되는 주장이 없는지 확인
- 인과관계의 타당성 검토

**2. 수치적 정확성 검증**
- 계산 과정의 정확성
- 단위와 스케일의 일관성
- 통계적 유의성 검토

**3. 가정의 현실성 검증**
- 가정의 현실 가능성
- 극단적 가정의 영향 분석
- 대안 가정의 결과 비교

**4. 외부 검증**
- 다른 분석가들의 견해와 비교
- 역사적 데이터와의 일치성
- 업계 표준과의 비교
"""

    @staticmethod
    def get_confidence_scoring_framework() -> str:
        """신뢰도 점수화 프레임워크를 반환합니다."""
        return """
**📊 신뢰도 점수화 프레임워크**

모든 결론에 대해 0-100점 신뢰도 점수를 부여하세요:

**신뢰도 평가 기준:**
- **90-100점**: 매우 높은 신뢰도 (강력한 증거, 일관된 결과)
- **80-89점**: 높은 신뢰도 (충분한 증거, 논리적 일관성)
- **70-79점**: 중간 신뢰도 (적절한 증거, 일부 불확실성)
- **60-69점**: 낮은 신뢰도 (제한적 증거, 상당한 불확실성)
- **50-59점**: 매우 낮은 신뢰도 (약한 증거, 높은 불확실성)
- **0-49점**: 신뢰할 수 없음 (증거 부족, 논리적 오류)

**신뢰도 영향 요인:**
- 데이터 품질과 양
- 분석 방법론의 적절성
- 가정의 현실성
- 외부 검증 결과
- 전문가 합의도
"""

    @staticmethod
    def get_web_search_integration_guide() -> str:
        """웹 검색 통합 가이드를 반환합니다."""
        return """
**🌐 웹 검색 통합 가이드**

최신 정보를 반영하기 위해 웹 검색을 활용하세요:

**검색 키워드 예시:**
- "[기업명] 최신 실적 발표"
- "[섹터명] 20xx년 전망"
- "[기업명] 경쟁사 비교"
- "[섹터명] 규제 변화"
- "[기업명] ESG 평가"

**검색 결과 활용 방법:**
- 최신 실적과 전망 반영
- 경쟁사 비교 정보 보완
- 업계 트렌드 분석
- 리스크 요인 업데이트
- 투자자 관심사 파악

**출처 명시 규칙:**
- 모든 웹 검색 결과에 **[웹검색]** 태그 추가
- 구체적인 출처 URL 또는 언론사 명시
- 검색 날짜와 정보의 시점 명시
- 정보의 신뢰도 평가 포함
"""

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

**2. 8단계 상세 분석 결과**
- 각 단계별 분석 내용
- Fact Layer와 Interpretation Layer 구분
- Chain of Reasoning 과정
- Peer Benchmark 비교
- Assumption Ledger 명시
- Chain of Verification 결과

**3. Self-Critique 결과**
- 분석의 한계점 및 편향 가능성
- 반대 의견 및 대안적 해석
- 추가 검토 필요 사항

**4. 신뢰도 평가**
- 각 분석 요소별 신뢰도 점수 (1-10점)
- 종합 신뢰도 및 해석
- 불확실성 요인 및 민감도 분석

**5. 투자 시사점**
- 구체적인 투자 권고사항
- 목표가 및 투자 기간
- 리스크 관리 방안

**6. 최종 출력 형식**
```
🎯 투자 의견: [BUY/HOLD/SELL]
💰 목표가: [구체적 금액]
🔍 핵심 근거: [3가지 주요 근거]
⚠️ 주요 리스크: [주요 위험 요소]
```
"""

    @staticmethod
    def _get_default_questions(sector=None, sector_manager=None) -> str:
        """기본 분석 질문들을 반환합니다. 섹터 정보가 있으면 동적으로 Q5를 생성합니다."""

        # Q1-Q4는 모든 섹터 공통
        base_questions = """
Q1: 이 기업의 재무적 건전성은 어떤가?
  └─ Q1-1: ROE, ROA, ROIC는 업계 대비 어떤 수준인가?
    • [Fact Layer] ROE: [구체적 수치]% vs 업계 평균 [수치]%
    • [Fact Layer] ROA: [구체적 수치]% vs 업계 평균 [수치]%
    • [Fact Layer] ROIC: [구체적 수치]% vs 업계 평균 [수치]%
    • [Interpretation Layer] 수익성 지표 해석: [구체적 분석]
    • [Peer Benchmark] 동종업계 순위: [구체적 순위]
    • [Chain of Reasoning] 수익성 지표가 재무 건전성에 미치는 영향: [구체적 분석]
  └─ Q1-2: 부채비율과 유동성은 안전한 수준인가?
    • [Fact Layer] 부채비율: [구체적 수치]%
    • [Fact Layer] 유동비율: [구체적 수치]
    • [Fact Layer] 당좌비율: [구체적 수치]
    • [Interpretation Layer] 부채 및 유동성 위험도 평가: [구체적 분석]
    • [Peer Benchmark] 업계 평균 대비 부채 수준: [구체적 비교]
    • [Chain of Reasoning] 부채 구조가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q1-3: 현금흐름의 질과 안정성은 어떤가?
    • [Fact Layer] 영업활동 현금흐름: [구체적 수치]억원
    • [Fact Layer] FCF: [구체적 수치]억원
    • [Fact Layer] 현금흐름 안정성: [3년간 변동성 분석]
    • [Interpretation Layer] 현금흐름 품질 평가: [구체적 분석]
    • [Peer Benchmark] 업계 평균 현금흐름 수준: [구체적 비교]
    • [Chain of Reasoning] 현금흐름이 기업 지속가능성에 미치는 영향: [구체적 분석]

Q2: 이 기업의 성장성과 수익성 전망은 어떤가?
  └─ Q2-1: 과거 3년간 매출과 이익 성장 추세는?
    • [Fact Layer] 매출 성장률: 20xx년 [수치]%, 20xx년 [수치]%, 20xx년 예상 [수치]%
    • [Fact Layer] 영업이익 성장률: 20xx년 [수치]%, 20xx년 [수치]%, 20xx년 예상 [수치]%
    • [Fact Layer] 순이익 성장률: 20xx년 [수치]%, 20xx년 [수치]%, 20xx년 예상 [수치]%
    • [Interpretation Layer] 성장 추세 해석: [구체적 분석]
    • [Peer Benchmark] 업계 평균 성장률 대비: [구체적 비교]
    • [Chain of Reasoning] 성장률이 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q2-2: 주요 성장 동력과 수익원은 무엇인가?
    • [Fact Layer] 사업부별 매출 비중: [구체적 비중]
    • [Fact Layer] 신사업 성장률: [구체적 수치]
    • [Fact Layer] 해외 매출 비중: [구체적 비중]
    • [Interpretation Layer] 성장 동력의 지속가능성 평가: [구체적 분석]
    • [Peer Benchmark] 경쟁사 대비 성장 동력: [구체적 비교]
    • [Chain of Reasoning] 성장 동력이 미래 수익성에 미치는 영향: [구체적 분석]
  └─ Q2-3: 향후 성장 지속가능성은 어떤가?
    • [Fact Layer] R&D 투자 대비 수익화 성공률: [구체적 수치]
    • [Fact Layer] 시장 점유율 변화: [구체적 추이]
    • [Fact Layer] 신기술 도입 현황: [구체적 내용]
    • [Interpretation Layer] 지속가능성 전망: [구체적 분석]
    • [Peer Benchmark] 업계 평균 대비 지속가능성: [구체적 비교]
    • [Chain of Reasoning] 지속가능성이 기업 가치에 미치는 영향: [구체적 분석]

Q3: 이 기업의 적정 가치는 얼마인가?
  └─ Q3-1: DCF 기반 내재가치는 얼마인가?
    • [Assumption Ledger] FCF 예측 가정: [구체적 가정]
    • [Fact Layer] FCF 예측: [구체적 수치]억원
    • [Assumption Ledger] WACC 계산 가정: [구체적 가정]
    • [Fact Layer] WACC: [구체적 수치]%
    • [Assumption Ledger] 성장률 가정: [구체적 가정]
    • [Fact Layer] 성장률 가정: [구체적 수치]%
    • [Fact Layer] 내재가치: [구체적 수치]원
    • [Interpretation Layer] DCF 모델의 신뢰도: [구체적 분석]
    • [Chain of Verification] DCF 가정의 민감도 분석: [구체적 분석]
  └─ Q3-2: 멀티플 기반 상대가치는 얼마인가?
    • [Fact Layer] P/E: [구체적 수치]배 vs 업계 평균 [수치]배
    • [Fact Layer] P/B: [구체적 수치]배 vs 업계 평균 [수치]배
    • [Fact Layer] EV/EBITDA: [구체적 수치]배 vs 업계 평균 [수치]배
    • [Fact Layer] 상대가치: [구체적 수치]원
    • [Interpretation Layer] 멀티플 기반 가치 평가: [구체적 분석]
    • [Peer Benchmark] 업계 평균 대비 멀티플: [구체적 비교]
    • [Chain of Verification] 멀티플 기반 가치의 신뢰도: [구체적 분석]
  └─ Q3-3: 현재 주가는 고평가/적정/저평가 상태인가?
    • [Fact Layer] 현재가: [구체적 수치]원
    • [Fact Layer] 전일대비: [구체적 수치]원 ([수치]%)
    • [Fact Layer] 52주 최고가 대비: [구체적 수치]%
    • [Fact Layer] 52주 최저가 대비: [구체적 수치]%
    • [Fact Layer] 목표가 대비: [구체적 수치]% (고평가/적정/저평가)
    • [Interpretation Layer] 주가 평가 상태 해석: [구체적 분석]
    • [Peer Benchmark] 업계 평균 대비 주가 수준: [구체적 비교]
    • [Chain of Verification] 주가 평가의 신뢰도: [구체적 분석]

Q4: 주요 리스크와 기회 요인은 무엇인가?
  └─ Q4-1: 재무적/운영적 리스크는 무엇인가?
    • [Fact Layer] 부채 리스크: [구체적 내용과 수치]
    • [Fact Layer] 환율 리스크: [구체적 내용과 수치]
    • [Fact Layer] 원자재 가격 리스크: [구체적 내용과 수치]
    • [Interpretation Layer] 리스크 영향도 평가: [구체적 분석]
    • [Peer Benchmark] 업계 평균 대비 리스크 수준: [구체적 비교]
    • [Chain of Reasoning] 리스크가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q4-2: 산업 환경과 경쟁 구도 변화는?
    • [Fact Layer] 시장 점유율 변화: [구체적 추이]
    • [Fact Layer] 신규 진입자 위협: [구체적 내용]
    • [Fact Layer] 대체재 위협: [구체적 내용]
    • [Interpretation Layer] 경쟁 환경 변화 영향 평가: [구체적 분석]
    • [Peer Benchmark] 경쟁사 대비 경쟁력: [구체적 비교]
    • [Chain of Reasoning] 경쟁 환경 변화가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q4-3: 규제나 외부 환경 리스크는?
    • [Fact Layer] 정부 규제 변화: [구체적 내용]
    • [Fact Layer] 무역 분쟁 리스크: [구체적 내용]
    • [Fact Layer] ESG 규제 리스크: [구체적 내용]
    • [Interpretation Layer] 외부 리스크 영향도 평가: [구체적 분석]
    • [Peer Benchmark] 업계 평균 대비 외부 리스크 노출도: [구체적 비교]
    • [Chain of Reasoning] 외부 리스크가 기업 가치에 미치는 영향: [구체적 분석]
"""

        # Q5는 섹터별로 동적 생성
        if sector and sector_manager:
            q5_questions = PromptComponents._get_sector_specific_q5_questions(
                sector, sector_manager
            )
            if q5_questions:
                return base_questions + q5_questions

        # 섹터별 Q5 생성 실패 또는 섹터 정보가 없으면 기본 Q5 사용
        return base_questions + PromptComponents._get_default_q5_questions()

    @staticmethod
    def _get_default_q5_questions() -> str:
        """기본 Q5 질문을 반환합니다. 섹터별 Q5 생성 실패 시 사용됩니다."""
        return """
Q5: 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: 핵심 경쟁력과 시장 포지션은?
    • [Fact Layer] 핵심 사업 영역: [구체적 내용]
    • [Fact Layer] 시장 점유율: [구체적 수치]
    • [Fact Layer] 경쟁 우위 요소: [구체적 내용]
    • [Interpretation Layer] 경쟁력 평가: [구체적 분석]
    • [Peer Benchmark] 경쟁사 대비 경쟁력: [구체적 비교]
    • [Chain of Reasoning] 경쟁력이 미래 성장에 미치는 영향: [구체적 분석]
  └─ Q5-2: 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] 핵심 사업 영역: [구체적 내용]
    • [Fact Layer] 차별화 요소: [구체적 내용]
    • [Fact Layer] 브랜드 가치: [구체적 수치]
    • [Interpretation Layer] 차별화 요소의 지속가능성: [구체적 분석]
    • [Peer Benchmark] 경쟁사 대비 차별화 요소: [구체적 비교]
    • [Chain of Reasoning] 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q5-3: 운영 효율성과 전략적 우위는?
    • [Fact Layer] 운영 효율성 지표: [구체적 수치]
    • [Fact Layer] 비용 구조: [구체적 분석]
    • [Fact Layer] 전략적 파트너십: [구체적 내용]
    • [Interpretation Layer] 운영 우위 평가: [구체적 분석]
    • [Peer Benchmark] 경쟁사 대비 운영 효율성: [구체적 비교]
    • [Chain of Reasoning] 운영 우위가 수익성에 미치는 영향: [구체적 분석]
"""

    @staticmethod
    def _generate_sector_specific_questions(sector=None, sector_manager=None) -> str:
        """
        특정 섹터에 맞춤화된 동적 질문들을 생성합니다.
        현재는 Q5만 사용하므로 Q5 섹터별 질문만 반환합니다.

        Args:
            sector: GICS 섹터
            sector_manager: 섹터 매니저 인스턴스

        Returns:
            str: 기본 질문 + 섹터별 Q5 질문
        """
        try:
            # 기본 질문 가져오기 (섹터 정보 포함)
            base_questions = PromptComponents._get_default_questions(
                sector, sector_manager
            )
            return base_questions

        except Exception as e:
            logger.warning(f"⚠️ 섹터별 질문 생성 실패: {e}")
            return PromptComponents._get_default_questions()

    @staticmethod
    def _get_sector_specific_q5_questions(sector=None, sector_manager=None) -> str:
        """섹터별 Q5 특화 질문을 반환합니다."""
        if not sector or not sector_manager:
            return ""

        try:
            # 섹터가 문자열인지 객체인지 확인
            if isinstance(sector, str):
                sector_name = sector
            else:
                sector_name = getattr(
                    sector_manager, "get_sector_korean_name", lambda x: str(x)
                )(sector)

            # 섹터별 특화 질문 매핑 (GICS 섹터 이름과 일치)
            sector_specific_questions = {
                "INFORMATION_TECHNOLOGY": f"""
Q5: {sector_name} 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: {sector_name} 섹터 내 기술력과 시장 경쟁력은?
    • [Fact Layer] R&D 투자 규모: [구체적 수치]
    • [Fact Layer] 특허 보유 현황: [구체적 내용]
    • [Fact Layer] 기술 혁신 속도: [구체적 평가]
    • [Fact Layer] 시장 점유율: [구체적 수치]
    • [Interpretation Layer] 섹터 내 기술 경쟁력 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 기술력: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 기술력이 미래 성장에 미치는 영향: [구체적 분석]
  └─ Q5-2: {sector_name} 섹터 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] AI/클라우드/반도체 등 핵심 기술 영역: [구체적 내용]
    • [Fact Layer] 소프트웨어/하드웨어 비중: [구체적 비중]
    • [Fact Layer] 글로벌 시장 진출 현황: [구체적 내용]
    • [Interpretation Layer] 섹터 특화 차별화 요소의 지속가능성: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 차별화 요소: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q5-3: {sector_name} 섹터 운영 효율성과 전략적 우위는?
    • [Fact Layer] 개발 효율성 (인력당 매출): [구체적 수치]
    • [Fact Layer] 연구개발 투자 효율성: [구체적 분석]
    • [Fact Layer] 기술 파트너십 및 생태계: [구체적 내용]
    • [Interpretation Layer] 섹터 내 운영 우위 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 운영 효율성: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 운영 우위가 수익성에 미치는 영향: [구체적 분석]
""",
                "FINANCIALS": f"""
Q5: {sector_name} 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: {sector_name} 섹터 내 금융 서비스 경쟁력은?
    • [Fact Layer] 자본 적정성 비율 (BIS): [구체적 수치]
    • [Fact Layer] 대출 품질 지표: [구체적 내용]
    • [Fact Layer] 수수료 수익 비중: [구체적 비중]
    • [Fact Layer] 디지털 뱅킹 점유율: [구체적 수치]
    • [Interpretation Layer] 섹터 내 금융 경쟁력 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 금융 서비스 품질: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 금융 경쟁력이 미래 성장에 미치는 영향: [구체적 분석]
  └─ Q5-2: {sector_name} 섹터 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] 핵심 금융 상품 영역: [구체적 내용]
    • [Fact Layer] 핀테크 투자 및 혁신: [구체적 내용]
    • [Fact Layer] 해외 진출 및 글로벌 네트워크: [구체적 내용]
    • [Interpretation Layer] 섹터 특화 차별화 요소의 지속가능성: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 차별화 요소: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q5-3: {sector_name} 섹터 운영 효율성과 전략적 우위는?
    • [Fact Layer] 비용 대비 수익 비율 (CIR): [구체적 수치]
    • [Fact Layer] 디지털 전환 투자 효율성: [구체적 분석]
    • [Fact Layer] 규제 대응 및 리스크 관리: [구체적 내용]
    • [Interpretation Layer] 섹터 내 운영 우위 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 운영 효율성: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 운영 우위가 수익성에 미치는 영향: [구체적 분석]
""",
                "CONSUMER_DISCRETIONARY": f"""
Q5: {sector_name} 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: {sector_name} 섹터 내 브랜드 경쟁력은?
    • [Fact Layer] 브랜드 가치 및 인지도: [구체적 수치]
    • [Fact Layer] 고객 충성도 지표: [구체적 내용]
    • [Fact Layer] 제품 품질 및 디자인: [구체적 평가]
    • [Fact Layer] 시장 점유율: [구체적 수치]
    • [Interpretation Layer] 섹터 내 브랜드 경쟁력 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 브랜드력: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 브랜드 경쟁력이 미래 성장에 미치는 영향: [구체적 분석]
  └─ Q5-2: {sector_name} 섹터 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] 핵심 제품/서비스 영역: [구체적 내용]
    • [Fact Layer] 온라인/오프라인 채널 전략: [구체적 내용]
    • [Fact Layer] 글로벌 시장 진출 현황: [구체적 내용]
    • [Interpretation Layer] 섹터 특화 차별화 요소의 지속가능성: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 차별화 요소: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q5-3: {sector_name} 섹터 운영 효율성과 전략적 우위는?
    • [Fact Layer] 매장당 매출 효율성: [구체적 수치]
    • [Fact Layer] 공급망 및 재고 관리: [구체적 분석]
    • [Fact Layer] 디지털 전환 및 고객 경험: [구체적 내용]
    • [Interpretation Layer] 섹터 내 운영 우위 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 운영 효율성: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 운영 우위가 수익성에 미치는 영향: [구체적 분석]
""",
                "HEALTH_CARE": f"""
Q5: {sector_name} 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: {sector_name} 섹터 내 의료 기술 경쟁력은?
    • [Fact Layer] R&D 투자 규모: [구체적 수치]
    • [Fact Layer] 의료 특허 보유 현황: [구체적 내용]
    • [Fact Layer] 임상시험 성공률: [구체적 수치]
    • [Fact Layer] 의료 기기/제약 품질: [구체적 평가]
    • [Interpretation Layer] 섹터 내 의료 기술 경쟁력 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 의료 기술력: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 의료 기술력이 미래 성장에 미치는 영향: [구체적 분석]
  └─ Q5-2: {sector_name} 섹터 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] 핵심 의료 분야: [구체적 내용]
    • [Fact Layer] 바이오/디지털 헬스 혁신: [구체적 내용]
    • [Fact Layer] 글로벌 의료 시장 진출: [구체적 내용]
    • [Interpretation Layer] 섹터 특화 차별화 요소의 지속가능성: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 차별화 요소: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q5-3: {sector_name} 섹터 운영 효율성과 전략적 우위는?
    • [Fact Layer] 의료 서비스 효율성: [구체적 수치]
    • [Fact Layer] 규제 승인 및 인증: [구체적 분석]
    • [Fact Layer] 의료 파트너십 및 네트워크: [구체적 내용]
    • [Interpretation Layer] 섹터 내 운영 우위 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 운영 효율성: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 운영 우위가 수익성에 미치는 영향: [구체적 분석]
""",
                "INDUSTRIALS": f"""
Q5: {sector_name} 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: {sector_name} 섹터 내 제조 기술 경쟁력은?
    • [Fact Layer] 제조 기술 수준: [구체적 평가]
    • [Fact Layer] 자동화 및 스마트팩토리: [구체적 내용]
    • [Fact Layer] 품질 관리 시스템: [구체적 평가]
    • [Fact Layer] 시장 점유율: [구체적 수치]
    • [Interpretation Layer] 섹터 내 제조 기술 경쟁력 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 제조 기술력: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 제조 기술력이 미래 성장에 미치는 영향: [구체적 분석]
  └─ Q5-2: {sector_name} 섹터 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] 핵심 제조 분야: [구체적 내용]
    • [Fact Layer] 글로벌 공급망: [구체적 내용]
    • [Fact Layer] 지속가능 제조 및 ESG: [구체적 내용]
    • [Interpretation Layer] 섹터 특화 차별화 요소의 지속가능성: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 차별화 요소: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q5-3: {sector_name} 섹터 운영 효율성과 전략적 우위는?
    • [Fact Layer] 생산성 및 효율성 지표: [구체적 수치]
    • [Fact Layer] 공급망 최적화: [구체적 분석]
    • [Fact Layer] 고객 서비스 및 유지보수: [구체적 내용]
    • [Interpretation Layer] 섹터 내 운영 우위 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 운영 효율성: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 운영 우위가 수익성에 미치는 영향: [구체적 분석]
""",
                "ENERGY": f"""
Q5: {sector_name} 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: {sector_name} 섹터 내 에너지 자원 경쟁력은?
    • [Fact Layer] 원유/가스 매장량 및 생산량: [구체적 수치]
    • [Fact Layer] 탐사 및 개발 기술력: [구체적 평가]
    • [Fact Layer] 글로벌 에너지 자원 포트폴리오: [구체적 내용]
    • [Fact Layer] 시장 점유율: [구체적 수치]
    • [Interpretation Layer] 섹터 내 에너지 자원 경쟁력 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 자원 보유량: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 에너지 자원 경쟁력이 미래 성장에 미치는 영향: [구체적 분석]
  └─ Q5-2: {sector_name} 섹터 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] 신재생에너지 투자 및 포트폴리오: [구체적 내용]
    • [Fact Layer] 에너지 효율성 및 친환경 기술: [구체적 내용]
    • [Fact Layer] 글로벌 에너지 시장 진출: [구체적 내용]
    • [Interpretation Layer] 섹터 특화 차별화 요소의 지속가능성: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 차별화 요소: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q5-3: {sector_name} 섹터 운영 효율성과 전략적 우위는?
    • [Fact Layer] 생산 효율성 및 비용 구조: [구체적 수치]
    • [Fact Layer] 에너지 가격 변동 리스크 관리: [구체적 분석]
    • [Fact Layer] 정부 정책 및 규제 대응: [구체적 내용]
    • [Interpretation Layer] 섹터 내 운영 우위 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 운영 효율성: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 운영 우위가 수익성에 미치는 영향: [구체적 분석]
""",
                "MATERIALS": f"""
Q5: {sector_name} 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: {sector_name} 섹터 내 소재 기술 경쟁력은?
    • [Fact Layer] 신소재 개발 및 특허 보유: [구체적 내용]
    • [Fact Layer] 원자재 확보 및 공급망: [구체적 평가]
    • [Fact Layer] 제품 품질 및 기술력: [구체적 평가]
    • [Fact Layer] 시장 점유율: [구체적 수치]
    • [Interpretation Layer] 섹터 내 소재 기술 경쟁력 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 소재 기술력: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 소재 기술력이 미래 성장에 미치는 영향: [구체적 분석]
  └─ Q5-2: {sector_name} 섹터 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] 핵심 소재 분야: [구체적 내용]
    • [Fact Layer] 친환경 소재 및 ESG 대응: [구체적 내용]
    • [Fact Layer] 글로벌 시장 진출 및 수출: [구체적 내용]
    • [Interpretation Layer] 섹터 특화 차별화 요소의 지속가능성: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 차별화 요소: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q5-3: {sector_name} 섹터 운영 효율성과 전략적 우위는?
    • [Fact Layer] 생산 효율성 및 원가 관리: [구체적 수치]
    • [Fact Layer] 원자재 가격 변동 대응: [구체적 분석]
    • [Fact Layer] 고객 파트너십 및 장기 계약: [구체적 내용]
    • [Interpretation Layer] 섹터 내 운영 우위 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 운영 효율성: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 운영 우위가 수익성에 미치는 영향: [구체적 분석]
""",
                "CONSUMER_STAPLES": f"""
Q5: {sector_name} 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: {sector_name} 섹터 내 브랜드 및 제품 경쟁력은?
    • [Fact Layer] 브랜드 가치 및 시장 인지도: [구체적 수치]
    • [Fact Layer] 제품 품질 및 안전성: [구체적 평가]
    • [Fact Layer] 고객 충성도 및 재구매율: [구체적 수치]
    • [Fact Layer] 시장 점유율: [구체적 수치]
    • [Interpretation Layer] 섹터 내 브랜드 경쟁력 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 브랜드력: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 브랜드 경쟁력이 미래 성장에 미치는 영향: [구체적 분석]
  └─ Q5-2: {sector_name} 섹터 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] 핵심 제품 카테고리: [구체적 내용]
    • [Fact Layer] 유통 채널 및 공급망: [구체적 내용]
    • [Fact Layer] 건강식품 및 프리미엄 제품: [구체적 내용]
    • [Interpretation Layer] 섹터 특화 차별화 요소의 지속가능성: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 차별화 요소: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q5-3: {sector_name} 섹터 운영 효율성과 전략적 우위는?
    • [Fact Layer] 매장당 매출 및 운영 효율성: [구체적 수치]
    • [Fact Layer] 공급망 및 재고 관리: [구체적 분석]
    • [Fact Layer] 원가 관리 및 마진 최적화: [구체적 내용]
    • [Interpretation Layer] 섹터 내 운영 우위 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 운영 효율성: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 운영 우위가 수익성에 미치는 영향: [구체적 분석]
""",
                "COMMUNICATION_SERVICES": f"""
Q5: {sector_name} 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: {sector_name} 섹터 내 콘텐츠 및 플랫폼 경쟁력은?
    • [Fact Layer] 콘텐츠 포트폴리오 및 IP 보유: [구체적 내용]
    • [Fact Layer] 플랫폼 사용자 수 및 참여도: [구체적 수치]
    • [Fact Layer] 광고 수익 및 수익화 모델: [구체적 평가]
    • [Fact Layer] 시장 점유율: [구체적 수치]
    • [Interpretation Layer] 섹터 내 콘텐츠 경쟁력 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 콘텐츠력: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 콘텐츠 경쟁력이 미래 성장에 미치는 영향: [구체적 분석]
  └─ Q5-2: {sector_name} 섹터 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] 핵심 서비스 영역: [구체적 내용]
    • [Fact Layer] 디지털 전환 및 기술 혁신: [구체적 내용]
    • [Fact Layer] 글로벌 시장 진출: [구체적 내용]
    • [Interpretation Layer] 섹터 특화 차별화 요소의 지속가능성: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 차별화 요소: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q5-3: {sector_name} 섹터 운영 효율성과 전략적 우위는?
    • [Fact Layer] 사용자당 수익 (ARPU): [구체적 수치]
    • [Fact Layer] 콘텐츠 제작 및 운영 효율성: [구체적 분석]
    • [Fact Layer] 파트너십 및 생태계 구축: [구체적 내용]
    • [Interpretation Layer] 섹터 내 운영 우위 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 운영 효율성: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 운영 우위가 수익성에 미치는 영향: [구체적 분석]
""",
                "UTILITIES": f"""
Q5: {sector_name} 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: {sector_name} 섹터 내 인프라 및 서비스 경쟁력은?
    • [Fact Layer] 발전 설비 용량 및 효율성: [구체적 수치]
    • [Fact Layer] 송배전 네트워크 및 안정성: [구체적 평가]
    • [Fact Layer] 고객 서비스 품질: [구체적 평가]
    • [Fact Layer] 시장 점유율: [구체적 수치]
    • [Interpretation Layer] 섹터 내 인프라 경쟁력 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 인프라력: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 인프라 경쟁력이 미래 성장에 미치는 영향: [구체적 분석]
  └─ Q5-2: {sector_name} 섹터 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] 신재생에너지 포트폴리오: [구체적 내용]
    • [Fact Layer] 스마트그리드 및 디지털화: [구체적 내용]
    • [Fact Layer] 에너지 효율성 서비스: [구체적 내용]
    • [Interpretation Layer] 섹터 특화 차별화 요소의 지속가능성: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 차별화 요소: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q5-3: {sector_name} 섹터 운영 효율성과 전략적 우위는?
    • [Fact Layer] 운영 효율성 및 비용 관리: [구체적 수치]
    • [Fact Layer] 규제 대응 및 정책 리스크: [구체적 분석]
    • [Fact Layer] 장기 계약 및 수익 안정성: [구체적 내용]
    • [Interpretation Layer] 섹터 내 운영 우위 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 운영 효율성: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 운영 우위가 수익성에 미치는 영향: [구체적 분석]
""",
                "REAL_ESTATE": f"""
Q5: {sector_name} 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: {sector_name} 섹터 내 부동산 포트폴리오 경쟁력은?
    • [Fact Layer] 부동산 자산 가치 및 수익률: [구체적 수치]
    • [Fact Layer] 입지 및 접근성: [구체적 평가]
    • [Fact Layer] 임차인 품질 및 임대료 안정성: [구체적 평가]
    • [Fact Layer] 시장 점유율: [구체적 수치]
    • [Interpretation Layer] 섹터 내 부동산 포트폴리오 경쟁력 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 포트폴리오 품질: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 부동산 경쟁력이 미래 성장에 미치는 영향: [구체적 분석]
  └─ Q5-2: {sector_name} 섹터 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] 핵심 부동산 분야: [구체적 내용]
    • [Fact Layer] 개발 및 재개발 프로젝트: [구체적 내용]
    • [Fact Layer] 디지털 부동산 서비스: [구체적 내용]
    • [Interpretation Layer] 섹터 특화 차별화 요소의 지속가능성: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 차별화 요소: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q5-3: {sector_name} 섹터 운영 효율성과 전략적 우위는?
    • [Fact Layer] 임대 수익률 및 운영 효율성: [구체적 수치]
    • [Fact Layer] 자산 관리 및 유지보수: [구체적 분석]
    • [Fact Layer] 금융 구조 및 부채 관리: [구체적 내용]
    • [Interpretation Layer] 섹터 내 운영 우위 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 운영 효율성: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 운영 우위가 수익성에 미치는 영향: [구체적 분석]
""",
            }

            # 섹터별 특화 질문 반환 (GICS 섹터 이름 매칭)
            # 섹터가 문자열인 경우 GICS 섹터 이름으로 변환
            if isinstance(sector, str):
                sector_key = sector.upper()
            else:
                sector_key = sector.name

            if sector_key in sector_specific_questions:
                return sector_specific_questions[sector_key]
            else:
                # 기본 섹터 특화 질문 (새로운 섹터용)
                return f"""
Q5: {sector_name} 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: {sector_name} 섹터 내 핵심 경쟁력은?
    • [Fact Layer] 섹터 핵심 역량: [구체적 내용]
    • [Fact Layer] 시장 점유율: [구체적 수치]
    • [Fact Layer] 경쟁 우위 요소: [구체적 내용]
    • [Interpretation Layer] 섹터 내 경쟁력 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 경쟁력: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 경쟁력이 미래 성장에 미치는 영향: [구체적 분석]
  └─ Q5-2: {sector_name} 섹터 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] 섹터 핵심 사업 영역: [구체적 내용]
    • [Fact Layer] 섹터 차별화 요소: [구체적 내용]
    • [Fact Layer] 브랜드 가치: [구체적 수치]
    • [Interpretation Layer] 섹터 특화 차별화 요소의 지속가능성: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 차별화 요소: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석]
  └─ Q5-3: {sector_name} 섹터 운영 효율성과 전략적 우위는?
    • [Fact Layer] 섹터 운영 효율성 지표: [구체적 수치]
    • [Fact Layer] 섹터 비용 구조: [구체적 분석]
    • [Fact Layer] 섹터 전략적 파트너십: [구체적 내용]
    • [Interpretation Layer] 섹터 내 운영 우위 평가: [구체적 분석]
    • [Peer Benchmark] 섹터 내 경쟁사 대비 운영 효율성: [구체적 비교]
    • [Chain of Reasoning] 섹터 특화 운영 우위가 수익성에 미치는 영향: [구체적 분석]
"""

        except Exception as e:
            logger.warning(f"⚠️ 섹터별 Q5 질문 생성 실패: {e}")
            return ""

    @staticmethod
    def _get_sector_analysis_guidance(sector, sector_manager) -> str:
        """섹터별 분석 가이드라인을 반환합니다."""
        try:
            # 섹터 특성 정보 가져오기 (안전하게)
            sector_description = ""
            if hasattr(sector, "description"):
                sector_description = sector.description
            elif sector_manager and hasattr(sector_manager, "get_sector_context"):
                try:
                    sector_context = sector_manager.get_sector_context(sector)
                    sector_description = sector_context.get("description", "")
                except:
                    sector_description = f"{sector.name} 섹터의 특성"
            else:
                sector_description = f"{sector.name} 섹터의 특성"

            # 경쟁사 정보 가져오기 (안전하게)
            competitors_info = "해당 섹터 주요 기업들"
            if sector_manager and hasattr(sector_manager, "get_competitors"):
                try:
                    competitors = sector_manager.get_competitors(sector)
                    if competitors:
                        competitors_info = ", ".join(competitors)
                except:
                    pass

            return f"""
**🏭 {sector.name} 섹터 특화 분석 가이드**

이 기업은 {sector.name} 섹터에 속하며, 다음 섹터 특화 요소들을 고려하여 분석하세요:

- **섹터 특성**: {sector_description}
- **주요 경쟁사**: {competitors_info}
- **섹터 트렌드**: 최신 업계 동향과 기술 발전 방향
- **규제 환경**: 해당 섹터에 적용되는 특별한 규제나 정책
- **성장 동력**: 섹터 내 주요 성장 요인과 기회 요소
"""
        except Exception as e:
            logger.warning(f"⚠️ 섹터 분석 가이드 생성 실패: {e}")
        return f"""
**🏭 {sector.name} 섹터 특화 분석 가이드**

이 기업은 {sector.name} 섹터에 속하며, 다음 섹터 특화 요소들을 고려하여 분석하세요:

- **섹터 특성**: {sector.name} 섹터의 특성
- **주요 경쟁사**: 해당 섹터 주요 기업들
- **섹터 트렌드**: 최신 업계 동향과 기술 발전 방향
- **규제 환경**: 해당 섹터에 적용되는 특별한 규제나 정책
- **성장 동력**: 섹터 내 주요 성장 요인과 기회 요소
"""

    @staticmethod
    def get_8step_enhanced_framework() -> str:
        """8단계 향상된 프레임워크를 반환합니다."""
        return """
**🎯 8단계 Enhanced Framework 적용 가이드**

각 분석 단계에서 다음 형식을 따라주세요:

**1단계: Self-Ask**
- 핵심 질문을 명확히 정의
- 분석 범위와 깊이 설정

**2단계: ReAct**
- 정보 수집 계획 수립
- 필요한 데이터 소스 식별

**3단계: Fact Layer**
- 객관적 사실만 기록
- 모든 수치에 출처 명시

**4단계: Interpretation Layer**
- Fact Layer 기반 해석
- 트렌드와 패턴 분석

**5단계: Chain of Reasoning**
- 논리적 추론 과정 기록
- 단계별 근거 명시

**6단계: Peer Benchmark**
- 업계 평균과 비교
- 경쟁사 대비 위치 분석

**7단계: Assumption Ledger**
- 모든 가정을 명시
- 가정의 근거 제시

**8단계: Chain of Verification**
- 결론의 신뢰성 검증
- 취약점과 한계점 명시

**최종 출력 형식:**
```
🎯 투자 의견: [BUY/HOLD/SELL]
💰 목표가: [구체적 금액]
📊 신뢰도: [0-100점]
🔍 핵심 근거: [3가지 주요 근거]
⚠️ 주요 리스크: [주요 위험 요소]
```
"""
