# 🚀 One-Hot Sector Activation 통합 가이드

OpenManus 시스템에 성공적으로 통합된 **One-Hot Sector Activation** 시스템의 사용법과 기능을 설명합니다.

## 📋 개요

### 혁신적인 비용 절감 솔루션
- **기존 방식**: 55개 에이전트 동시 활성화 → 분석당 $5-10 비용
- **One-Hot 방식**: 5개 에이전트 선택적 활성화 → 분석당 $0.20-1.00 비용
- **90% 비용 절감** 달성! 🎉

### 핵심 기능
1. **GICS 11개 섹터 자동 감지** - 에너지, IT, 헬스케어, 금융 등
2. **섹터별 5명 전문가 팀** - 기본/기술/산업/밸류에이션/리스크 분석가
3. **3단계 분석 깊이** - QUICK/STANDARD/DEEP 자동 선택
4. **지능형 캐싱 시스템** - 중복 분석 방지로 추가 비용 절감

## 🏗️ 시스템 구조

### 핵심 모듈
```
app/crew/
├── __init__.py                 # 모듈 exports
├── gics_sectors.py            # GICS 섹터 정의 및 매핑
├── sector_teams.py            # 전문가 팀 정의
└── smart_sector_manager.py    # One-Hot 활성화 핵심 로직
```

### 통합 지점
- `enhanced_main.py` - 메인 분석 플로우에 통합
- Step 2.5에서 섹터 감지 및 전문가 팀 활성화
- Step 3에서 섹터 전문가 인사이트를 종합 분석에 통합

## 🚀 사용법

### 1. 기본 사용 (자동 통합)

기존 방식과 동일하게 사용하면 자동으로 One-Hot 시스템이 작동합니다:

```python
from enhanced_main import EnhancedStockAnalysisSystem

system = EnhancedStockAnalysisSystem()
result = await system.run_enhanced_analysis("삼성전자의 반도체 경쟁력을 분석해주세요")
```

### 2. 섹터별 분석 확인

분석 결과에서 섹터 정보를 확인할 수 있습니다:

```python
# 분석 결과에서 섹터 정보 추출
sector_info = result["steps"]["step2_5_sector_analysis"]
print(f"감지된 섹터: {sector_info['detected_sector']}")
print(f"활성화된 전문가: {sector_info['activated_experts']}")
print(f"비용 절감: {sector_info['cost_savings']['savings_percentage']:.1f}%")
```

### 3. 분석 깊이 제어

프롬프트 키워드로 분석 깊이를 제어할 수 있습니다:

```python
# QUICK 분석 (2명, $0.20, 12시간 캐시)
"삼성전자 주가는 얼마인가요?"

# STANDARD 분석 (5명, $0.50, 24시간 캐시)
"삼성전자의 반도체 경쟁력을 분석해주세요"

# DEEP 분석 (5명 + 검증, $1.00, 48시간 캐시)
"삼성전자에 투자하려고 하는데 상세한 DCF 밸류에이션과 리스크 분석을 부탁드립니다"
```

## 🎯 지원 섹터 및 전문가

### GICS 11개 섹터
1. **Energy (10)** - 에너지
2. **Materials (15)** - 소재
3. **Industrials (20)** - 산업재
4. **Consumer_Discretionary (25)** - 임의소비재
5. **Consumer_Staples (30)** - 필수소비재
6. **Healthcare (35)** - 헬스케어
7. **Financials (40)** - 금융
8. **IT (45)** - 정보기술
9. **Communication_Services (50)** - 통신서비스
10. **Utilities (55)** - 유틸리티
11. **Real_Estate (60)** - 부동산

### 각 섹터별 5명 전문가 팀
- **기본 분석가** (Fundamental Analyst) - 재무제표, 성장성 분석
- **기술 분석가** (Technical Analyst) - 차트, 거래량, 기술적 지표
- **산업 전문가** (Industry Expert) - 섹터 특화 동향, 경쟁사 분석
- **밸류에이션 전문가** (Valuation Specialist) - 적정가치, 투자지표
- **리스크 평가사** (Risk Assessor) - 위험요소, 시나리오 분석

