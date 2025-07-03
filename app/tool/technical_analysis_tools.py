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
            uptrend_line = self._calculate_uptrend_line(peaks, price_data)

            # 하락 추세선 계산
            downtrend_line = self._calculate_downtrend_line(troughs, price_data)

            # 지지선과 저항선 계산
            support_resistance = self._calculate_support_resistance(price_data)

            # 추세 강도 분석
            trend_strength = self._analyze_trend_strength(
                price_data, uptrend_line, downtrend_line
            )

            result = {
                "success": True,
                "uptrend_line": uptrend_line,
                "downtrend_line": downtrend_line,
                "support_resistance": support_resistance,
                "trend_strength": trend_strength,
                "peaks_count": len(peaks),
                "troughs_count": len(troughs),
                "current_position": self._analyze_current_position(
                    price_data[-1], support_resistance
                ),
                "breakout_signals": self._analyze_breakout_signals(
                    price_data, support_resistance
                ),
            }

            logger.info("✅ 추세선 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 추세선 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def generate_trading_signals(
        self, price_data: List[float], volume_data: List[float] = None
    ) -> Dict[str, Any]:
        """
        종합 매매 신호 생성

        Args:
            price_data: 가격 데이터 리스트
            volume_data: 거래량 데이터 리스트 (선택사항)

        Returns:
            Dict: 종합 매매 신호
        """
        try:
            logger.info("🔍 종합 매매 신호 생성 시작...")

            # 각종 기술적 지표 계산
            ma_analysis = self.calculate_moving_averages(price_data)
            rsi_analysis = self.calculate_rsi(price_data)
            trend_analysis = self.analyze_trend_lines(price_data)

            # 거래량 분석 (데이터가 있는 경우)
            volume_analysis = None
            if volume_data:
                volume_analysis = self.analyze_volume_patterns(price_data, volume_data)

            # 신호 통합 분석
            integrated_signals = self._integrate_trading_signals(
                ma_analysis,
                rsi_analysis,
                trend_analysis,
                volume_analysis,
            )

            # 신호 강도 계산
            signal_strength = self._calculate_signal_strength(integrated_signals)

            # 매매 추천
            trading_recommendation = self._generate_trading_recommendation(
                integrated_signals, signal_strength
            )

            result = {
                "success": True,
                "technical_indicators": {
                    "moving_averages": ma_analysis,
                    "rsi": rsi_analysis,
                    "trend_lines": trend_analysis,
                    "volume": volume_analysis,
                },
                "integrated_signals": integrated_signals,
                "signal_strength": signal_strength,
                "trading_recommendation": trading_recommendation,
                "risk_assessment": self._assess_trading_risk(integrated_signals),
                "confidence_level": self._calculate_confidence_level(
                    integrated_signals
                ),
            }

            logger.info("✅ 종합 매매 신호 생성 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 매매 신호 생성 실패: {e}")
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
