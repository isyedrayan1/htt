"""
Groq LLM Client for AI-powered coaching and chat
"""
import os
from groq import Groq
import logging

logger = logging.getLogger(__name__)

class GroqClient:
    """Client for interacting with Groq's LLaMA models"""
    
    def __init__(self):
        """Initialize Groq client with API key from environment"""
        api_key = os.getenv("GROQ_API_KEY")
        
        if api_key:
            try:
                self.client = Groq(api_key=api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
                self.client = None
        else:
            logger.warning("GROQ_API_KEY not found in environment - AI features will use fallback")
            self.client = None
    
    def generate_coaching_report(self, driver_data: dict, analysis_data: dict) -> dict:
        """
        Generate AI coaching report using LLaMA 3.3
        
        Args:
            driver_data: Driver performance metrics
            analysis_data: DPTAD and SIWTL analysis results
            
        Returns:
            dict with coaching recommendations
        """
        if not self.client:
            return self._fallback_coaching(driver_data, analysis_data)
        
        try:
            # Build comprehensive prompt
            prompt = self._build_coaching_prompt(driver_data, analysis_data)
            
            # Call LLaMA 3.3
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert race engineer providing coaching to professional drivers. Be specific, actionable, and encouraging."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500,
                top_p=1,
                stream=False
            )
            
            response_text = completion.choices[0].message.content
            
            return {
                "coaching_text": response_text,
                "generated_by": "AI (Groq LLaMA 3.3)",
                "model": "llama-3.3-70b-versatile"
            }
            
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            return self._fallback_coaching(driver_data, analysis_data)
    
    def _build_coaching_prompt(self, driver_data: dict, analysis_data: dict) -> str:
        """Build detailed coaching prompt from data"""
        
        prompt = f"""Analyze this driver's performance and provide coaching:

DRIVER METRICS:
- Best Lap: {driver_data.get('best_lap', 'N/A')}s
- Average Lap: {driver_data.get('avg_lap', 'N/A')}s
- Consistency: {driver_data.get('consistency_score', 'N/A')}%

DPTAD ANALYSIS:
- Brake Smoothness: {analysis_data.get('dptad', {}).get('brake_smoothness', 'N/A')}
- Throttle Smoothness: {analysis_data.get('dptad', {}).get('throttle_smoothness', 'N/A')}
- Anomalies Detected: {analysis_data.get('dptad', {}).get('anomaly_count', 0)}

SIWTL TARGET:
- Theoretical Best: {analysis_data.get('siwtl', {}).get('siwtl_lap', 'N/A')}s
- Potential Gain: {analysis_data.get('siwtl', {}).get('potential_gain_sec', 'N/A')}s
- Achievability: {analysis_data.get('siwtl', {}).get('achievability_score', 'N/A')}

Provide 3-4 specific, actionable coaching tips to help this driver improve. Focus on technique, consistency, and achievable gains."""
        
        return prompt
    
    def _fallback_coaching(self, driver_data: dict, analysis_data: dict) -> dict:
        """Fallback coaching when AI is unavailable"""
        
        consistency = driver_data.get('consistency_score', 0)
        potential_gain = analysis_data.get('siwtl', {}).get('potential_gain_sec', 0)
        
        tips = []
        
        if consistency < 85:
            tips.append("Focus on consistency - your lap time variance suggests room for improvement in repeatable performance.")
        
        if potential_gain > 0.5:
            tips.append(f"You have {potential_gain:.3f}s of potential gain available. Focus on executing your best sectors together.")
        
        brake_smoothness = analysis_data.get('dptad', {}).get('brake_smoothness', 1.0)
        if brake_smoothness < 0.8:
            tips.append("Work on brake application smoothness - detected some harsh braking events.")
        
        if not tips:
            tips.append("Maintain your current performance level and focus on consistency.")
        
        coaching_text = "\n\n".join([f"{i+1}. {tip}" for i, tip in enumerate(tips)])
        
        return {
            "coaching_text": coaching_text,
            "generated_by": "Rule-based fallback",
            "model": "fallback"
        }
    
    def generate_coaching_advice(self, evidence_pack: dict) -> dict:
        """
        Generate coaching advice from evidence pack
        
        Args:
            evidence_pack: Dict with potential, consistency, and technique data
            
        Returns:
            dict with summary, key_strength, primary_weakness, actionable_advice, drill
        """
        if not self.client:
            return self._fallback_advice(evidence_pack)
        
        try:
            prompt = f"""Analyze this driver's performance data and provide coaching:

POTENTIAL:
- Potential Gain: {evidence_pack['potential']['potential_gain_sec']}s
- Theoretical Best: {evidence_pack['potential']['theoretical_best']}s
- Achievability: {evidence_pack['potential']['achievability']}

CONSISTENCY:
- Total Anomalies: {evidence_pack['consistency']['total_anomalies']}
- Brake Spikes: {evidence_pack['consistency']['brake_spikes']}
- Throttle Drops: {evidence_pack['consistency']['throttle_drops']}

TECHNIQUE:
- Brake Smoothness: {evidence_pack['technique']['brake_smoothness']}
- Throttle Smoothness: {evidence_pack['technique']['throttle_smoothness']}

Provide:
1. A brief summary (1 sentence)
2. Key strength (1 sentence)
3. Primary weakness (1 sentence)
4. 3 actionable tips
5. One specific drill to practice"""

            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert race engineer. Be specific and actionable."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400,
                stream=False
            )
            
            response_text = completion.choices[0].message.content
            
            # Parse response (simple approach - could be improved)
            lines = [l.strip() for l in response_text.split('\n') if l.strip()]
            
            return {
                "summary": lines[0] if lines else "Driver showing good potential",
                "key_strength": lines[1] if len(lines) > 1 else "Consistent performance",
                "primary_weakness": lines[2] if len(lines) > 2 else "Minor technique refinements needed",
                "actionable_advice": lines[3:6] if len(lines) > 3 else ["Focus on consistency", "Smooth inputs", "Optimize racing line"],
                "drill": lines[6] if len(lines) > 6 else "Practice threshold braking in Turn 1"
            }
            
        except Exception as e:
            logger.error(f"Groq coaching advice failed: {e}")
            return self._fallback_advice(evidence_pack)
    
    def _fallback_advice(self, evidence_pack: dict) -> dict:
        """Fallback coaching advice when AI unavailable"""
        
        potential_gain = evidence_pack['potential']['potential_gain_sec']
        brake_smoothness = evidence_pack['technique']['brake_smoothness']
        throttle_smoothness = evidence_pack['technique']['throttle_smoothness']
        
        advice = []
        weakness = "General technique refinement"
        strength = "Solid baseline performance"
        
        if potential_gain > 0.5:
            weakness = "Inconsistent sector execution"
            advice.append(f"Focus on achieving your best sectors together - {potential_gain:.2f}s available")
        
        if brake_smoothness < 0.8:
            weakness = "Brake application technique"
            advice.append("Work on progressive brake application to avoid spikes")
            strength = "Good throttle control"
        
        if throttle_smoothness < 0.8:
            weakness = "Throttle modulation"
            advice.append("Practice smoother throttle application through corners")
            strength = "Good braking technique"
        
        if not advice:
            advice = ["Maintain current performance", "Focus on consistency", "Optimize racing line"]
        
        return {
            "summary": f"Driver has {potential_gain:.2f}s of potential gain available",
            "key_strength": strength,
            "primary_weakness": weakness,
            "actionable_advice": advice[:3],
            "drill": "Practice consistent lap times within 0.2s variance"
        }
