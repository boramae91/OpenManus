"""
간단하고 실용적인 8단계 분석 프레임워크
"""


class PromptComponentsSimple:
    @staticmethod
    def get_enhanced_analyst_thinking_flow(
        sector=None,
        sector_manager=None,
    ) -> str:
        """
        8단계 체계적 분석 프레임워크를 반환합니다.
        기존의 복잡한 4단계 구조를 실용적인 8단계로 단순화했습니다.
        """

        dynamic_questions = PromptComponentsSimple._get_default_questions()
        sector_specific_info = ""

        if sector and sector_manager:
            sector_specific_info = PromptComponentsSimple._get_sector_analysis_guidance(
                sector, sector_manager
            )

        return f"""
**🧠 Enhanced Analyst Thinking Flow (8단계 체계적 분석 프레임워크)**

모든 분석에서 다음 8단계 애널리스트 사고 흐름을 **반드시 순서대로** 수행하세요:

=== 1단계: Self-Ask (핵심 질문 구성) ===

🎯 각 분석 영역별 핵심 질문을 체계적으로 구성하세요:

{dynamic_questions}

{sector_specific_info}

=== 2단계: ReAct (Reason + Action) - 정보 수집 ===

🔍 각 질문에 대한 체계적 정보 수집과 추론 수행:

**Reason (추론)**: 왜 이 정보가 필요한가?
**Action (행동)**: 어떤 정보를 어떻게 수집할 것인가?

📊 **모든 데이터 종합 활용**:
✅ **재무데이터**: yfinance 데이터, 기본 재무지표 완전 분석
✅ **DART 데이터**: 재무제표, 사업보고서, 공시자료 상세 분석
✅ **사업보고서 딕셔너리**: PDF 상세 정보, 경영진 메시지 심층 분석
✅ **웹 검색 보완**: 업계 동향, 경쟁사 비교 추가 분석

**Observation (관찰)**: 수집된 정보의 의미는?
- 핵심 발견사항, 예상과의 차이, 추가 조사 필요성

=== 3단계: Fact Layer (객관적 사실 분리) ===

📊 **모든 객관적 사실을 출처와 함께 명시**:
- 재무지표, 시장 데이터, 공시 정보 등
- 모든 수치에 **[출처]** 명시 필수
- 해석이나 추론 없이 순수 사실만 기록

=== 4단계: Interpretation Layer (주관적 해석) ===

🧠 **Fact Layer의 데이터를 바탕으로 한 해석**:
- 데이터의 의미와 시사점
- 트렌드 분석과 패턴 인식
- 업계 특성을 고려한 해석

=== 5단계: Chain of Reasoning (추론 과정) ===

🔗 **모든 결론의 논리적 추론 과정을 단계별로 기록**:
- A → B → C 형태의 명확한 논리 체인
- 각 단계별 근거와 가정 명시
- 대안적 시나리오 고려

=== 6단계: Peer Benchmark (동종업계 비교) ===

📈 **업계 평균 및 경쟁사 대비 위치 분석**:
- 동종업계 평균과의 비교
- 주요 경쟁사 대비 상대적 위치
- 글로벌 기준 비교 (해당 시)

=== 7단계: Assumption Ledger (가정 명시) ===

📝 **모든 분석에서 사용된 가정을 명시**:
- DCF 모델의 가정 (성장률, 할인율 등)
- 멀티플 비교의 기준
- 리스크 평가의 가정

=== 8단계: Chain of Verification (결론 검증) ===

✅ **각 핵심 결론에 대한 검증 수행**:
- 출처의 신뢰성 검증
- 수치 기반 타당성 검증
- 상대 비교의 논리적 적절성 검증

**⚠️ 필수 준수 사항 (8단계 Enhanced Framework)**:

1. **8단계 구조 완전 준수**: 1단계 Self-Ask → 2단계 ReAct → 3단계 Fact Layer → 4단계 Interpretation Layer → 5단계 Chain of Reasoning → 6단계 Peer Benchmark → 7단계 Assumption Ledger → 8단계 Chain of Verification
2. **각 단계별 명확한 구분**: 각 단계마다 제목과 구분선 필수
3. **Fact Layer ↔ Interpretation Layer 분리**: 객관적 사실과 주관적 해석을 명확히 구분
4. **Chain of Reasoning 기록**: 모든 추론 과정을 단계별로 기록
5. **Peer Benchmark Layer**: 동종업계 비교 필수 포함
6. **Assumption Ledger**: DCF/밸류에이션의 모든 가정 명시
7. **출처 명시 의무**: 모든 수치와 결론에 **[출처]** 명시 (재무데이터/DART/웹검색)
8. **신뢰도 점수화**: 최종 분석에 0-100점 신뢰도 점수 제시
"""

    @staticmethod
    def _get_default_questions() -> str:
        """기본 분석 질문들을 반환합니다."""
        return """
Q1: 이 기업의 재무적 건전성은 어떤가?
  └─ Q1-1: ROE, ROA, ROIC는 업계 대비 어떤 수준인가?
    • [Fact Layer] ROE: [구체적 수치]% vs 업계 평균 [수치]% **[출처]**
    • [Fact Layer] ROA: [구체적 수치]% vs 업계 평균 [수치]% **[출처]**
    • [Fact Layer] ROIC: [구체적 수치]% vs 업계 평균 [수치]% **[출처]**
    • [Interpretation Layer] 수익성 지표 해석: [구체적 분석] **[출처]**
    • [Peer Benchmark] 동종업계 순위: [구체적 순위] **[출처]**
    • [Chain of Reasoning] 수익성 지표가 재무 건전성에 미치는 영향: [구체적 분석] **[출처]**
  └─ Q1-2: 부채비율과 유동성은 안전한 수준인가?
    • [Fact Layer] 부채비율: [구체적 수치]% (안전 기준: 50% 이하) **[출처]**
    • [Fact Layer] 유동비율: [구체적 수치] (안전 기준: 1.0 이상) **[출처]**
    • [Fact Layer] 당좌비율: [구체적 수치] (안전 기준: 0.8 이상) **[출처]**
    • [Interpretation Layer] 부채 및 유동성 위험도 평가: [구체적 분석] **[출처]**
    • [Peer Benchmark] 업계 평균 대비 부채 수준: [구체적 비교] **[출처]**
    • [Chain of Reasoning] 부채 구조가 기업 가치에 미치는 영향: [구체적 분석] **[출처]**
  └─ Q1-3: 현금흐름의 질과 안정성은 어떤가?
    • [Fact Layer] 영업활동 현금흐름: [구체적 수치]억원 **[출처]**
    • [Fact Layer] FCF: [구체적 수치]억원 **[출처]**
    • [Fact Layer] 현금흐름 안정성: [3년간 변동성 분석] **[출처]**
    • [Interpretation Layer] 현금흐름 품질 평가: [구체적 분석] **[출처]**
    • [Peer Benchmark] 업계 평균 현금흐름 수준: [구체적 비교] **[출처]**
    • [Chain of Reasoning] 현금흐름이 기업 지속가능성에 미치는 영향: [구체적 분석] **[출처]**

Q2: 이 기업의 성장성과 수익성 전망은 어떤가?
  └─ Q2-1: 과거 3년간 매출과 이익 성장 추세는?
    • [Fact Layer] 매출 성장률: 20xx년 [수치]%, 20xx년 [수치]%, 20xx년 예상 [수치]% **[출처]**
    • [Fact Layer] 영업이익 성장률: 20xx년 [수치]%, 20xx년 [수치]%, 20xx년 예상 [수치]% **[출처]**
    • [Fact Layer] 순이익 성장률: 20xx년 [수치]%, 20xx년 [수치]%, 20xx년 예상 [수치]% **[출처]**
    • [Interpretation Layer] 성장 추세 해석: [구체적 분석] **[출처]**
    • [Peer Benchmark] 업계 평균 성장률 대비: [구체적 비교] **[출처]**
    • [Chain of Reasoning] 성장률이 기업 가치에 미치는 영향: [구체적 분석] **[출처]**
  └─ Q2-2: 주요 성장 동력과 수익원은 무엇인가?
    • [Fact Layer] 사업부별 매출 비중: [구체적 비중] **[출처]**
    • [Fact Layer] 신사업 성장률: [구체적 수치] **[출처]**
    • [Fact Layer] 해외 매출 비중: [구체적 비중] **[출처]**
    • [Interpretation Layer] 성장 동력의 지속가능성 평가: [구체적 분석] **[출처]**
    • [Peer Benchmark] 경쟁사 대비 성장 동력: [구체적 비교] **[출처]**
    • [Chain of Reasoning] 성장 동력이 미래 수익성에 미치는 영향: [구체적 분석] **[출처]**
  └─ Q2-3: 향후 성장 지속가능성은 어떤가?
    • [Fact Layer] R&D 투자 대비 수익화 성공률: [구체적 수치] **[출처]**
    • [Fact Layer] 시장 점유율 변화: [구체적 추이] **[출처]**
    • [Fact Layer] 신기술 도입 현황: [구체적 내용] **[출처]**
    • [Interpretation Layer] 지속가능성 전망: [구체적 분석] **[출처]**
    • [Peer Benchmark] 업계 평균 대비 지속가능성: [구체적 비교] **[출처]**
    • [Chain of Reasoning] 지속가능성이 기업 가치에 미치는 영향: [구체적 분석] **[출처]**

Q3: 이 기업의 적정 가치는 얼마인가?
  └─ Q3-1: DCF 기반 내재가치는 얼마인가?
    • [Assumption Ledger] FCF 예측 가정: [구체적 가정] **[출처]**
    • [Fact Layer] FCF 예측: [구체적 수치]억원 **[출처]**
    • [Assumption Ledger] WACC 계산 가정: [구체적 가정] **[출처]**
    • [Fact Layer] WACC: [구체적 수치]% **[출처]**
    • [Assumption Ledger] 성장률 가정: [구체적 가정] **[출처]**
    • [Fact Layer] 성장률 가정: [구체적 수치]% **[출처]**
    • [Fact Layer] 내재가치: [구체적 수치]원 **[출처]**
    • [Interpretation Layer] DCF 모델의 신뢰도: [구체적 분석] **[출처]**
    • [Chain of Verification] DCF 가정의 민감도 분석: [구체적 분석] **[출처]**
  └─ Q3-2: 멀티플 기반 상대가치는 얼마인가?
    • [Fact Layer] P/E: [구체적 수치]배 vs 업계 평균 [수치]배 **[출처]**
    • [Fact Layer] P/B: [구체적 수치]배 vs 업계 평균 [수치]배 **[출처]**
    • [Fact Layer] EV/EBITDA: [구체적 수치]배 vs 업계 평균 [수치]배 **[출처]**
    • [Fact Layer] 상대가치: [구체적 수치]원 **[출처]**
    • [Interpretation Layer] 멀티플 기반 가치 평가: [구체적 분석] **[출처]**
    • [Peer Benchmark] 업계 평균 대비 멀티플: [구체적 비교] **[출처]**
    • [Chain of Verification] 멀티플 기반 가치의 신뢰도: [구체적 분석] **[출처]**
  └─ Q3-3: 현재 주가는 고평가/적정/저평가 상태인가?
    • [Fact Layer] 현재가: [구체적 수치]원 **[yfinance]**
    • [Fact Layer] 전일대비: [구체적 수치]원 ([수치]%) **[yfinance]**
    • [Fact Layer] 52주 최고가 대비: [구체적 수치]% **[yfinance]**
    • [Fact Layer] 52주 최저가 대비: [구체적 수치]% **[yfinance]**
    • [Fact Layer] 목표가 대비: [구체적 수치]% (고평가/적정/저평가) **[출처]**
    • [Interpretation Layer] 주가 평가 상태 해석: [구체적 분석] **[출처]**
    • [Peer Benchmark] 업계 평균 대비 주가 수준: [구체적 비교] **[출처]**
    • [Chain of Verification] 주가 평가의 신뢰도: [구체적 분석] **[출처]**

Q4: 주요 리스크와 기회 요인은 무엇인가?
  └─ Q4-1: 재무적/운영적 리스크는 무엇인가?
    • [Fact Layer] 부채 리스크: [구체적 내용과 수치] **[출처]**
    • [Fact Layer] 환율 리스크: [구체적 내용과 수치] **[출처]**
    • [Fact Layer] 원자재 가격 리스크: [구체적 내용과 수치] **[출처]**
    • [Interpretation Layer] 리스크 영향도 평가: [구체적 분석] **[출처]**
    • [Peer Benchmark] 업계 평균 대비 리스크 수준: [구체적 비교] **[출처]**
    • [Chain of Reasoning] 리스크가 기업 가치에 미치는 영향: [구체적 분석] **[출처]**
  └─ Q4-2: 산업 환경과 경쟁 구도 변화는?
    • [Fact Layer] 시장 점유율 변화: [구체적 추이] **[출처]**
    • [Fact Layer] 신규 진입자 위협: [구체적 내용] **[출처]**
    • [Fact Layer] 대체재 위협: [구체적 내용] **[출처]**
    • [Interpretation Layer] 경쟁 환경 변화 영향 평가: [구체적 분석] **[출처]**
    • [Peer Benchmark] 경쟁사 대비 경쟁력: [구체적 비교] **[출처]**
    • [Chain of Reasoning] 경쟁 환경 변화가 기업 가치에 미치는 영향: [구체적 분석] **[출처]**
  └─ Q4-3: 규제나 외부 환경 리스크는?
    • [Fact Layer] 정부 규제 변화: [구체적 내용] **[출처]**
    • [Fact Layer] 무역 분쟁 리스크: [구체적 내용] **[출처]**
    • [Fact Layer] ESG 규제 리스크: [구체적 내용] **[출처]**
    • [Interpretation Layer] 외부 리스크 영향도 평가: [구체적 분석] **[출처]**
    • [Peer Benchmark] 업계 평균 대비 외부 리스크 노출도: [구체적 비교] **[출처]**
    • [Chain of Reasoning] 외부 리스크가 기업 가치에 미치는 영향: [구체적 분석] **[출처]**

Q5: 섹터 특화 경쟁력과 차별화 요소는?
  └─ Q5-1: 기술력과 시장 경쟁력은?
    • [Fact Layer] R&D 투자 규모: [구체적 수치] **[출처]**
    • [Fact Layer] 특허 보유 현황: [구체적 내용] **[출처]**
    • [Fact Layer] 시장 점유율: [구체적 수치] **[출처]**
    • [Interpretation Layer] 기술 경쟁력 평가: [구체적 분석] **[출처]**
    • [Peer Benchmark] 경쟁사 대비 기술력: [구체적 비교] **[출처]**
    • [Chain of Reasoning] 기술력이 미래 성장에 미치는 영향: [구체적 분석] **[출처]**
  └─ Q5-2: 핵심 성장 동력과 차별화 요소는?
    • [Fact Layer] 핵심 사업 영역: [구체적 내용] **[출처]**
    • [Fact Layer] 차별화 요소: [구체적 내용] **[출처]**
    • [Fact Layer] 브랜드 가치: [구체적 수치] **[출처]**
    • [Interpretation Layer] 차별화 요소의 지속가능성: [구체적 분석] **[출처]**
    • [Peer Benchmark] 경쟁사 대비 차별화 요소: [구체적 비교] **[출처]**
    • [Chain of Reasoning] 차별화 요소가 기업 가치에 미치는 영향: [구체적 분석] **[출처]**
  └─ Q5-3: 운영 효율성과 전략적 우위는?
    • [Fact Layer] 운영 효율성 지표: [구체적 수치] **[출처]**
    • [Fact Layer] 비용 구조: [구체적 분석] **[출처]**
    • [Fact Layer] 전략적 파트너십: [구체적 내용] **[출처]**
    • [Interpretation Layer] 운영 우위 평가: [구체적 분석] **[출처]**
    • [Peer Benchmark] 경쟁사 대비 운영 효율성: [구체적 비교] **[출처]**
    • [Chain of Reasoning] 운영 우위가 수익성에 미치는 영향: [구체적 분석] **[출처]**
"""

    @staticmethod
    def _get_sector_analysis_guidance(sector, sector_manager) -> str:
        """섹터별 분석 가이드라인을 반환합니다."""
        return f"""
**🏭 {sector.name} 섹터 특화 분석 가이드**

이 기업은 {sector.name} 섹터에 속하며, 다음 섹터 특화 요소들을 고려하여 분석하세요:

- **섹터 특성**: {sector.description}
- **주요 경쟁사**: {', '.join(sector_manager.get_competitors(sector)) if sector_manager else '해당 섹터 주요 기업들'}
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
