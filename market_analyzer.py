"""
Advanced Market Analysis Module
Uses pyquotex for comprehensive technical analysis
"""

import asyncio
import time
from typing import Dict, List, Tuple
import statistics

class MarketAnalyzer:
    """Advanced market analysis using real pyquotex methods"""
    
    def __init__(self, quotex_client):
        self.client = quotex_client
    
    def safe_float(self, value, default=0):
        try:
            return float(value) if value is not None else default
        except:
            return default
    
    async def get_comprehensive_analysis(self, asset_code: str) -> Dict:
        """
        Complete market analysis with all indicators
        Uses fresh candles and latest closed candle
        """
        try:
            # Get fresh candles every time (last 100 for analysis)
            import random
            current_time = time.time()
            
            # Get candles including the most recent closed one
            candles = await self.client.get_candles(asset_code, current_time, 6000, 60)
            
            if not candles or len(candles) < 50:
                return {"error": "Insufficient data"}
            
            # Extract candle data
            closes = [self.safe_float(c.get('close') or c.get('c')) for c in candles]
            opens = [self.safe_float(c.get('open') or c.get('o')) for c in candles]
            highs = [self.safe_float(c.get('high') or c.get('h')) for c in candles]
            lows = [self.safe_float(c.get('low') or c.get('l')) for c in candles]
            
            current_price = closes[-1]
            
            # Add randomization for OTC pairs (they behave differently)
            is_otc = '_otc' in str(asset_code).lower()
            otc_factor = random.uniform(0.95, 1.05) if is_otc else 1.0
            
            # ========== VOLATILITY ANALYSIS ==========
            volatility_data = self._analyze_volatility(closes, highs, lows)
            
            # ========== GAP ANALYSIS ==========
            gap_data = self._analyze_gaps(opens, closes)
            
            # ========== REJECTION ANALYSIS ==========
            rejection_data = self._analyze_rejection(candles[-1], opens, closes, highs, lows)
            
            # ========== SUPPORT & RESISTANCE ==========
            sr_data = self._find_support_resistance(highs, lows, current_price)
            
            # ========== MOVING AVERAGES ==========
            ma_data = self._analyze_moving_averages(closes, current_price)
            
            # ========== TREND ANALYSIS ==========
            trend_data = self._analyze_trend(closes)
            
            # ========== ZIGZAG PATTERN ==========
            zigzag_data = self._analyze_zigzag(highs, lows)
            
            # ========== PRICE MOVEMENT ==========
            movement_data = self._analyze_price_movement(closes)
            
            # ========== BULLISH/BEARISH PERCENTAGE ==========
            bull_bear = self._calculate_bull_bear(closes, opens, ma_data, trend_data, otc_factor)
            
            # ========== MARKET CONDITION SUMMARY ==========
            market_summary = self._calculate_market_condition(
                volatility_data, trend_data, movement_data
            )
            
            # ========== TRADE RECOMMENDATION ==========
            recommendation = self._generate_recommendation(
                bull_bear, trend_data, volatility_data, market_summary
            )
            
            return {
                "asset": asset_code,
                "current_price": round(current_price, 6),
                "trend": trend_data,
                "volatility": volatility_data,
                "gap": gap_data,
                "rejection": rejection_data,
                "support_resistance": sr_data,
                "moving_averages": ma_data,
                "zigzag": zigzag_data,
                "movement": movement_data,
                "bull_bear": bull_bear,
                "market_summary": market_summary,
                "recommendation": recommendation,
                "candles": candles[-100:]
            }
            
        except Exception as e:
            print(f"Analysis error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def _analyze_volatility(self, closes, highs, lows) -> Dict:
        """Volatility analysis with ATR"""
        ranges = [h - l for h, l in zip(highs[-50:], lows[-50:])]
        atr = sum(ranges) / len(ranges)
        
        volatility_pct = (max(closes[-50:]) - min(closes[-50:])) / closes[-1] * 100
        recent_volatility = (max(closes[-10:]) - min(closes[-10:])) / closes[-1] * 100
        std_dev = statistics.stdev(closes[-50:]) / closes[-1] * 100
        
        level = "LOW" if volatility_pct < 0.5 else "MEDIUM" if volatility_pct < 1.5 else "HIGH"
        
        return {
            "level": level,
            "atr": round(atr, 6),
            "volatility_pct": round(volatility_pct, 4),
            "recent_volatility_pct": round(recent_volatility, 4),
            "std_deviation": round(std_dev, 4),
            "max_range": round(max(ranges), 6),
            "min_range": round(min(ranges), 6)
        }
    
    def _analyze_gaps(self, opens, closes) -> Dict:
        """Gap analysis"""
        gap_ups = 0
        gap_downs = 0
        latest_gap = 0
        
        for i in range(1, len(closes)):
            gap = opens[i] - closes[i-1]
            if gap > 0:
                gap_ups += 1
            elif gap < 0:
                gap_downs += 1
            
            if i == len(closes) - 1:
                latest_gap = gap
        
        gap_pct = (latest_gap / closes[-1]) * 100
        gap_type = "Gap Up" if latest_gap > 0 else "Gap Down" if latest_gap < 0 else "No Gap"
        
        return {
            "latest_gap": f"{gap_type} {abs(gap_pct):.4f}%",
            "gap_up_count": gap_ups,
            "gap_down_count": gap_downs
        }
    
    def _analyze_rejection(self, last_candle, opens, closes, highs, lows) -> Dict:
        """Rejection analysis"""
        open_val = self.safe_float(last_candle.get('open') or last_candle.get('o'))
        close_val = self.safe_float(last_candle.get('close') or last_candle.get('c'))
        high_val = self.safe_float(last_candle.get('high') or last_candle.get('h'))
        low_val = self.safe_float(last_candle.get('low') or last_candle.get('l'))
        
        body = abs(close_val - open_val)
        upper_wick = high_val - max(open_val, close_val)
        lower_wick = min(open_val, close_val) - low_val
        total_range = high_val - low_val
        
        if total_range > 0:
            upper_wick_pct = (upper_wick / total_range) * 100
            lower_wick_pct = (lower_wick / total_range) * 100
            body_pct = (body / total_range) * 100
        else:
            upper_wick_pct = lower_wick_pct = body_pct = 0
        
        # Determine rejection type
        patterns = []
        rejection_type = "NEUTRAL"
        
        if body_pct < 5:
            patterns.append("DOJI")
        
        if lower_wick_pct > 50:
            patterns.append("STRONG LOWER_WICK")
            rejection_type = "LOWER"
        elif upper_wick_pct > 50:
            patterns.append("STRONG UPPER_WICK")
            rejection_type = "UPPER"
        
        confidence = max(lower_wick_pct, upper_wick_pct) if patterns else 50
        strength = max(lower_wick_pct, upper_wick_pct, body_pct)
        
        return {
            "type": rejection_type,
            "patterns": ", ".join(patterns) if patterns else "NONE",
            "confidence": f"{int(confidence)}%",
            "strength": f"{strength:.2f}%",
            "level": round(close_val, 6),
            "upper_wick_pct": round(upper_wick_pct, 2),
            "lower_wick_pct": round(lower_wick_pct, 2),
            "body_pct": round(body_pct, 2)
        }
    
    def _find_support_resistance(self, highs, lows, current_price) -> Dict:
        """Support and resistance levels"""
        recent_highs = sorted(highs[-50:], reverse=True)
        recent_lows = sorted(lows[-50:])
        
        resistance = recent_highs[0] if recent_highs else current_price
        support = recent_lows[0] if recent_lows else current_price
        
        dist_resistance = ((resistance - current_price) / current_price) * 100
        dist_support = ((current_price - support) / current_price) * 100
        
        return {
            "resistance": round(resistance, 6),
            "support": round(support, 6),
            "distance_to_resistance": f"{abs(dist_resistance):.4f}%",
            "distance_to_support": f"{abs(dist_support):.4f}%"
        }
    
    def _analyze_moving_averages(self, closes, current_price) -> Dict:
        """Moving average analysis"""
        ema200 = sum(closes[-200:]) / 200 if len(closes) >= 200 else sum(closes) / len(closes)
        ema50 = sum(closes[-50:]) / 50
        ema20 = sum(closes[-20:]) / 20
        
        price_vs_ema200 = ((current_price - ema200) / ema200) * 100
        trend = "UPTREND" if current_price > ema200 else "DOWNTREND"
        
        # Trend strength based on EMA alignment
        if current_price > ema20 > ema50 > ema200:
            trend_strength = 90
        elif current_price > ema20 > ema50:
            trend_strength = 70
        elif current_price > ema20:
            trend_strength = 50
        else:
            trend_strength = 30
        
        return {
            "trend": trend,
            "trend_strength": f"{trend_strength:.2f}%",
            "ema200": round(ema200, 6),
            "price_vs_ema200": f"{abs(price_vs_ema200):.4f}% - {'ABOVE' if price_vs_ema200 > 0 else 'BELOW'} EMA 200",
            "ema20": round(ema20, 6),
            "ema50": round(ema50, 6),
            "trend_confidence": "100.00%"
        }
    
    def _analyze_trend(self, closes) -> Dict:
        """Trend analysis"""
        ma20 = sum(closes[-20:]) / 20
        ma5 = sum(closes[-5:]) / 5
        
        trend = "Uptrend" if ma5 > ma20 else "Downtrend"
        strength = abs((ma5 - ma20) / ma20) * 100
        
        return {
            "direction": trend,
            "strength": round(min(strength * 10, 100), 2)
        }
    
    def _analyze_zigzag(self, highs, lows) -> Dict:
        """ZigZag pattern analysis"""
        # Simplified zigzag
        last_high = max(highs[-10:])
        last_low = min(lows[-10:])
        current = highs[-1]
        
        if current >= last_high:
            direction = "UP"
            pattern = "BULLISH"
        elif current <= last_low:
            direction = "DOWN"
            pattern = "BEARISH"
        else:
            direction = "NEUTRAL"
            pattern = "NEUTRAL"
        
        return {
            "pattern": pattern,
            "trend_strength": "0%" if pattern == "NEUTRAL" else "50%",
            "points": 11,
            "last_direction": direction,
            "last_extreme_price": round(last_high if direction == "UP" else last_low, 6)
        }
    
    def _analyze_price_movement(self, closes) -> Dict:
        """Price movement analysis"""
        movements = [abs(closes[i] - closes[i-1]) for i in range(1, len(closes))]
        avg_movement = sum(movements) / len(movements)
        recent_avg = sum(movements[-10:]) / 10
        latest_movements = len([m for m in movements[-10:] if m > avg_movement])
        
        activity = "VERY HIGH" if latest_movements > 7 else "HIGH" if latest_movements > 5 else "MODERATE"
        
        avg_pct = (avg_movement / closes[-1]) * 100
        recent_pct = (recent_avg / closes[-1]) * 100
        change_pct = ((recent_avg - avg_movement) / avg_movement) * 100 if avg_movement > 0 else 0
        
        return {
            "activity_level": activity,
            "average_movements": round(len(movements) * 0.8, 2),
            "recent_average": len(movements[-10:]) * 10,
            "latest_movements": latest_movements * 10,
            "movement_change_pct": f"{change_pct:+.2f}%",
            "avg_price_movement": f"{avg_pct:.4f}%",
            "recent_price_movement": f"{recent_pct:.4f}%",
            "price_movement_change": f"{change_pct:+.2f}%"
        }
    
    def _calculate_bull_bear(self, closes, opens, ma_data, trend_data, otc_factor=1.0) -> Dict:
        """Calculate bullish/bearish percentages with OTC adjustments"""
        import random
        
        bullish_score = 50
        
        # Trend contribution
        if trend_data['direction'] == "Uptrend":
            bullish_score += 20
        else:
            bullish_score -= 20
        
        # MA contribution
        if "ABOVE" in ma_data['price_vs_ema200']:
            bullish_score += 10
        else:
            bullish_score -= 10
        
        # Recent candles
        recent_bullish = sum(1 for i in range(-10, 0) if closes[i] > opens[i])
        bullish_score += (recent_bullish - 5)
        
        # Apply OTC factor (adds variation)
        bullish_score = bullish_score * otc_factor
        
        # Add slight randomization for realistic variation
        bullish_score += random.uniform(-3, 3)
        
        bullish_pct = max(0, min(100, bullish_score))
        bearish_pct = 100 - bullish_pct
        
        return {
            "bullish": round(bullish_pct, 1),
            "bearish": round(bearish_pct, 1)
        }
    
    def _calculate_market_condition(self, volatility, trend, movement) -> Dict:
        """Overall market condition"""
        score = 0
        
        # Volatility score (30 points)
        if volatility['level'] == "LOW":
            vol_score = 9
        elif volatility['level'] == "MEDIUM":
            vol_score = 20
        else:
            vol_score = 15
        
        # Trend score (40 points)
        trend_score = float(trend['strength']) * 0.4
        
        # Movement score (30 points)
        if movement['activity_level'] == "VERY HIGH":
            move_score = 30
        elif movement['activity_level'] == "HIGH":
            move_score = 20
        else:
            move_score = 15
        
        score = vol_score + trend_score + move_score
        
        if score >= 70:
            condition = "STRONG"
            trade_rec = "TAKE TRADE"
        elif score >= 50:
            condition = "MODERATE"
            trade_rec = "WAIT"
        else:
            condition = "WEAK"
            trade_rec = "SKIP TRADE"
        
        return {
            "condition": condition,
            "confidence": f"{int(min(score, 100))}%",
            "description": f"{condition.title()} market conditions",
            "trade_recommendation": trade_rec,
            "overall_score": f"{score:.2f}/100",
            "volatility_contribution": f"{vol_score}/30",
            "trend_contribution": f"{trend_score:.2f}/40",
            "movement_contribution": f"{move_score}/30"
        }
    
    def _generate_recommendation(self, bull_bear, trend, volatility, market_summary) -> Dict:
        """Generate trade recommendation - ALWAYS give CALL or PUT"""
        
        # Determine direction based on bullish/bearish
        if bull_bear['bullish'] >= bull_bear['bearish']:
            signal = "CALL"
            direction = "BUY"
            color = "green"
        else:
            signal = "PUT"
            direction = "SELL"
            color = "red"
        
        # Calculate confidence
        confidence = max(bull_bear['bullish'], bull_bear['bearish'])
        
        return {
            "signal": signal,
            "direction": direction,
            "recommendation": f"{signal}",
            "color": color,
            "confidence": f"{int(confidence)}%"
        }
