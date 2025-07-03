#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 성능 모니터링 시스템

이 모듈은 OpenManus 시스템의 성능을 실시간으로 모니터링하고 분석하는 도구입니다.
마치 자동차의 대시보드처럼 시스템이 얼마나 빠르고 효율적으로 작동하는지 보여줘요!

주요 기능:
1. 🕐 분석 속도 측정 - 각 단계별 소요 시간 추적
2. 💾 메모리 사용량 모니터링 - RAM 사용량 실시간 추적
3. 💰 API 호출 비용 추적 - OpenAI API 사용량 및 비용 계산
4. 📈 성능 지표 시각화 - 차트와 그래프로 성능 표시
5. ⚠️ 성능 경고 시스템 - 임계값 초과 시 알림

사용법:
- PerformanceMonitor() 인스턴스 생성
- start_monitoring()으로 모니터링 시작
- stop_monitoring()으로 모니터링 종료
- get_performance_report()로 성능 리포트 생성
"""

import json
import logging
import os
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """
    성능 지표 데이터 클래스

    각 분석 단계별 성능 정보를 저장하는 상자예요.
    마치 운동할 때 심박수, 속도, 거리를 측정하는 것처럼요!
    """

    # 기본 정보
    analysis_id: str
    start_time: datetime
    end_time: Optional[datetime] = None

    # 시간 지표
    total_duration: float = 0.0  # 총 소요 시간 (초)
    step_durations: Dict[str, float] = None  # 각 단계별 소요 시간

    # 메모리 지표
    peak_memory_mb: float = 0.0  # 최대 메모리 사용량 (MB)
    average_memory_mb: float = 0.0  # 평균 메모리 사용량 (MB)
    memory_samples: List[float] = None  # 메모리 사용량 샘플들

    # API 호출 지표
    api_calls: int = 0  # API 호출 횟수
    api_tokens_used: int = 0  # 사용된 토큰 수
    estimated_cost_usd: float = 0.0  # 예상 비용 (USD)

    # 성능 점수
    performance_score: float = 0.0  # 종합 성능 점수 (0-100)

    def __post_init__(self):
        """데이터 초기화"""
        if self.step_durations is None:
            self.step_durations = {}
        if self.memory_samples is None:
            self.memory_samples = []


class PerformanceMonitor:
    """
    성능 모니터링 클래스

    시스템의 성능을 실시간으로 추적하고 분석하는 매니저 역할을 해요.
    마치 공장의 품질 관리 담당자가 생산라인의 효율성을 모니터링하는 것처럼요!
    """

    def __init__(self, max_history: int = 100):
        """
        성능 모니터 초기화

        Args:
            max_history: 저장할 최대 분석 기록 수 (기본값: 100개)
        """
        self.max_history = max_history
        self.current_analysis: Optional[PerformanceMetrics] = None
        self.analysis_history: deque = deque(maxlen=max_history)
        self.monitoring_active = False
        self.memory_monitor_thread: Optional[threading.Thread] = None

        # 성능 임계값 설정 (경고 기준)
        self.thresholds = {
            "max_duration_seconds": 300,  # 5분
            "max_memory_mb": 2048,  # 2GB
            "max_api_calls": 50,
            "max_cost_usd": 1.0,  # $1
        }

        # 성능 통계
        self.performance_stats = {
            "total_analyses": 0,
            "average_duration": 0.0,
            "average_memory": 0.0,
            "total_api_calls": 0,
            "total_cost": 0.0,
        }

        logger.info("📊 성능 모니터링 시스템 초기화 완료")

    def start_monitoring(self, analysis_id: str) -> str:
        """
        성능 모니터링 시작

        Args:
            analysis_id: 분석 고유 ID

        Returns:
            str: 모니터링 세션 ID
        """
        if self.monitoring_active:
            logger.warning("⚠️ 이미 모니터링이 진행 중입니다.")
            return self.current_analysis.analysis_id if self.current_analysis else ""

        # 새로운 분석 메트릭 생성
        self.current_analysis = PerformanceMetrics(
            analysis_id=analysis_id, start_time=datetime.now()
        )

        # 메모리 모니터링 스레드 시작
        self.monitoring_active = True
        self.memory_monitor_thread = threading.Thread(
            target=self._monitor_memory_usage, daemon=True
        )
        self.memory_monitor_thread.start()

        logger.info(f"📊 성능 모니터링 시작: {analysis_id}")
        return analysis_id

    def stop_monitoring(self) -> Optional[PerformanceMetrics]:
        """
        성능 모니터링 종료

        Returns:
            PerformanceMetrics: 완료된 분석 성능 데이터
        """
        if not self.monitoring_active or not self.current_analysis:
            logger.warning("⚠️ 모니터링이 진행 중이 아닙니다.")
            return None

        # 모니터링 중지
        self.monitoring_active = False
        if self.memory_monitor_thread:
            self.memory_monitor_thread.join(timeout=1.0)

        # 분석 완료 시간 설정
        self.current_analysis.end_time = datetime.now()
        self.current_analysis.total_duration = (
            self.current_analysis.end_time - self.current_analysis.start_time
        ).total_seconds()

        # 평균 메모리 사용량 계산
        if self.current_analysis.memory_samples:
            self.current_analysis.average_memory_mb = sum(
                self.current_analysis.memory_samples
            ) / len(self.current_analysis.memory_samples)
            self.current_analysis.peak_memory_mb = max(
                self.current_analysis.memory_samples
            )

        # 성능 점수 계산
        self.current_analysis.performance_score = self._calculate_performance_score()

        # 히스토리에 추가
        self.analysis_history.append(self.current_analysis)

        # 통계 업데이트
        self._update_performance_stats()

        # 성능 경고 체크
        self._check_performance_warnings()

        completed_analysis = self.current_analysis
        self.current_analysis = None

        logger.info(f"📊 성능 모니터링 종료: {completed_analysis.analysis_id}")
        logger.info(f"   소요시간: {completed_analysis.total_duration:.2f}초")
        logger.info(f"   메모리: {completed_analysis.peak_memory_mb:.1f}MB")
        logger.info(f"   API호출: {completed_analysis.api_calls}회")

        return completed_analysis

    def record_step_duration(self, step_name: str, duration: float):
        """
        단계별 소요 시간 기록

        Args:
            step_name: 단계 이름 (예: "종목감지", "재무데이터수집", "전문가분석")
            duration: 소요 시간 (초)
        """
        if self.current_analysis:
            self.current_analysis.step_durations[step_name] = duration
            logger.debug(f"📊 단계 기록: {step_name} - {duration:.2f}초")

    def record_api_call(self, tokens_used: int, estimated_cost: float = 0.0):
        """
        API 호출 정보 기록

        Args:
            tokens_used: 사용된 토큰 수
            estimated_cost: 예상 비용 (USD)
        """
        if self.current_analysis:
            self.current_analysis.api_calls += 1
            self.current_analysis.api_tokens_used += tokens_used
            self.current_analysis.estimated_cost_usd += estimated_cost
            logger.debug(f"📊 API 호출 기록: {tokens_used} 토큰, ${estimated_cost:.4f}")

    def _monitor_memory_usage(self):
        """메모리 사용량 실시간 모니터링 (백그라운드 스레드)"""
        while self.monitoring_active:
            try:
                # 현재 프로세스의 메모리 사용량 측정
                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / 1024 / 1024  # MB로 변환

                if self.current_analysis:
                    self.current_analysis.memory_samples.append(memory_mb)

                time.sleep(0.5)  # 0.5초마다 측정

            except Exception as e:
                logger.error(f"❌ 메모리 모니터링 오류: {e}")
                break

    def _calculate_performance_score(self) -> float:
        """성능 점수 계산 (0-100점)"""
        if not self.current_analysis:
            return 0.0

        score = 100.0

        # 시간 점수 (빠를수록 높은 점수)
        if (
            self.current_analysis.total_duration
            > self.thresholds["max_duration_seconds"]
        ):
            time_penalty = (
                (
                    self.current_analysis.total_duration
                    - self.thresholds["max_duration_seconds"]
                )
                / 60
                * 10
            )
            score -= min(time_penalty, 30)

        # 메모리 점수 (적을수록 높은 점수)
        if self.current_analysis.peak_memory_mb > self.thresholds["max_memory_mb"]:
            memory_penalty = (
                (
                    self.current_analysis.peak_memory_mb
                    - self.thresholds["max_memory_mb"]
                )
                / 100
                * 5
            )
            score -= min(memory_penalty, 20)

        # API 호출 점수 (적을수록 높은 점수)
        if self.current_analysis.api_calls > self.thresholds["max_api_calls"]:
            api_penalty = (
                self.current_analysis.api_calls - self.thresholds["max_api_calls"]
            ) * 2
            score -= min(api_penalty, 20)

        # 비용 점수 (적을수록 높은 점수)
        if self.current_analysis.estimated_cost_usd > self.thresholds["max_cost_usd"]:
            cost_penalty = (
                self.current_analysis.estimated_cost_usd
                - self.thresholds["max_cost_usd"]
            ) * 50
            score -= min(cost_penalty, 30)

        return max(0.0, score)

    def _update_performance_stats(self):
        """성능 통계 업데이트"""
        if not self.current_analysis:
            return

        self.performance_stats["total_analyses"] += 1

        # 평균 계산
        total_analyses = self.performance_stats["total_analyses"]
        current_avg_duration = self.performance_stats["average_duration"]
        current_avg_memory = self.performance_stats["average_memory"]

        # 이동 평균 업데이트
        self.performance_stats["average_duration"] = (
            current_avg_duration * (total_analyses - 1)
            + self.current_analysis.total_duration
        ) / total_analyses
        self.performance_stats["average_memory"] = (
            current_avg_memory * (total_analyses - 1)
            + self.current_analysis.average_memory_mb
        ) / total_analyses

        # 누적 통계
        self.performance_stats["total_api_calls"] += self.current_analysis.api_calls
        self.performance_stats["total_cost"] += self.current_analysis.estimated_cost_usd

    def _check_performance_warnings(self):
        """성능 경고 체크"""
        if not self.current_analysis:
            return

        warnings = []

        if (
            self.current_analysis.total_duration
            > self.thresholds["max_duration_seconds"]
        ):
            warnings.append(
                f"⚠️ 분석 시간이 {self.thresholds['max_duration_seconds']}초를 초과했습니다: {self.current_analysis.total_duration:.1f}초"
            )

        if self.current_analysis.peak_memory_mb > self.thresholds["max_memory_mb"]:
            warnings.append(
                f"⚠️ 메모리 사용량이 {self.thresholds['max_memory_mb']}MB를 초과했습니다: {self.current_analysis.peak_memory_mb:.1f}MB"
            )

        if self.current_analysis.api_calls > self.thresholds["max_api_calls"]:
            warnings.append(
                f"⚠️ API 호출 횟수가 {self.thresholds['max_api_calls']}회를 초과했습니다: {self.current_analysis.api_calls}회"
            )

        if self.current_analysis.estimated_cost_usd > self.thresholds["max_cost_usd"]:
            warnings.append(
                f"⚠️ 예상 비용이 ${self.thresholds['max_cost_usd']}를 초과했습니다: ${self.current_analysis.estimated_cost_usd:.4f}"
            )

        for warning in warnings:
            logger.warning(warning)

    def get_performance_report(
        self, analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        성능 리포트 생성

        Args:
            analysis_id: 특정 분석 ID (None이면 전체 통계)

        Returns:
            Dict: 성능 리포트 데이터
        """
        if analysis_id:
            # 특정 분석 리포트
            for analysis in self.analysis_history:
                if analysis.analysis_id == analysis_id:
                    return self._create_analysis_report(analysis)
            return {"error": "분석을 찾을 수 없습니다."}
        else:
            # 전체 통계 리포트
            return self._create_overall_report()

    def _create_analysis_report(self, analysis: PerformanceMetrics) -> Dict[str, Any]:
        """개별 분석 리포트 생성"""
        return {
            "analysis_id": analysis.analysis_id,
            "start_time": analysis.start_time.isoformat(),
            "end_time": analysis.end_time.isoformat() if analysis.end_time else None,
            "total_duration_seconds": analysis.total_duration,
            "step_durations": analysis.step_durations,
            "memory_usage": {
                "peak_mb": analysis.peak_memory_mb,
                "average_mb": analysis.average_memory_mb,
                "samples_count": len(analysis.memory_samples),
            },
            "api_usage": {
                "calls": analysis.api_calls,
                "tokens": analysis.api_tokens_used,
                "estimated_cost_usd": analysis.estimated_cost_usd,
            },
            "performance_score": analysis.performance_score,
            "performance_grade": self._get_performance_grade(
                analysis.performance_score
            ),
        }

    def _create_overall_report(self) -> Dict[str, Any]:
        """전체 성능 통계 리포트 생성"""
        if not self.analysis_history:
            return {"message": "아직 분석 기록이 없습니다."}

        # 최근 10개 분석의 평균 계산
        recent_analyses = list(self.analysis_history)[-10:]

        recent_durations = [a.total_duration for a in recent_analyses]
        recent_memories = [a.peak_memory_mb for a in recent_analyses]
        recent_scores = [a.performance_score for a in recent_analyses]

        return {
            "summary": {
                "total_analyses": self.performance_stats["total_analyses"],
                "average_duration_seconds": self.performance_stats["average_duration"],
                "average_memory_mb": self.performance_stats["average_memory"],
                "total_api_calls": self.performance_stats["total_api_calls"],
                "total_cost_usd": self.performance_stats["total_cost"],
            },
            "recent_performance": {
                "average_duration_seconds": sum(recent_durations)
                / len(recent_durations),
                "average_memory_mb": sum(recent_memories) / len(recent_memories),
                "average_performance_score": sum(recent_scores) / len(recent_scores),
            },
            "thresholds": self.thresholds,
            "performance_trend": self._analyze_performance_trend(),
        }

    def _get_performance_grade(self, score: float) -> str:
        """성능 점수를 등급으로 변환"""
        if score >= 90:
            return "A+ (우수)"
        elif score >= 80:
            return "A (양호)"
        elif score >= 70:
            return "B+ (보통)"
        elif score >= 60:
            return "B (미흡)"
        else:
            return "C (불량)"

    def _analyze_performance_trend(self) -> Dict[str, Any]:
        """성능 트렌드 분석"""
        if len(self.analysis_history) < 5:
            return {"message": "트렌드 분석을 위한 충분한 데이터가 없습니다."}

        # 최근 5개와 이전 5개 비교
        recent = list(self.analysis_history)[-5:]
        previous = (
            list(self.analysis_history)[-10:-5]
            if len(self.analysis_history) >= 10
            else []
        )

        recent_avg_duration = sum(a.total_duration for a in recent) / len(recent)
        recent_avg_memory = sum(a.peak_memory_mb for a in recent) / len(recent)

        trend_analysis = {
            "recent_average_duration": recent_avg_duration,
            "recent_average_memory": recent_avg_memory,
        }

        if previous:
            previous_avg_duration = sum(a.total_duration for a in previous) / len(
                previous
            )
            previous_avg_memory = sum(a.peak_memory_mb for a in previous) / len(
                previous
            )

            duration_change = (
                (recent_avg_duration - previous_avg_duration) / previous_avg_duration
            ) * 100
            memory_change = (
                (recent_avg_memory - previous_avg_memory) / previous_avg_memory
            ) * 100

            trend_analysis.update(
                {
                    "duration_trend": f"{duration_change:+.1f}%",
                    "memory_trend": f"{memory_change:+.1f}%",
                    "trend_interpretation": self._interpret_trend(
                        duration_change, memory_change
                    ),
                }
            )

        return trend_analysis

    def _interpret_trend(self, duration_change: float, memory_change: float) -> str:
        """트렌드 해석"""
        if duration_change < -10 and memory_change < -10:
            return "🚀 성능이 크게 개선되었습니다!"
        elif duration_change < -5 and memory_change < -5:
            return "📈 성능이 개선되었습니다."
        elif duration_change > 10 and memory_change > 10:
            return "⚠️ 성능이 저하되었습니다. 최적화가 필요합니다."
        elif duration_change > 5 and memory_change > 5:
            return "📉 성능이 약간 저하되었습니다."
        else:
            return "➡️ 성능이 안정적으로 유지되고 있습니다."

    def save_performance_data(self, filepath: str):
        """
        성능 데이터를 JSON 파일로 저장

        Args:
            filepath: 저장할 파일 경로
        """
        try:
            data = {
                "performance_stats": self.performance_stats,
                "thresholds": self.thresholds,
                "analysis_history": [
                    asdict(analysis) for analysis in self.analysis_history
                ],
            }

            # datetime 객체를 문자열로 변환
            for analysis in data["analysis_history"]:
                analysis["start_time"] = analysis["start_time"].isoformat()
                if analysis["end_time"]:
                    analysis["end_time"] = analysis["end_time"].isoformat()

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"📊 성능 데이터 저장 완료: {filepath}")

        except Exception as e:
            logger.error(f"❌ 성능 데이터 저장 실패: {e}")

    def load_performance_data(self, filepath: str):
        """
        JSON 파일에서 성능 데이터 로드

        Args:
            filepath: 로드할 파일 경로
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.performance_stats = data.get(
                "performance_stats", self.performance_stats
            )
            self.thresholds = data.get("thresholds", self.thresholds)

            # 분석 히스토리 복원
            self.analysis_history.clear()
            for analysis_data in data.get("analysis_history", []):
                # 문자열을 datetime 객체로 변환
                analysis_data["start_time"] = datetime.fromisoformat(
                    analysis_data["start_time"]
                )
                if analysis_data["end_time"]:
                    analysis_data["end_time"] = datetime.fromisoformat(
                        analysis_data["end_time"]
                    )

                analysis = PerformanceMetrics(**analysis_data)
                self.analysis_history.append(analysis)

            logger.info(f"📊 성능 데이터 로드 완료: {filepath}")

        except Exception as e:
            logger.error(f"❌ 성능 데이터 로드 실패: {e}")


# 전역 성능 모니터 인스턴스
performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """
    전역 성능 모니터 인스턴스 반환

    Returns:
        PerformanceMonitor: 전역 성능 모니터 인스턴스
    """
    return performance_monitor


# 성능 측정 데코레이터
def monitor_performance(step_name: str = None):
    """
    함수 성능 측정 데코레이터

    Args:
        step_name: 단계 이름 (None이면 함수명 사용)

    사용법:
        @monitor_performance("재무데이터수집")
        def collect_financial_data():
            # 함수 내용
            pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            if not monitor.current_analysis:
                # 모니터링이 활성화되지 않은 경우 함수만 실행
                return func(*args, **kwargs)

            step = step_name or func.__name__
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                monitor.record_step_duration(step, duration)

        return wrapper

    return decorator
