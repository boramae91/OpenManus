# -*- coding: utf-8 -*-
"""
기술적 분석가 특화 도구 모음

추세선, 이동평균, RSI, 시계열 분석 기능을 제공해요
ChatGPT 피드백을 반영한 고급 기술적 분석 도구들이에요!
"""

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from app.logger import logger


class TechnicalAnalysisTools:
    """
    기술적 분석가를 위한 특화 도구들
    추세선, 이동평균, RSI, 시계열 분석에 특화된 도구들이에요
    """

    def __init__(self):
        """기술적 분석 도구 초기화"""
        logger.info("📈 기술적 분석 도구 초기화 완료!")

    def calculate_moving_averages(
        self, price_data: List[float], periods: List[int] = [5, 10, 20, 50, 200]
    ) -> Dict[str, Any]:
        """
        다양한 기간의 이동평균 계산

        Args:
            price_data: 가격 데이터 리스트
            periods: 이동평균 기간 리스트

        Returns:
            Dict: 이동평균 분석 결과
        """
        try:
            logger.info("🔍 이동평균 분석 시작...")

            if len(price_data) < max(periods):
                return {
                    "success": False,
                    "error": f"데이터가 부족합니다. 최소 {max(periods)}개 데이터가 필요합니다.",
                }

            # 이동평균 계산
            moving_averages = {}
            for period in periods:
                if len(price_data) >= period:
                    ma_values = []
                    for i in range(period - 1, len(price_data)):
                        ma = sum(price_data[i - period + 1 : i + 1]) / period
                        ma_values.append(ma)
                    moving_averages[f"MA_{period}"] = ma_values

            # 현재 가격과 이동평균 비교
            current_price = price_data[-1]
            ma_comparison = {}
            for period, ma_values in moving_averages.items():
                if ma_values:
                    current_ma = ma_values[-1]
                    ma_comparison[period] = {
                        "value": round(current_ma, 2),
                        "difference": round(current_price - current_ma, 2),
                        "ratio": (
                            round(current_price / current_ma, 3)
                            if current_ma > 0
                            else 0
                        ),
                        "position": "above" if current_price > current_ma else "below",
                    }

            # 이동평균 크로스오버 분석
            crossover_signals = self._analyze_ma_crossovers(moving_averages)

            # 추세 분석
            trend_analysis = self._analyze_ma_trends(moving_averages)

            result = {
                "success": True,
                "current_price": current_price,
                "moving_averages": ma_comparison,
                "crossover_signals": crossover_signals,
                "trend_analysis": trend_analysis,
                "data_points": len(price_data),
                "calculation_method": "단순이동평균 (SMA)",
            }

            logger.info("✅ 이동평균 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 이동평균 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def calculate_rsi(
        self, price_data: List[float], period: int = 14
    ) -> Dict[str, Any]:
        """
        RSI(상대강도지수) 계산 및 분석

        Args:
            price_data: 가격 데이터 리스트
            period: RSI 계산 기간 (기본값: 14)

        Returns:
            Dict: RSI 분석 결과
        """
        try:
            logger.info("🔍 RSI 분석 시작...")

            if len(price_data) < period + 1:
                return {
                    "success": False,
                    "error": f"데이터가 부족합니다. 최소 {period + 1}개 데이터가 필요합니다.",
                }

            # 가격 변화 계산
            price_changes = []
            for i in range(1, len(price_data)):
                change = price_data[i] - price_data[i - 1]
                price_changes.append(change)

            # RSI 계산
            rsi_values = []
            for i in range(period, len(price_changes)):
                gains = [
                    change for change in price_changes[i - period : i] if change > 0
                ]
                losses = [
                    -change for change in price_changes[i - period : i] if change < 0
                ]

                avg_gain = sum(gains) / period if gains else 0
                avg_loss = sum(losses) / period if losses else 0

                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))

                rsi_values.append(rsi)

            # 현재 RSI 값
            current_rsi = rsi_values[-1] if rsi_values else 50

            # RSI 신호 분석
            rsi_signals = self._analyze_rsi_signals(current_rsi, rsi_values)

            # 과매수/과매도 분석
            overbought_oversold = self._analyze_overbought_oversold(current_rsi)

            result = {
                "success": True,
                "current_rsi": round(current_rsi, 2),
                "rsi_signals": rsi_signals,
                "overbought_oversold": overbought_oversold,
                "rsi_trend": self._analyze_rsi_trend(rsi_values),
                "calculation_period": period,
                "data_points": len(rsi_values),
                "interpretation": self._interpret_rsi(current_rsi),
            }

            logger.info(f"✅ RSI 분석 완료: {current_rsi:.2f}")
            return result

        except Exception as e:
            logger.error(f"❌ RSI 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def analyze_trend_lines(self, price_data: List[float]) -> Dict[str, Any]:
        """
        추세선 분석

        Args:
            price_data: 가격 데이터 리스트

        Returns:
            Dict: 추세선 분석 결과
        """
        try:
            logger.info("🔍 추세선 분석 시작...")

            if len(price_data) < 20:
                return {
                    "success": False,
                    "error": "추세선 분석을 위해 최소 20개 데이터가 필요합니다.",
                }

            # 고점과 저점 찾기
            peaks = self._find_peaks(price_data)
            troughs = self._find_troughs(price_data)

            # 상승 추세선 계산
            uptrend = self._calculate_uptrend_line(peaks, price_data)

            # 하락 추세선 계산
            downtrend = self._calculate_downtrend_line(troughs, price_data)

            # 지지/저항선 계산
            support_resistance = self._calculate_support_resistance(price_data)

            # 현재 위치 분석
            current_position = self._analyze_current_position(
                price_data[-1], support_resistance
            )

            # 돌파 신호 분석
            breakout_signals = self._analyze_breakout_signals(
                price_data, support_resistance
            )

            # 추세 강도 분석
            trend_strength = self._analyze_trend_strength(
                price_data, uptrend, downtrend
            )

            result = {
                "success": True,
                "uptrend": uptrend,
                "downtrend": downtrend,
                "support_resistance": support_resistance,
                "current_position": current_position,
                "breakout_signals": breakout_signals,
                "trend_strength": trend_strength,
                "data_points": len(price_data),
                "analysis_period": f"{len(price_data)}일",
            }

            logger.info("✅ 추세선 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 추세선 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def analyze_technical_indicators(
        self, price_data: List[float], volume_data: List[float] = None
    ) -> Dict[str, Any]:
        """
        종합 기술적 지표 분석

        Args:
            price_data: 가격 데이터 리스트
            volume_data: 거래량 데이터 리스트 (선택사항)

        Returns:
            Dict: 종합 기술적 분석 결과
        """
        try:
            logger.info("🔍 종합 기술적 지표 분석 시작...")

            # 이동평균 분석
            ma_analysis = self.calculate_moving_averages(price_data)

            # RSI 분석
            rsi_analysis = self.calculate_rsi(price_data)

            # 추세선 분석
            trend_analysis = self.analyze_trend_lines(price_data)

            # 거래량 분석 (제공된 경우)
            volume_analysis = None
            if volume_data:
                volume_analysis = self._analyze_volume_patterns(price_data, volume_data)

            # 매매 신호 생성
            trading_signals = self.generate_trading_signals(price_data, volume_data)

            result = {
                "success": True,
                "moving_averages": ma_analysis,
                "rsi": rsi_analysis,
                "trend_lines": trend_analysis,
                "volume_analysis": volume_analysis,
                "trading_signals": trading_signals,
                "summary": self._generate_technical_summary(
                    ma_analysis, rsi_analysis, trend_analysis, trading_signals
                ),
            }

            logger.info("✅ 종합 기술적 지표 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 종합 기술적 지표 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def generate_trading_signals(
        self, price_data: List[float], volume_data: List[float] = None
    ) -> Dict[str, Any]:
        """
        매매 신호 생성

        Args:
            price_data: 가격 데이터 리스트
            volume_data: 거래량 데이터 리스트 (선택사항)

        Returns:
            Dict: 매매 신호 분석 결과
        """
        try:
            logger.info("🔍 매매 신호 생성 시작...")

            # 각 지표별 분석
            ma_analysis = self.calculate_moving_averages(price_data)
            rsi_analysis = self.calculate_rsi(price_data)
            trend_analysis = self.analyze_trend_lines(price_data)

            # 거래량 분석
            volume_analysis = None
            if volume_data:
                volume_analysis = self._analyze_volume_patterns(price_data, volume_data)

            # 신호 통합
            integrated_signals = self._integrate_trading_signals(
                ma_analysis, rsi_analysis, trend_analysis, volume_analysis
            )

            # 신호 강도 계산
            signal_strength = self._calculate_signal_strength(integrated_signals)

            # 매매 추천 생성
            trading_recommendation = self._generate_trading_recommendation(
                integrated_signals, signal_strength
            )

            # 리스크 평가
            risk_assessment = self._assess_trading_risk(integrated_signals)

            # 신뢰도 계산
            confidence_level = self._calculate_confidence_level(integrated_signals)

            result = {
                "success": True,
                "integrated_signals": integrated_signals,
                "signal_strength": signal_strength,
                "trading_recommendation": trading_recommendation,
                "risk_assessment": risk_assessment,
                "confidence_level": confidence_level,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info("✅ 매매 신호 생성 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 매매 신호 생성 실패: {e}")
            return {"success": False, "error": str(e)}

    def analyze_chart_patterns(self, price_data: List[float]) -> Dict[str, Any]:
        """
        차트 패턴 분석 (헤드앤숄더, 더블탑, 삼각형 등)

        Args:
            price_data: 가격 데이터 리스트

        Returns:
            Dict: 차트 패턴 분석 결과
        """
        try:
            logger.info("🔍 차트 패턴 분석 시작...")

            if len(price_data) < 30:
                return {
                    "success": False,
                    "error": "차트 패턴 분석을 위해 최소 30개 데이터가 필요합니다.",
                }

            patterns = {}

            # 헤드앤숄더 패턴 검출
            head_shoulders = self._detect_head_and_shoulders(price_data)
            if head_shoulders:
                patterns["head_and_shoulders"] = head_shoulders

            # 더블탑/더블바텀 패턴 검출
            double_patterns = self._detect_double_patterns(price_data)
            if double_patterns:
                patterns["double_patterns"] = double_patterns

            # 삼각형 패턴 검출
            triangle_patterns = self._detect_triangle_patterns(price_data)
            if triangle_patterns:
                patterns["triangle_patterns"] = triangle_patterns

            # 플래그/페넌트 패턴 검출
            flag_patterns = self._detect_flag_patterns(price_data)
            if flag_patterns:
                patterns["flag_patterns"] = flag_patterns

            result = {
                "success": True,
                "patterns": patterns,
                "pattern_count": len(patterns),
                "data_points": len(price_data),
                "analysis_period": f"{len(price_data)}일",
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ 차트 패턴 분석 완료: {len(patterns)}개 패턴 발견")
            return result

        except Exception as e:
            logger.error(f"❌ 차트 패턴 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def analyze_trends(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        주가 추세 분석

        Args:
            market_data: 시장 데이터

        Returns:
            Dict: 추세 분석 결과
        """
        try:
            logger.info("🔍 주가 추세 분석 시작...")

            # 기본 데이터 추출
            current_price = market_data.get("current_price", 0)
            price_history = market_data.get("price_history", [])

            if not price_history or len(price_history) < 2:
                return {
                    "success": False,
                    "error": "가격 이력 데이터가 부족합니다",
                    "trend": "분석 불가",
                }

            # 단기/중기/장기 추세 분석
            short_term_trend = self._analyze_short_term_trend(
                price_history[-20:]
            )  # 최근 20일
            medium_term_trend = self._analyze_medium_term_trend(
                price_history[-60:]
            )  # 최근 60일
            long_term_trend = self._analyze_long_term_trend(price_history)  # 전체 기간

            # 추세 강도 분석
            trend_strength = self._calculate_trend_strength(price_history)

            result = {
                "success": True,
                "trend_analysis": {
                    "short_term": short_term_trend,
                    "medium_term": medium_term_trend,
                    "long_term": long_term_trend,
                    "trend_strength": trend_strength,
                },
                "current_price": current_price,
                "interpretation": self._interpret_trend_analysis(
                    short_term_trend, medium_term_trend, long_term_trend
                ),
            }

            logger.info(f"✅ 추세 분석 완료: {short_term_trend['direction']}")
            return result

        except Exception as e:
            logger.error(f"❌ 추세 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def analyze_support_resistance(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        지지/저항선 분석

        Args:
            market_data: 시장 데이터

        Returns:
            Dict: 지지/저항선 분석 결과
        """
        try:
            logger.info("🔍 지지/저항선 분석 시작...")

            # 기본 데이터 추출
            current_price = market_data.get("current_price", 0)
            price_history = market_data.get("price_history", [])

            if not price_history or len(price_history) < 20:
                return {
                    "success": False,
                    "error": "가격 이력 데이터가 부족합니다",
                    "support_resistance": "분석 불가",
                }

            # 지지선/저항선 계산
            support_levels = self._find_support_levels(price_history)
            resistance_levels = self._find_resistance_levels(price_history)

            # 현재 가격과의 관계 분석
            nearest_support = self._find_nearest_support(current_price, support_levels)
            nearest_resistance = self._find_nearest_resistance(
                current_price, resistance_levels
            )

            result = {
                "success": True,
                "support_resistance": {
                    "support_levels": support_levels,
                    "resistance_levels": resistance_levels,
                    "nearest_support": nearest_support,
                    "nearest_resistance": nearest_resistance,
                    "current_position": self._analyze_current_position(
                        current_price, nearest_support, nearest_resistance
                    ),
                },
                "current_price": current_price,
                "interpretation": self._interpret_support_resistance(
                    nearest_support, nearest_resistance, current_price
                ),
            }

            logger.info(
                f"✅ 지지/저항선 분석 완료: 지지선 {nearest_support}, 저항선 {nearest_resistance}"
            )
            return result

        except Exception as e:
            logger.error(f"❌ 지지/저항선 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    # ==================== 내부 헬퍼 메서드들 ====================

    def _analyze_ma_crossovers(
        self, moving_averages: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """이동평균 크로스오버 분석"""
        crossovers = []

        # 단기/장기 이동평균 크로스오버 확인
        if "MA_5" in moving_averages and "MA_20" in moving_averages:
            ma5 = moving_averages["MA_5"]
            ma20 = moving_averages["MA_20"]

            if len(ma5) >= 2 and len(ma20) >= 2:
                # 골든 크로스 (단기선이 장기선을 상향 돌파)
                if ma5[-2] <= ma20[-2] and ma5[-1] > ma20[-1]:
                    crossovers.append(
                        {
                            "type": "golden_cross",
                            "description": "단기 이동평균이 장기 이동평균을 상향 돌파",
                            "signal": "매수 신호",
                        }
                    )

                # 데드 크로스 (단기선이 장기선을 하향 돌파)
                elif ma5[-2] >= ma20[-2] and ma5[-1] < ma20[-1]:
                    crossovers.append(
                        {
                            "type": "dead_cross",
                            "description": "단기 이동평균이 장기 이동평균을 하향 돌파",
                            "signal": "매도 신호",
                        }
                    )

        return {"crossovers": crossovers, "total_signals": len(crossovers)}

    def _analyze_ma_trends(
        self, moving_averages: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """이동평균 추세 분석"""
        trends = {}

        for period, ma_values in moving_averages.items():
            if len(ma_values) >= 5:
                recent_trend = "상승" if ma_values[-1] > ma_values[-5] else "하락"
                trends[period] = {
                    "trend": recent_trend,
                    "slope": round((ma_values[-1] - ma_values[-5]) / 5, 4),
                }

        return trends

    def _analyze_rsi_signals(
        self, current_rsi: float, rsi_values: List[float]
    ) -> Dict[str, Any]:
        """RSI 신호 분석"""
        signals = []

        # 과매수/과매도 신호
        if current_rsi > 70:
            signals.append(
                {
                    "type": "overbought",
                    "description": "과매수 구간",
                    "signal": "매도 고려",
                }
            )
        elif current_rsi < 30:
            signals.append(
                {
                    "type": "oversold",
                    "description": "과매도 구간",
                    "signal": "매수 고려",
                }
            )

        return {"signals": signals, "total_signals": len(signals)}

    def _analyze_overbought_oversold(self, current_rsi: float) -> Dict[str, Any]:
        """과매수/과매도 분석"""
        if current_rsi > 80:
            status = "심각한 과매수"
            action = "매도 강력 권장"
        elif current_rsi > 70:
            status = "과매수"
            action = "매도 고려"
        elif current_rsi < 20:
            status = "심각한 과매도"
            action = "매수 강력 권장"
        elif current_rsi < 30:
            status = "과매도"
            action = "매수 고려"
        else:
            status = "중립"
            action = "관망"

        return {"status": status, "action": action, "rsi_level": current_rsi}

    def _analyze_rsi_trend(self, rsi_values: List[float]) -> str:
        """RSI 추세 분석"""
        if len(rsi_values) < 5:
            return "데이터 부족"

        recent_trend = "상승" if rsi_values[-1] > rsi_values[-5] else "하락"
        return f"RSI {recent_trend} 추세"

    def _interpret_rsi(self, rsi: float) -> str:
        """RSI 해석"""
        if rsi > 80:
            return "심각한 과매수 상태로 조정 가능성 높음"
        elif rsi > 70:
            return "과매수 상태로 매도 압력 증가"
        elif rsi < 20:
            return "심각한 과매도 상태로 반등 가능성 높음"
        elif rsi < 30:
            return "과매도 상태로 매수 기회"
        else:
            return "중립 구간으로 추세 추종"

    def _find_peaks(self, data: List[float]) -> List[int]:
        """고점 찾기"""
        peaks = []
        for i in range(1, len(data) - 1):
            if data[i] > data[i - 1] and data[i] > data[i + 1]:
                peaks.append(i)
        return peaks

    def _find_troughs(self, data: List[float]) -> List[int]:
        """저점 찾기"""
        troughs = []
        for i in range(1, len(data) - 1):
            if data[i] < data[i - 1] and data[i] < data[i + 1]:
                troughs.append(i)
        return troughs

    def _calculate_uptrend_line(
        self, peaks: List[int], price_data: List[float]
    ) -> Dict[str, Any]:
        """상승 추세선 계산"""
        if len(peaks) < 2:
            return {"success": False, "error": "고점이 부족합니다"}

        # 최근 2개 고점으로 추세선 계산
        recent_peaks = peaks[-2:]
        x1, x2 = recent_peaks[0], recent_peaks[1]
        y1, y2 = price_data[x1], price_data[x2]

        slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
        intercept = y1 - slope * x1

        return {
            "success": True,
            "slope": round(slope, 4),
            "intercept": round(intercept, 2),
            "equation": f"y = {slope:.4f}x + {intercept:.2f}",
            "strength": "강함" if slope > 0.1 else "약함" if slope > 0 else "하락",
        }

    def _calculate_downtrend_line(
        self, troughs: List[int], price_data: List[float]
    ) -> Dict[str, Any]:
        """하락 추세선 계산"""
        if len(troughs) < 2:
            return {"success": False, "error": "저점이 부족합니다"}

        # 최근 2개 저점으로 추세선 계산
        recent_troughs = troughs[-2:]
        x1, x2 = recent_troughs[0], recent_troughs[1]
        y1, y2 = price_data[x1], price_data[x2]

        slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
        intercept = y1 - slope * x1

        return {
            "success": True,
            "slope": round(slope, 4),
            "intercept": round(intercept, 2),
            "equation": f"y = {slope:.4f}x + {intercept:.2f}",
            "strength": "강함" if slope < -0.1 else "약함" if slope < 0 else "상승",
        }

    def _calculate_support_resistance(self, price_data: List[float]) -> Dict[str, Any]:
        """지지선과 저항선 계산"""
        if len(price_data) < 20:
            return {"success": False, "error": "데이터가 부족합니다"}

        # 최근 20일간의 고점과 저점
        recent_data = price_data[-20:]
        high = max(recent_data)
        low = min(recent_data)

        current_price = price_data[-1]

        return {
            "success": True,
            "resistance_level": round(high, 2),
            "support_level": round(low, 2),
            "current_position": (
                "저항선 근처"
                if current_price > high * 0.95
                else "지지선 근처" if current_price < low * 1.05 else "중간"
            ),
            "distance_to_resistance": round(high - current_price, 2),
            "distance_to_support": round(current_price - low, 2),
        }

    def _analyze_trend_strength(
        self, price_data: List[float], uptrend: Dict, downtrend: Dict
    ) -> str:
        """추세 강도 분석"""
        if not uptrend.get("success") and not downtrend.get("success"):
            return "추세 불명확"

        if uptrend.get("success") and uptrend["slope"] > 0.1:
            return "강한 상승 추세"
        elif downtrend.get("success") and downtrend["slope"] < -0.1:
            return "강한 하락 추세"
        else:
            return "약한 추세"

    def _analyze_current_position(
        self, current_price: float, support_resistance: Dict[str, Any]
    ) -> str:
        """현재 위치 분석"""
        if not support_resistance.get("success"):
            return "분석 불가"

        resistance = support_resistance["resistance_level"]
        support = support_resistance["support_level"]

        if current_price > resistance * 0.98:
            return "저항선 근처"
        elif current_price < support * 1.02:
            return "지지선 근처"
        else:
            return "중간 구간"

    def _analyze_breakout_signals(
        self, price_data: List[float], support_resistance: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """돌파 신호 분석"""
        signals = []

        if not support_resistance.get("success"):
            return signals

        current_price = price_data[-1]
        resistance = support_resistance["resistance_level"]
        support = support_resistance["support_level"]

        # 저항선 돌파
        if current_price > resistance:
            signals.append(
                {
                    "type": "breakout",
                    "direction": "상향",
                    "level": resistance,
                    "signal": "매수 신호",
                }
            )

        # 지지선 이탈
        if current_price < support:
            signals.append(
                {
                    "type": "breakdown",
                    "direction": "하향",
                    "level": support,
                    "signal": "매도 신호",
                }
            )

        return signals

    def _integrate_trading_signals(
        self,
        ma_analysis: Dict,
        rsi_analysis: Dict,
        trend_analysis: Dict,
        volume_analysis: Dict = None,
    ) -> Dict[str, Any]:
        """매매 신호 통합 분석"""
        signals = []
        bullish_count = 0
        bearish_count = 0

        # 이동평균 신호
        if ma_analysis.get("success"):
            for crossover in ma_analysis.get("crossover_signals", {}).get(
                "crossovers", []
            ):
                if crossover["type"] == "golden_cross":
                    signals.append(
                        {"indicator": "MA", "signal": "매수", "strength": "강함"}
                    )
                    bullish_count += 1
                elif crossover["type"] == "dead_cross":
                    signals.append(
                        {"indicator": "MA", "signal": "매도", "strength": "강함"}
                    )
                    bearish_count += 1

        # RSI 신호
        if rsi_analysis.get("success"):
            current_rsi = rsi_analysis.get("current_rsi", 50)
            if current_rsi < 30:
                signals.append(
                    {"indicator": "RSI", "signal": "매수", "strength": "중간"}
                )
                bullish_count += 1
            elif current_rsi > 70:
                signals.append(
                    {"indicator": "RSI", "signal": "매도", "strength": "중간"}
                )
                bearish_count += 1

        # 추세선 신호
        if trend_analysis.get("success"):
            for signal in trend_analysis.get("breakout_signals", []):
                if signal["type"] == "breakout":
                    signals.append(
                        {"indicator": "Trend", "signal": "매수", "strength": "강함"}
                    )
                    bullish_count += 1
                elif signal["type"] == "breakdown":
                    signals.append(
                        {"indicator": "Trend", "signal": "매도", "strength": "강함"}
                    )
                    bearish_count += 1

        return {
            "signals": signals,
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "total_signals": len(signals),
        }

    def _calculate_signal_strength(self, integrated_signals: Dict[str, Any]) -> str:
        """신호 강도 계산"""
        bullish = integrated_signals.get("bullish_count", 0)
        bearish = integrated_signals.get("bearish_count", 0)

        if bullish > bearish + 1:
            return "강한 매수"
        elif bullish > bearish:
            return "약한 매수"
        elif bearish > bullish + 1:
            return "강한 매도"
        elif bearish > bullish:
            return "약한 매도"
        else:
            return "중립"

    def _generate_trading_recommendation(
        self, integrated_signals: Dict[str, Any], signal_strength: str
    ) -> Dict[str, Any]:
        """매매 추천 생성"""
        recommendation = {
            "action": "관망",
            "confidence": "낮음",
            "reasoning": "신호가 모호합니다",
        }

        if signal_strength == "강한 매수":
            recommendation = {
                "action": "매수",
                "confidence": "높음",
                "reasoning": "여러 지표에서 일관된 매수 신호",
            }
        elif signal_strength == "약한 매수":
            recommendation = {
                "action": "매수 고려",
                "confidence": "중간",
                "reasoning": "일부 지표에서 매수 신호",
            }
        elif signal_strength == "강한 매도":
            recommendation = {
                "action": "매도",
                "confidence": "높음",
                "reasoning": "여러 지표에서 일관된 매도 신호",
            }
        elif signal_strength == "약한 매도":
            recommendation = {
                "action": "매도 고려",
                "confidence": "중간",
                "reasoning": "일부 지표에서 매도 신호",
            }

        return recommendation

    def _assess_trading_risk(
        self, integrated_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """매매 리스크 평가"""
        total_signals = integrated_signals.get("total_signals", 0)

        if total_signals == 0:
            risk_level = "높음"
            reason = "신호가 없어 불확실성 높음"
        elif total_signals >= 4:
            risk_level = "낮음"
            reason = "여러 지표에서 일관된 신호"
        else:
            risk_level = "중간"
            reason = "제한된 신호로 중간 리스크"

        return {
            "risk_level": risk_level,
            "reason": reason,
            "signal_count": total_signals,
        }

    def _calculate_confidence_level(self, integrated_signals: Dict[str, Any]) -> str:
        """신뢰도 계산"""
        total_signals = integrated_signals.get("total_signals", 0)

        if total_signals >= 4:
            return "높음"
        elif total_signals >= 2:
            return "중간"
        else:
            return "낮음"

    def _analyze_volume_patterns(
        self, price_data: List[float], volume_data: List[float]
    ) -> Dict[str, Any]:
        """
        거래량 패턴 분석

        Args:
            price_data: 가격 데이터
            volume_data: 거래량 데이터

        Returns:
            Dict: 거래량 분석 결과
        """
        try:
            if len(price_data) != len(volume_data):
                return {
                    "success": False,
                    "error": "가격과 거래량 데이터 길이가 다릅니다.",
                }

            # 평균 거래량 계산
            avg_volume = sum(volume_data) / len(volume_data)

            # 현재 거래량
            current_volume = volume_data[-1]

            # 거래량 증가율
            volume_change = ((current_volume - avg_volume) / avg_volume) * 100

            # 가격 변화와 거래량 관계
            price_change = (
                ((price_data[-1] - price_data[-2]) / price_data[-2]) * 100
                if len(price_data) > 1
                else 0
            )

            result = {
                "success": True,
                "current_volume": current_volume,
                "average_volume": avg_volume,
                "volume_change_percent": round(volume_change, 2),
                "price_change_percent": round(price_change, 2),
                "volume_price_relationship": self._interpret_volume_price_relationship(
                    price_change, volume_change
                ),
                "volume_trend": "증가" if volume_change > 0 else "감소",
            }

            return result

        except Exception as e:
            logger.error(f"❌ 거래량 패턴 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def _interpret_volume_price_relationship(
        self, price_change: float, volume_change: float
    ) -> str:
        """
        가격과 거래량 관계 해석

        Args:
            price_change: 가격 변화율
            volume_change: 거래량 변화율

        Returns:
            str: 관계 해석
        """
        if price_change > 0 and volume_change > 0:
            return "가격 상승 + 거래량 증가 = 강한 상승 신호"
        elif price_change > 0 and volume_change < 0:
            return "가격 상승 + 거래량 감소 = 약한 상승 신호"
        elif price_change < 0 and volume_change > 0:
            return "가격 하락 + 거래량 증가 = 강한 하락 신호"
        elif price_change < 0 and volume_change < 0:
            return "가격 하락 + 거래량 감소 = 약한 하락 신호"
        else:
            return "중립적 신호"

    def _generate_technical_summary(
        self,
        ma_analysis: Dict,
        rsi_analysis: Dict,
        trend_analysis: Dict,
        trading_signals: Dict,
    ) -> Dict[str, Any]:
        """
        기술적 분석 요약 생성

        Args:
            ma_analysis: 이동평균 분석 결과
            rsi_analysis: RSI 분석 결과
            trend_analysis: 추세선 분석 결과
            trading_signals: 거래 신호 결과

        Returns:
            Dict: 종합 요약
        """
        try:
            summary = {
                "overall_sentiment": "중립",
                "key_signals": [],
                "risk_level": "보통",
                "recommendation": "관망",
            }

            # 전반적 감정 분석
            bullish_signals = 0
            bearish_signals = 0

            # 이동평균 신호 분석
            if ma_analysis.get("success"):
                ma_signals = ma_analysis.get("crossover_signals", {})
                for signal in ma_signals.get("bullish_signals", []):
                    bullish_signals += 1
                for signal in ma_signals.get("bearish_signals", []):
                    bearish_signals += 1

            # RSI 신호 분석
            if rsi_analysis.get("success"):
                current_rsi = rsi_analysis.get("current_rsi", 50)
                if current_rsi < 30:
                    bullish_signals += 1
                elif current_rsi > 70:
                    bearish_signals += 1

            # 추세선 신호 분석
            if trend_analysis.get("success"):
                trend_strength = trend_analysis.get("trend_strength", "중립")
                if "상승" in trend_strength:
                    bullish_signals += 1
                elif "하락" in trend_strength:
                    bearish_signals += 1

            # 전반적 감정 결정
            if bullish_signals > bearish_signals:
                summary["overall_sentiment"] = "매수"
                summary["recommendation"] = "매수 고려"
            elif bearish_signals > bullish_signals:
                summary["overall_sentiment"] = "매도"
                summary["recommendation"] = "매도 고려"
            else:
                summary["overall_sentiment"] = "중립"
                summary["recommendation"] = "관망"

            # 주요 신호 추출
            if ma_analysis.get("success"):
                summary["key_signals"].append("이동평균 분석 완료")
            if rsi_analysis.get("success"):
                summary["key_signals"].append(
                    f"RSI: {rsi_analysis.get('current_rsi', 0):.1f}"
                )
            if trend_analysis.get("success"):
                summary["key_signals"].append(
                    f"추세: {trend_analysis.get('trend_strength', '중립')}"
                )

            return summary

        except Exception as e:
            logger.error(f"❌ 기술적 분석 요약 생성 실패: {e}")
            return {
                "overall_sentiment": "중립",
                "key_signals": ["분석 오류"],
                "risk_level": "높음",
                "recommendation": "관망",
            }

    def _detect_head_and_shoulders(
        self, price_data: List[float]
    ) -> Optional[Dict[str, Any]]:
        """헤드앤숄더 패턴 검출"""
        try:
            if len(price_data) < 20:
                return None

            # 고점들 찾기
            peaks = self._find_peaks(price_data)
            if len(peaks) < 3:
                return None

            # 최근 3개 고점 분석
            recent_peaks = peaks[-3:]
            peak_values = [price_data[i] for i in recent_peaks]

            # 헤드앤숄더 조건 확인
            left_shoulder = peak_values[0]
            head = peak_values[1]
            right_shoulder = peak_values[2]

            # 조건: 헤드가 양쪽 어깨보다 높고, 어깨들이 비슷한 높이
            shoulder_tolerance = 0.05  # 5% 허용 오차

            if (
                head > left_shoulder
                and head > right_shoulder
                and abs(left_shoulder - right_shoulder) / left_shoulder
                < shoulder_tolerance
            ):

                return {
                    "type": "head_and_shoulders",
                    "pattern": "bearish",
                    "left_shoulder": left_shoulder,
                    "head": head,
                    "right_shoulder": right_shoulder,
                    "neckline": min(left_shoulder, right_shoulder),
                    "target": min(left_shoulder, right_shoulder)
                    - (head - min(left_shoulder, right_shoulder)),
                    "confidence": (
                        "high"
                        if abs(left_shoulder - right_shoulder) / left_shoulder < 0.02
                        else "medium"
                    ),
                }

            return None

        except Exception as e:
            logger.error(f"❌ 헤드앤숄더 패턴 검출 실패: {e}")
            return None

    def _detect_double_patterns(
        self, price_data: List[float]
    ) -> Optional[Dict[str, Any]]:
        """더블탑/더블바텀 패턴 검출"""
        try:
            if len(price_data) < 15:
                return None

            # 고점과 저점들 찾기
            peaks = self._find_peaks(price_data)
            troughs = self._find_troughs(price_data)

            patterns = []

            # 더블탑 검출
            if len(peaks) >= 2:
                recent_peaks = peaks[-2:]
                peak_values = [price_data[i] for i in recent_peaks]

                # 두 고점이 비슷한 높이인지 확인
                if (
                    abs(peak_values[0] - peak_values[1]) / peak_values[0] < 0.03
                ):  # 3% 허용 오차
                    patterns.append(
                        {
                            "type": "double_top",
                            "pattern": "bearish",
                            "peaks": peak_values,
                            "support": min(
                                price_data[recent_peaks[0] : recent_peaks[1]]
                            ),
                            "target": min(price_data[recent_peaks[0] : recent_peaks[1]])
                            - (
                                max(peak_values)
                                - min(price_data[recent_peaks[0] : recent_peaks[1]])
                            ),
                            "confidence": "medium",
                        }
                    )

            # 더블바텀 검출
            if len(troughs) >= 2:
                recent_troughs = troughs[-2:]
                trough_values = [price_data[i] for i in recent_troughs]

                # 두 저점이 비슷한 높이인지 확인
                if (
                    abs(trough_values[0] - trough_values[1]) / trough_values[0] < 0.03
                ):  # 3% 허용 오차
                    patterns.append(
                        {
                            "type": "double_bottom",
                            "pattern": "bullish",
                            "troughs": trough_values,
                            "resistance": max(
                                price_data[recent_troughs[0] : recent_troughs[1]]
                            ),
                            "target": max(
                                price_data[recent_troughs[0] : recent_troughs[1]]
                            )
                            + (
                                max(price_data[recent_troughs[0] : recent_troughs[1]])
                                - min(trough_values)
                            ),
                            "confidence": "medium",
                        }
                    )

            return {"patterns": patterns} if patterns else None

        except Exception as e:
            logger.error(f"❌ 더블 패턴 검출 실패: {e}")
            return None

    def _detect_triangle_patterns(
        self, price_data: List[float]
    ) -> Optional[Dict[str, Any]]:
        """삼각형 패턴 검출"""
        try:
            if len(price_data) < 20:
                return None

            # 고점과 저점들의 추세 분석
            peaks = self._find_peaks(price_data)
            troughs = self._find_troughs(price_data)

            if len(peaks) < 3 or len(troughs) < 3:
                return None

            # 고점과 저점의 추세 계산
            peak_trend = self._calculate_trend([price_data[i] for i in peaks[-3:]])
            trough_trend = self._calculate_trend([price_data[i] for i in troughs[-3:]])

            patterns = []

            # 대칭 삼각형
            if abs(peak_trend) < 0.01 and abs(trough_trend) < 0.01:
                patterns.append(
                    {
                        "type": "symmetrical_triangle",
                        "pattern": "neutral",
                        "breakout_direction": "unknown",
                        "confidence": "medium",
                    }
                )

            # 상승 삼각형
            elif abs(peak_trend) < 0.01 and trough_trend > 0.01:
                patterns.append(
                    {
                        "type": "ascending_triangle",
                        "pattern": "bullish",
                        "breakout_direction": "upward",
                        "confidence": "medium",
                    }
                )

            # 하락 삼각형
            elif abs(trough_trend) < 0.01 and peak_trend < -0.01:
                patterns.append(
                    {
                        "type": "descending_triangle",
                        "pattern": "bearish",
                        "breakout_direction": "downward",
                        "confidence": "medium",
                    }
                )

            return {"patterns": patterns} if patterns else None

        except Exception as e:
            logger.error(f"❌ 삼각형 패턴 검출 실패: {e}")
            return None

    def _detect_flag_patterns(
        self, price_data: List[float]
    ) -> Optional[Dict[str, Any]]:
        """플래그/페이넌트 패턴 검출"""
        try:
            if len(price_data) < 15:
                return None

            # 최근 가격 움직임 분석
            recent_prices = price_data[-10:]
            price_trend = self._calculate_trend(recent_prices)

            patterns = []

            # 강한 상승 후 횡보 (플래그)
            if price_trend > 0.02:  # 2% 이상 상승
                patterns.append(
                    {
                        "type": "flag",
                        "pattern": "bullish",
                        "continuation": True,
                        "confidence": "medium",
                    }
                )

            # 강한 하락 후 횡보 (페이넌트)
            elif price_trend < -0.02:  # 2% 이상 하락
                patterns.append(
                    {
                        "type": "pennant",
                        "pattern": "bearish",
                        "continuation": True,
                        "confidence": "medium",
                    }
                )

            return {"patterns": patterns} if patterns else None

        except Exception as e:
            logger.error(f"❌ 플래그 패턴 검출 실패: {e}")
            return None

    def _calculate_trend(self, values: List[float]) -> float:
        """값들의 추세 계산"""
        try:
            if len(values) < 2:
                return 0.0

            # 선형 회귀를 통한 추세 계산
            x = list(range(len(values)))
            y = values

            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))

            if n * sum_x2 - sum_x**2 == 0:
                return 0.0

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
            return slope

        except Exception as e:
            logger.error(f"❌ 추세 계산 실패: {e}")
            return 0.0

    def _analyze_short_term_trend(self, price_data: List[float]) -> Dict[str, Any]:
        """단기 추세 분석"""
        if len(price_data) < 2:
            return {"direction": "불명확", "strength": "약함", "slope": 0}

        # 선형 회귀로 기울기 계산
        x = list(range(len(price_data)))
        y = price_data

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))

        slope = (
            (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
            if (n * sum_x2 - sum_x**2) != 0
            else 0
        )

        # 추세 방향 결정
        if slope > 0.1:
            direction = "상승"
            strength = "강함" if slope > 0.5 else "보통"
        elif slope < -0.1:
            direction = "하락"
            strength = "강함" if slope < -0.5 else "보통"
        else:
            direction = "횡보"
            strength = "약함"

        return {
            "direction": direction,
            "strength": strength,
            "slope": round(slope, 4),
            "price_change": round(price_data[-1] - price_data[0], 2),
        }

    def _analyze_medium_term_trend(self, price_data: List[float]) -> Dict[str, Any]:
        """중기 추세 분석"""
        return self._analyze_short_term_trend(price_data)

    def _analyze_long_term_trend(self, price_data: List[float]) -> Dict[str, Any]:
        """장기 추세 분석"""
        return self._analyze_short_term_trend(price_data)

    def _calculate_trend_strength(self, price_data: List[float]) -> str:
        """추세 강도 계산"""
        if len(price_data) < 10:
            return "약함"

        # 변동성 계산
        returns = [
            (price_data[i] - price_data[i - 1]) / price_data[i - 1]
            for i in range(1, len(price_data))
        ]
        volatility = sum(abs(r) for r in returns) / len(returns)

        if volatility > 0.03:
            return "강함"
        elif volatility > 0.015:
            return "보통"
        else:
            return "약함"

    def _find_support_levels(self, price_data: List[float]) -> List[float]:
        """지지선 찾기"""
        if len(price_data) < 10:
            return []

        # 최근 10일간의 최저점들을 지지선으로 간주
        support_levels = []
        for i in range(1, len(price_data) - 1):
            if price_data[i] < price_data[i - 1] and price_data[i] < price_data[i + 1]:
                support_levels.append(price_data[i])

        return sorted(list(set(support_levels)))[-3:]  # 최근 3개 지지선

    def _find_resistance_levels(self, price_data: List[float]) -> List[float]:
        """저항선 찾기"""
        if len(price_data) < 10:
            return []

        # 최근 10일간의 최고점들을 저항선으로 간주
        resistance_levels = []
        for i in range(1, len(price_data) - 1):
            if price_data[i] > price_data[i - 1] and price_data[i] > price_data[i + 1]:
                resistance_levels.append(price_data[i])

        return sorted(list(set(resistance_levels)))[-3:]  # 최근 3개 저항선

    def _find_nearest_support(
        self, current_price: float, support_levels: List[float]
    ) -> float:
        """가장 가까운 지지선 찾기"""
        if not support_levels:
            return 0

        # 현재 가격보다 낮은 지지선 중 가장 가까운 것
        valid_supports = [s for s in support_levels if s < current_price]
        if not valid_supports:
            return min(support_levels)

        return max(valid_supports)

    def _find_nearest_resistance(
        self, current_price: float, resistance_levels: List[float]
    ) -> float:
        """가장 가까운 저항선 찾기"""
        if not resistance_levels:
            return 0

        # 현재 가격보다 높은 저항선 중 가장 가까운 것
        valid_resistances = [r for r in resistance_levels if r > current_price]
        if not valid_resistances:
            return max(resistance_levels)

        return min(valid_resistances)

    def _analyze_current_position(
        self, current_price: float, support: float, resistance: float
    ) -> str:
        """현재 가격 위치 분석"""
        if support == 0 or resistance == 0:
            return "분석 불가"

        support_distance = current_price - support
        resistance_distance = resistance - current_price

        if support_distance < resistance_distance:
            return "지지선 근처"
        else:
            return "저항선 근처"

    def _interpret_trend_analysis(
        self, short_term: Dict, medium_term: Dict, long_term: Dict
    ) -> str:
        """추세 분석 결과 해석"""
        short_direction = short_term.get("direction", "불명확")
        medium_direction = medium_term.get("direction", "불명확")
        long_direction = long_term.get("direction", "불명확")

        if short_direction == medium_direction == long_direction:
            return f"모든 기간에서 {short_direction} 추세가 일관되게 나타납니다."
        elif short_direction == medium_direction:
            return f"단기와 중기에서 {short_direction} 추세, 장기에서는 {long_direction} 추세입니다."
        else:
            return f"추세가 혼재되어 있습니다: 단기 {short_direction}, 중기 {medium_direction}, 장기 {long_direction}"

    def _interpret_support_resistance(
        self, support: float, resistance: float, current_price: float
    ) -> str:
        """지지/저항선 분석 결과 해석"""
        if support == 0 or resistance == 0:
            return "지지/저항선 분석이 어렵습니다."

        support_distance = current_price - support
        resistance_distance = resistance - current_price

        if support_distance < resistance_distance:
            return (
                f"지지선({support:.0f}원) 근처에서 거래되고 있어 하락 위험이 있습니다."
            )
        else:
            return f"저항선({resistance:.0f}원) 근처에서 거래되고 있어 상승 가능성이 있습니다."