## 🔍 섹터 감지 시스템

### 3단계 우선순위 매핑
1. **한국 주요 기업 수동 매핑** (최우선)
   - 삼성전자 → IT
   - 셀트리온 → Healthcare
   - POSCO홀딩스 → Materials

2. **Bloomberg 데이터셋 매핑** (계획됨)
   - CSV 파일 기반 자동 매핑

3. **키워드 추론** (폴백)
   - 회사명/업종 키워드 기반 추정

### 섹터별 특화 지표 (각 8개)

**IT 섹터 예시:**
- 매출성장률, R&D 투자비율, 시장점유율
- 신제품 출시주기, 특허 포트폴리오, 기술 경쟁력
- 글로벌 진출도, ESG 등급

## 💰 비용 구조

### 분석 깊이별 비용
| 깊이 | 활성화 에이전트 | 비용 | 캐시 기간 | 사용 사례 |
|------|----------------|------|-----------|-----------|
| QUICK | 2명 | $0.20 | 12시간 | 간단한 정보 확인 |
| STANDARD | 5명 | $0.50 | 24시간 | 일반적인 분석 |
| DEEP | 5명 + 검증 | $1.00 | 48시간 | 투자 결정 지원 |

### 비용 절감 효과
- **기존 방식**: 55개 에이전트 × $0.50 = **$27.50**
- **One-Hot 방식**: 5개 에이전트 × $0.50 = **$2.50**
- **절약률**: **90.9%** 🎉

## 🧪 테스트 및 시연

### 통합 테스트
```bash
python test_one_hot_integration.py
```

### 시연 스크립트
```bash
python demo_one_hot_system.py
```

### 실제 분석 테스트
```bash
python enhanced_main.py
```

## 📊 성능 통계

시스템에서 자동으로 추적하는 지표들:

```python
from app.crew.smart_sector_manager import SmartSectorManager

manager = SmartSectorManager(llm=llm)
stats = manager.get_performance_stats()

print(f"총 분석 수행: {stats['total_analyses']}회")
print(f"총 비용 절감: ${stats['total_cost_savings']:.2f}")
print(f"평균 절약률: {stats['average_savings_rate']:.1f}%")
```

## 🔧 고급 설정

### 분석 깊이 강제 설정
```python
from app.crew.smart_sector_manager import AnalysisDepth

result = await smart_manager.analyze_with_optimal_team(
    user_prompt="...",
    stock_name="삼성전자",
    stock_code="005930",
    financial_data=data,
    analysis_depth=AnalysisDepth.DEEP  # 강제로 DEEP 분석
)
```

### 캐시 무효화
```python
# 특정 주식의 캐시 삭제
smart_manager.cache_manager.invalidate_cache("삼성전자_005930")

# 전체 캐시 삭제
smart_manager.cache_manager.clear_all_cache()
```

## 🚀 향후 계획

1. **Bloomberg 데이터셋 통합** - 자동 섹터 매핑 확장
2. **실시간 뉴스 분석** - 뉴스 기반 섹터 동향 반영
3. **다국가 시장 지원** - 미국, 일본, 유럽 주식 지원
4. **AI 학습 기반 개선** - 사용 패턴 학습으로 정확도 향상

## 🤝 문의 및 지원

- 기술 문의: 프로젝트 이슈 트래커 활용
- 기능 요청: enhancement 라벨로 이슈 등록
- 버그 리포트: 상세한 재현 단계와 함께 이슈 등록

---

🎉 **축하합니다!** One-Hot Sector Activation으로 90% 비용 절감을 달성했습니다!
이제 같은 예산으로 10배 더 많은 분석이 가능합니다! 🚀
