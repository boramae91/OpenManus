# -*- coding: utf-8 -*-
"""
LangChain 웹 검색 도구

GICS 섹터별 전문가들이 실시간으로 웹 검색을 통해 최신 정보를 가져올 수 있는 도구에요!
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import requests
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.schema import BaseMessage, HumanMessage
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class LangChainWebSearchTool:
    """
    LangChain을 통한 실시간 웹 검색 도구

    GICS 섹터별 전문가들이 분석에 필요한 최신 정보를 실시간으로 검색할 수 있어요!
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        웹 검색 도구 초기화

        Args:
            api_key: OpenAI API 키 (환경변수에서 자동 로드)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.search_engines = {
            "google": self._search_google,
            "bing": self._search_bing,
            "duckduckgo": self._search_duckduckgo,
        }

        print("🔍 LangChain 웹 검색 도구 초기화 완료!")

    def __enter__(self):
        """동기 컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """동기 컨텍스트 매니저 종료"""
        if self.session:
            self.session.close()

    def search(
        self,
        query: str,
        engine: str = "google",
        max_results: int = 5,
        language: str = "ko",
    ) -> Dict[str, Any]:
        """
        웹 검색 수행

        Args:
            query: 검색 쿼리
            engine: 검색 엔진 (google, bing, duckduckgo)
            max_results: 최대 결과 수
            language: 검색 언어

        Returns:
            Dict: 검색 결과
        """
        try:
            logger.info(f"🔍 웹 검색 시작: {query} (엔진: {engine})")

            if engine not in self.search_engines:
                logger.warning(f"⚠️ 지원하지 않는 검색 엔진: {engine}, Google 사용")
                engine = "google"

            # 검색 수행
            search_func = self.search_engines[engine]
            results = search_func(query, max_results, language)

            logger.info(f"✅ 웹 검색 완료: {len(results.get('results', []))}개 결과")
            return results

        except Exception as e:
            logger.error(f"❌ 웹 검색 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "engine": engine,
                "results": [],
            }

    def _search_google(
        self, query: str, max_results: int = 5, language: str = "ko"
    ) -> Dict[str, Any]:
        """
        Google 검색 수행 (실제 구현)

        DuckDuckGo API를 사용하여 실제 검색을 수행해요!
        """
        try:
            encoded_query = quote_plus(query)

            # DuckDuckGo Instant Answer API 사용 (무료, API 키 불필요)
            search_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"

            if self.session:
                response = self.session.get(search_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()

                    results = []

                    # Abstract 결과 추가
                    if data.get("Abstract"):
                        results.append(
                            {
                                "title": data.get("AbstractText", f"{query} 검색 결과"),
                                "url": data.get(
                                    "AbstractURL",
                                    f"https://duckduckgo.com/?q={encoded_query}",
                                ),
                                "snippet": data.get(
                                    "Abstract", f"{query}에 대한 정보입니다."
                                ),
                                "source": "duckduckgo",
                            }
                        )

                    # Related Topics 추가
                    if data.get("RelatedTopics"):
                        for topic in data["RelatedTopics"][: max_results - 1]:
                            if isinstance(topic, dict) and topic.get("Text"):
                                results.append(
                                    {
                                        "title": (
                                            topic.get("Text", "").split(" - ")[0]
                                            if " - " in topic.get("Text", "")
                                            else topic.get("Text", "")
                                        ),
                                        "url": topic.get(
                                            "FirstURL",
                                            f"https://duckduckgo.com/?q={encoded_query}",
                                        ),
                                        "snippet": topic.get("Text", ""),
                                        "source": "duckduckgo",
                                    }
                                )

                    # 결과가 없으면 기본 결과 제공
                    if not results:
                        results = [
                            {
                                "title": f"{query} 검색 결과",
                                "url": f"https://duckduckgo.com/?q={encoded_query}",
                                "snippet": f"{query}에 대한 검색 결과입니다. 더 자세한 정보는 링크를 확인하세요.",
                                "source": "duckduckgo",
                            }
                        ]

                    return {
                        "success": True,
                        "query": query,
                        "engine": "duckduckgo",
                        "language": language,
                        "results": results[:max_results],
                        "total_results": len(results),
                        "search_url": f"https://duckduckgo.com/?q={encoded_query}",
                    }
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.reason}")
            else:
                raise Exception("HTTP 세션이 초기화되지 않았습니다.")

        except Exception as e:
            logger.error(f"❌ DuckDuckGo 검색 실패: {e}")
            # ❌ 검색 실패 - 명확한 오류 반환
            return {
                "success": False,
                "error": f"DuckDuckGo 검색에 실패했습니다: {str(e)}",
                "query": query,
                "engine": "duckduckgo",
                "language": language,
                "results": [],
                "recommendation": "검색 API 키 설정 또는 네트워크 연결을 확인하세요.",
                "required_action": "검색 API 키 설정 또는 네트워크 연결 확인 필요",
            }

    def _search_bing(
        self, query: str, max_results: int = 5, language: str = "ko"
    ) -> Dict[str, Any]:
        """
        Bing 검색 수행 (시뮬레이션)
        """
        try:
            encoded_query = quote_plus(query)

            simulated_results = [
                {
                    "title": f"{query} - Bing 검색 결과",
                    "url": f"https://www.bing.com/search?q={encoded_query}",
                    "snippet": f"{query}에 대한 Bing 검색 결과입니다.",
                    "source": "bing",
                }
            ]

            return {
                "success": True,
                "query": query,
                "engine": "bing",
                "language": language,
                "results": simulated_results[:max_results],
                "total_results": len(simulated_results),
                "search_url": f"https://www.bing.com/search?q={encoded_query}&setlang={language}",
            }

        except Exception as e:
            logger.error(f"❌ Bing 검색 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "engine": "bing",
                "results": [],
            }

    def _search_duckduckgo(
        self, query: str, max_results: int = 5, language: str = "ko"
    ) -> Dict[str, Any]:
        """
        DuckDuckGo 검색 수행 (시뮬레이션)
        """
        try:
            encoded_query = quote_plus(query)

            simulated_results = [
                {
                    "title": f"{query} - DuckDuckGo 검색 결과",
                    "url": f"https://duckduckgo.com/?q={encoded_query}",
                    "snippet": f"{query}에 대한 DuckDuckGo 검색 결과입니다.",
                    "source": "duckduckgo",
                }
            ]

            return {
                "success": True,
                "query": query,
                "engine": "duckduckgo",
                "language": language,
                "results": simulated_results[:max_results],
                "total_results": len(simulated_results),
                "search_url": f"https://duckduckgo.com/?q={encoded_query}&kl={language}",
            }

        except Exception as e:
            logger.error(f"❌ DuckDuckGo 검색 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "engine": "duckduckgo",
                "results": [],
            }

    def create_langchain_tool(self) -> Tool:
        """
        LangChain Tool 생성 (동기 버전)

        Returns:
            Tool: LangChain에서 사용할 수 있는 웹 검색 도구
        """

        def web_search_tool(query: str) -> str:
            """
            LangChain에서 사용할 웹 검색 도구 (동기 버전)

            Args:
                query: 검색 쿼리

            Returns:
                str: 검색 결과 문자열
            """
            try:
                # 동기적으로 웹 검색 수행
                result = self.search(query, max_results=3)

                if result.get("success"):
                    results = result.get("results", [])
                    formatted_results = []

                    for i, item in enumerate(results, 1):
                        formatted_results.append(
                            f"{i}. {item['title']}\n"
                            f"   URL: {item['url']}\n"
                            f"   내용: {item['snippet']}\n"
                        )

                    return f"🔍 검색 결과 ({result['engine']}):\n\n" + "\n".join(
                        formatted_results
                    )
                else:
                    return f"❌ 검색 실패: {result.get('error', '알 수 없는 오류')}"

            except Exception as e:
                return f"❌ 웹 검색 도구 오류: {str(e)}"

        return Tool(
            name="web_search",
            description="실시간 웹 검색을 통해 최신 정보를 가져옵니다. 경쟁사 정보, 업계 동향, 최신 뉴스 등을 검색할 때 사용하세요.",
            func=web_search_tool,
        )

    async def search_financial_data(
        self, company_name: str, data_type: str = "financial_ratios"
    ) -> Dict[str, Any]:
        """
        재무 데이터 검색 (전문가용)

        Args:
            company_name: 회사명
            data_type: 검색할 데이터 타입 (financial_ratios, market_share, etc.)

        Returns:
            Dict: 검색된 재무 데이터
        """
        try:
            # 데이터 타입별 검색 쿼리 구성
            search_queries = {
                "financial_ratios": f"{company_name} 재무비율 ROE ROA ROIC 2024",
                "market_share": f"{company_name} 시장점유율 2024 업계 순위",
                "competitors": f"{company_name} 경쟁사 재무비율 비교 2024",
                "analyst_consensus": f"{company_name} 애널리스트 목표가 컨센서스 2024",
                "industry_average": f"{company_name} 업계 평균 PER PBR EV/EBITDA 2024",
                "beta": f"{company_name} 베타 계수 2024",
                "latest_news": f"{company_name} 최신 뉴스 실적 발표 2024",
            }

            query = search_queries.get(data_type, f"{company_name} {data_type} 2024")

            # 검색 수행
            result = await self.search(query, max_results=5)

            return {
                "success": result.get("success", False),
                "data_type": data_type,
                "company_name": company_name,
                "search_query": query,
                "results": result.get("results", []),
                "formatted_data": self._format_financial_search_results(
                    result, data_type
                ),
            }

        except Exception as e:
            logger.error(f"❌ 재무 데이터 검색 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "data_type": data_type,
                "company_name": company_name,
                "results": [],
            }

    def _format_financial_search_results(
        self, search_result: Dict[str, Any], data_type: str
    ) -> str:
        """
        재무 검색 결과를 포맷팅

        Args:
            search_result: 검색 결과
            data_type: 데이터 타입

        Returns:
            str: 포맷팅된 결과
        """
        if not search_result.get("success"):
            return f"❌ 검색 실패: {search_result.get('error', '알 수 없는 오류')}"

        results = search_result.get("results", [])
        if not results:
            return "📭 검색 결과가 없습니다."

        formatted = f"🔍 {data_type} 검색 결과:\n\n"

        for i, item in enumerate(results, 1):
            formatted += f"{i}. {item['title']}\n"
            formatted += f"   📄 {item['snippet']}\n"
            formatted += f"   🔗 {item['url']}\n\n"

        return formatted


# 🚀 LangChain Agent에 웹 검색 도구를 통합하는 클래스
class LangChainWebSearchAgent:
    """
    LangChain Agent에 웹 검색 도구를 통합하는 클래스

    GICS 섹터별 전문가들이 웹 검색을 통해 실시간 정보를 가져올 수 있어요!
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        웹 검색 Agent 초기화

        Args:
            api_key: OpenAI API 키
        """
        self.api_key = api_key
        self.web_search_tool = LangChainWebSearchTool(api_key)
        self.llm = ChatOpenAI(
            model="gpt-4o", temperature=0.1, max_tokens=8000
        )  # 2명 체제에 맞게 증가

        print("🤖 LangChain 웹 검색 Agent 초기화 완료!")

    async def create_agent_with_web_search(
        self, system_prompt: str, tools: List[Tool] = None
    ) -> AgentExecutor:
        """
        웹 검색 도구가 포함된 LangChain Agent 생성

        Args:
            system_prompt: 시스템 프롬프트
            tools: 추가 도구들

        Returns:
            AgentExecutor: 웹 검색 도구가 포함된 Agent
        """
        try:
            # 기본 도구 목록 (웹 검색 포함)
            base_tools = [self.web_search_tool.create_langchain_tool()]

            # 추가 도구가 있으면 추가
            if tools:
                base_tools.extend(tools)

            # Agent 생성
            agent = create_openai_functions_agent(
                llm=self.llm, tools=base_tools, prompt=system_prompt
            )

            # Agent Executor 생성
            agent_executor = AgentExecutor(
                agent=agent, tools=base_tools, verbose=True, max_iterations=5
            )

            print("✅ 웹 검색 도구가 포함된 LangChain Agent 생성 완료!")
            return agent_executor

        except Exception as e:
            logger.error(f"❌ Agent 생성 실패: {e}")
            raise

    async def search_and_analyze(
        self, query: str, analysis_prompt: str
    ) -> Dict[str, Any]:
        """
        웹 검색 후 분석 수행

        Args:
            query: 검색 쿼리
            analysis_prompt: 분석 프롬프트

        Returns:
            Dict: 검색 및 분석 결과
        """
        try:
            # 웹 검색 수행
            search_result = await self.web_search_tool.search(query)

            if not search_result.get("success"):
                return {
                    "success": False,
                    "error": "웹 검색 실패",
                    "search_result": search_result,
                }

            # 검색 결과를 분석 프롬프트에 포함
            search_data = self.web_search_tool._format_financial_search_results(
                search_result, "general"
            )

            full_prompt = f"""
{analysis_prompt}

**웹 검색 결과:**
{search_data}

위의 웹 검색 결과를 바탕으로 분석을 수행하세요.
"""

            # LLM을 통한 분석 수행
            messages = [HumanMessage(content=full_prompt)]
            analysis_result = await self.llm.ainvoke(messages)

            return {
                "success": True,
                "search_result": search_result,
                "analysis_result": analysis_result.content,
                "full_prompt": full_prompt,
            }

        except Exception as e:
            logger.error(f"❌ 검색 및 분석 실패: {e}")
            return {"success": False, "error": str(e), "query": query}


# 🚀 사용 예시
async def main():
    """사용 예시"""
    async with LangChainWebSearchTool() as search_tool:
        # 기본 검색
        result = await search_tool.search("삼성전자 재무비율 2024")
        print(json.dumps(result, ensure_ascii=False, indent=2))

        # 재무 데이터 검색
        financial_result = await search_tool.search_financial_data(
            "삼성전자", "financial_ratios"
        )
        print(json.dumps(financial_result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
