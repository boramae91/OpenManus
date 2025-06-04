from enum import Enum
from typing import Dict, Optional

from pydantic import Field

from app.agent.base import BaseAgent
from app.llm import LLM
from app.logger import logger
from app.schema import AgentState


class StockType(Enum):
    """주식 유형 분류를 위한 열거형 클래스예요"""

    LOW_GROWTH = "저성장주"  # 성장률이 낮지만 안정적인 종목
    BLUE_CHIP = "우량주"  # 대기업, 안정적인 실적과 배당
    HIGH_GROWTH = "고성장주"  # 높은 성장률을 보이는 종목
    ASSET_STOCK = "자산주"  # 자산가치가 높은 종목
    TURNAROUND = "턴어라운드주"  # 실적 개선이 기대되는 종목
    CYCLICAL = "시이클주"  # 경기에 민감한 종목
    OTHER = "기타주"  # 위 분류에 해당하지 않는 종목


class StockClassifier(BaseAgent):
    """
    종목을 7가지 유형으로 분류해주는 전문 에이전트예요
    - 저성장주, 우량주, 고성장주, 자산주, 턴어라운드주, 시이클주, 기타주로 분류해요
    """

    name: str = "StockClassifier"
    description: str = "종목을 7가지 유형으로 분류하는 전문 에이전트"

    # 분류 시스템 프롬프트
    system_prompt: str = """
당신은 종목을 전문적으로 분류하는 금융 분석 전문가입니다.
주어진 종목의 정보를 바탕으로 다음 7가지 분류 중 하나로 정확하게 분류해주세요:

1. 저성장주 (Low Growth Stock)
   - 매출 성장률이 연평균 5% 미만
   - 안정적이지만 성장성이 제한적
   - 성숙한 업종의 기업들
   - 예: 전통적인 제조업, 공익기업

2. 우량주 (Blue Chip Stock)
   - 시가총액이 큰 대기업
   - 안정적인 실적과 꾸준한 배당
   - 업계 선도기업
   - 예: 삼성전자, LG전자, 현대자동차

3. 고성장주 (High Growth Stock)
   - 매출 성장률이 연평균 15% 이상
   - 혁신적인 기술이나 비즈니스 모델
   - 높은 성장 잠재력
   - 예: IT, 바이오, 신재생에너지

4. 자산주 (Asset Stock)
   - 주가 대비 자산가치가 높음
   - PBR이 1 미만이거나 낮은 수준
   - 부동산, 보유자산의 가치가 높음
   - 예: 건설업, 부동산업

5. 턴어라운드주 (Turnaround Stock)
   - 현재는 부진하지만 실적 개선이 예상
   - 구조조정이나 사업전환 진행 중
   - 경영개선 노력이 진행 중
   - 예: 구조조정 중인 기업들

6. 시이클주 (Cyclical Stock)
   - 경기 변동에 민감하게 반응
   - 원자재, 에너지, 화학 등
   - 경기 사이클에 따라 실적 변동
   - 예: 철강, 화학, 조선

7. 기타주 (Other Stock)
   - 위 분류에 명확히 해당하지 않는 종목
   - 특수한 사업모델이나 업종
   - 분류가 애매한 경우

분류 시 다음 요소들을 종합적으로 고려하세요:
- 매출 성장률 및 영업이익 성장률
- 시가총액 및 업계 지위
- PER, PBR 등 밸류에이션 지표
- 업종 특성 및 경기 민감도
- 배당수익률 및 배당 안정성
- 최근 실적 트렌드 및 전망
"""

    next_step_prompt: str = """
주어진 종목 정보를 바탕으로 다음 단계를 수행해주세요:

1. 종목의 기본 정보 파악 (업종, 시가총액, 주요 사업)
2. 재무 지표 분석 (성장률, PER, PBR, 배당수익률 등)
3. 업종 특성 및 경기 민감도 평가
4. 7가지 분류 기준에 따른 매칭
5. 최종 분류 결과 및 근거 제시

결과는 다음 형식으로 제시해주세요:
**분류 결과: [분류명]**
**근거:**
- 주요 근거 1
- 주요 근거 2
- 주요 근거 3
**신뢰도: [높음/보통/낮음]**
"""

    max_steps: int = 3

    # 분류 결과를 저장할 속성
    classification_result: Optional[Dict] = Field(default=None)

    async def step(self) -> str:
        """종목 분류 단계를 실행하는 함수예요"""

        # 1단계: 입력 검증 및 기본 정보 파악
        if self.current_step == 1:
            return await self._analyze_stock_info()

        # 2단계: 재무 지표 분석 및 분류 기준 적용
        elif self.current_step == 2:
            return await self._classify_stock()

        # 3단계: 최종 결과 정리 및 출력
        elif self.current_step == 3:
            result = await self._finalize_classification()
            self.state = AgentState.FINISHED
            return result

        return "분류 단계를 완료했습니다."

    async def _analyze_stock_info(self) -> str:
        """종목의 기본 정보를 분석하는 함수예요"""

        # 사용자 메시지에서 종목 정보 추출
        if not self.memory.messages:
            self.update_memory("system", "종목 정보를 입력해주세요.")
            return "종목 정보가 필요합니다. 종목명이나 종목코드를 입력해주세요."

        user_input = self.memory.messages[-1].content if self.memory.messages else ""

        analysis_prompt = f"""
다음 종목에 대한 기본 정보를 파악해주세요:
입력: {user_input}

다음 정보를 조사하고 정리해주세요:
1. 종목명 및 종목코드
2. 업종 분류
3. 시가총액 규모
4. 주요 사업 영역
5. 최근 3년간 매출 및 영업이익 추이
6. 주요 재무지표 (PER, PBR, ROE, 부채비율 등)

위 정보를 바탕으로 기본 분석을 완료해주세요.
"""

        self.update_memory("user", analysis_prompt)

        system_messages = [{"role": "system", "content": self.system_prompt}]
        response = await self.llm.ask(
            messages=self.memory.to_dict_list(), system_msgs=system_messages
        )

        self.update_memory("assistant", response)

        logger.info(f"종목 기본 정보 분석 완료: {user_input}")
        return f"종목 기본 정보 분석을 완료했습니다.\n\n{response}"

    async def _classify_stock(self) -> str:
        """종목을 7가지 유형으로 분류하는 함수예요"""

        classification_prompt = f"""
앞서 분석한 종목 정보를 바탕으로 다음 7가지 분류 중 하나로 정확하게 분류해주세요:

{self._get_classification_criteria()}

분류 시 다음 단계를 따라주세요:
1. 각 분류 기준별로 해당 종목이 얼마나 부합하는지 점수화 (1-5점)
2. 가장 높은 점수를 받은 분류를 선택
3. 선택한 분류의 근거를 명확히 제시
4. 분류의 신뢰도 평가 (높음/보통/낮음)

결과를 구조화된 형태로 제시해주세요.
"""

        self.update_memory("user", classification_prompt)

        system_messages = [{"role": "system", "content": self.system_prompt}]
        response = await self.llm.ask(
            messages=self.memory.to_dict_list(), system_msgs=system_messages
        )

        self.update_memory("assistant", response)

        # 분류 결과 파싱 및 저장
        self.classification_result = self._parse_classification_result(response)

        logger.info(f"종목 분류 완료: {self.classification_result}")
        return f"종목 분류를 완료했습니다.\n\n{response}"

    async def _finalize_classification(self) -> str:
        """최종 분류 결과를 정리하고 출력하는 함수예요"""

        if not self.classification_result:
            return "분류 결과를 생성할 수 없습니다."

        final_prompt = """
최종 분류 결과를 사용자가 이해하기 쉽게 요약해주세요.

다음 형식으로 정리해주세요:
=== 종목 분류 결과 ===
🏷️ **분류: [분류명]**
📊 **신뢰도: [신뢰도]**
📋 **주요 근거:**
• 근거 1
• 근거 2
• 근거 3

🔍 **투자 시 고려사항:**
• 고려사항 1
• 고려사항 2

💡 **추가 조언:**
이 분류에 해당하는 종목의 일반적인 투자 전략이나 주의사항을 간단히 설명해주세요.

결과를 명확하고 간결하게 정리해주세요.
"""

        self.update_memory("user", final_prompt)

        system_messages = [{"role": "system", "content": self.system_prompt}]
        response = await self.llm.ask(
            messages=self.memory.to_dict_list(), system_msgs=system_messages
        )

        self.update_memory("assistant", response)

        logger.info("종목 분류 최종 결과 생성 완료")
        return response

    def _get_classification_criteria(self) -> str:
        """분류 기준을 상세히 설명하는 함수예요"""

        criteria = """
1. 저성장주: 매출성장률 <5%, 안정적이지만 성장성 제한
2. 우량주: 대기업, 안정적 실적, 꾸준한 배당, 업계 리더
3. 고성장주: 매출성장률 >15%, 혁신기술, 높은 성장잠재력
4. 자산주: PBR <1, 자산가치 높음, 부동산/보유자산 중요
5. 턴어라운드주: 현재 부진하지만 실적개선 예상, 구조조정 중
6. 시이클주: 경기변동 민감, 원자재/에너지/화학 등
7. 기타주: 위 분류에 명확히 해당하지 않는 특수한 경우
"""
        return criteria

    def _parse_classification_result(self, response: str) -> Dict:
        """분류 결과를 파싱하여 구조화된 데이터로 변환하는 함수예요"""

        result = {
            "classification": "기타주",  # 기본값
            "confidence": "보통",  # 기본값
            "reasoning": [],
            "raw_response": response,
        }

        try:
            # 분류명 추출 - 우선순위 기반으로 정확하게 추출!
            classification = "기타주"  # 기본값

            # 1순위: "선택한 분류", "최종 분류" 등 명시적 결과 패턴 찾기
            final_patterns = [
                r"선택한 분류.*?[:：]\s*([^(\n]*?)(?:\s*\(|$)",
                r"최종 분류.*?[:：]\s*([^(\n]*?)(?:\s*\(|$)",
                r"분류 결과.*?[:：]\s*([^(\n]*?)(?:\s*\(|$)",
                r"\*\*분류.*?[:：]\s*([^(\n]*?)(?:\s*\(|\*\*|$)",
            ]

            for pattern in final_patterns:
                import re

                matches = re.findall(pattern, response, re.IGNORECASE)
                if matches:
                    candidate = matches[0].strip()
                    # 발견된 후보가 실제 분류명인지 확인
                    for stock_type in StockType:
                        if stock_type.value in candidate:
                            classification = stock_type.value
                            break
                    if classification != "기타주":
                        break

            # 2순위: 전체 텍스트에서 순서대로 찾기 (기존 방식)
            if classification == "기타주":
                for stock_type in StockType:
                    if stock_type.value in response:
                        classification = stock_type.value
                        break

            result["classification"] = classification

            # 신뢰도 추출 - 패턴 기반으로 정확하게
            confidence = "보통"  # 기본값
            confidence_patterns = [
                r"신뢰도.*?[:：]\s*(높음|보통|낮음)",
                r"\*\*신뢰도.*?[:：]\s*(높음|보통|낮음)",
                r"신뢰도 평가.*?[:：]\s*(높음|보통|낮음)",
            ]

            for pattern in confidence_patterns:
                matches = re.findall(pattern, response, re.IGNORECASE)
                if matches:
                    confidence = matches[0]
                    break

            result["confidence"] = confidence

            # 근거 추출 (• 또는 - 로 시작하는 줄들)
            lines = response.split("\n")
            reasoning = []
            for line in lines:
                line = line.strip()
                if line.startswith("•") or line.startswith("-") or line.startswith("*"):
                    reasoning.append(line)
            result["reasoning"] = reasoning

        except Exception as e:
            logger.warning(f"분류 결과 파싱 중 오류: {e}")

        return result

    async def classify_stock(self, stock_input: str) -> Dict:
        """
        외부에서 호출할 수 있는 메인 분류 함수예요
        - stock_input: 종목명, 종목코드, 또는 종목 정보
        - 반환값: 분류 결과 딕셔너리
        """

        # 메모리 초기화
        self.memory.messages = []
        self.current_step = 0
        self.state = AgentState.IDLE
        self.classification_result = None

        # 사용자 입력 추가
        self.update_memory("user", stock_input)

        # 에이전트 실행
        result = await self.run()

        return {
            "input": stock_input,
            "classification": self.classification_result,
            "full_analysis": result,
            "agent_state": self.state.value,
        }

    def get_classification_types(self) -> Dict[str, str]:
        """사용 가능한 분류 유형들을 반환하는 함수예요"""

        return {stock_type.name: stock_type.value for stock_type in StockType}

    def extract_stock_info_from_analysis(self, analysis_text: str) -> Dict:
        """
        분석 결과에서 종목명과 종목코드를 동적으로 추출하는 함수예요
        - analysis_text: AI 분석 결과 텍스트
        - 반환값: {"stock_name": "종목명", "stock_code": "종목코드", "found": True/False}
        """
        import re

        result = {
            "stock_name": None,
            "stock_code": None,
            "found": False,
            "extraction_method": "stock_classifier_dynamic",
        }

        try:
            # 패턴 1: "종목명: XXX" 형태
            name_patterns = [
                r"종목명\s*[:：]\s*([가-힣A-Za-z0-9\s&\.\-]+)",
                r"회사명\s*[:：]\s*([가-힣A-Za-z0-9\s&\.\-]+)",
                r"기업명\s*[:：]\s*([가-힣A-Za-z0-9\s&\.\-]+)",
            ]

            # 패턴 2: "종목코드: XXXXXX" 형태
            code_patterns = [
                r"종목코드\s*[:：]\s*([A-Z]?[0-9]{2,6})",
                r"코드\s*[:：]\s*([A-Z]?[0-9]{2,6})",
                r"티커\s*[:：]\s*([A-Z]{2,5})",
            ]

            # 종목명 추출
            for pattern in name_patterns:
                matches = re.findall(pattern, analysis_text, re.IGNORECASE)
                if matches:
                    candidate = matches[0].strip()
                    # 유효성 검증
                    if self._is_valid_stock_name(candidate):
                        result["stock_name"] = candidate
                        break

            # 종목코드 추출
            for pattern in code_patterns:
                matches = re.findall(pattern, analysis_text, re.IGNORECASE)
                if matches:
                    candidate = matches[0].strip()
                    # 유효성 검증
                    if self._is_valid_stock_code(candidate):
                        result["stock_code"] = candidate
                        break

            # 패턴 3: "종목명(종목코드)" 형태
            combined_pattern = (
                r"([가-힣A-Za-z0-9\s&\.\-]+)\s*\(\s*([A-Z]?[0-9]{2,6})\s*\)"
            )
            combined_matches = re.findall(
                combined_pattern, analysis_text, re.IGNORECASE
            )

            if combined_matches:
                for match in combined_matches:
                    name_candidate = match[0].strip()
                    code_candidate = match[1].strip()

                    if self._is_valid_stock_name(
                        name_candidate
                    ) and self._is_valid_stock_code(code_candidate):
                        result["stock_name"] = name_candidate
                        result["stock_code"] = code_candidate
                        break

            # 결과 검증
            if result["stock_name"] or result["stock_code"]:
                result["found"] = True
                logger.info(
                    f"✅ StockClassifier에서 종목 정보 추출 성공: {result['stock_name']} ({result['stock_code']})"
                )
            else:
                logger.warning("❌ StockClassifier에서 종목 정보를 찾지 못했습니다.")

        except Exception as e:
            logger.error(f"StockClassifier 종목 정보 추출 중 오류: {e}")

        return result

    def _is_valid_stock_name(self, name: str) -> bool:
        """종목명이 유효한지 검증하는 함수예요"""
        if not name or len(name.strip()) < 2:
            return False

        name = name.strip()

        # 제외할 일반적인 단어들
        exclude_words = {
            "분석",
            "종목",
            "기업",
            "정보",
            "결과",
            "전망",
            "투자",
            "주식",
            "시장",
            "Analysis",
            "Stock",
            "Company",
            "Market",
            "Info",
            "Result",
        }

        if name in exclude_words:
            return False

        # 길이 제한
        if len(name) < 2 or len(name) > 50:
            return False

        # 숫자만인 경우 제외
        if name.isdigit():
            return False

        return True

    def _is_valid_stock_code(self, code: str) -> bool:
        """종목코드가 유효한지 검증하는 함수예요"""
        if not code or len(code.strip()) < 2:
            return False

        code = code.strip()

        # 한국 종목코드 (6자리 숫자)
        if re.match(r"^\d{6}$", code):
            return True

        # 해외 티커 (2-5글자 알파벳)
        if re.match(r"^[A-Z]{2,5}$", code):
            return True

        return False
