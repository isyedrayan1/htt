"""
Conversational AI Widget API
Intelligent racing assistant with global and contextual help
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
import json

from src.coaching.llm_client import GroqClient

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize LLM Client
llm_client = GroqClient()

class ChatMessage(BaseModel):
    message: str
    context: Dict[str, Any] = {}

@router.post("/chat")
async def chat_with_ai(chat_input: ChatMessage):
    """
    Conversational AI for racing insights with global and page-specific context
    """
    try:
        from db import query_to_df
        import pandas as pd
        
        message = chat_input.message
        context = chat_input.context
        
        # Fetch global fleet context for comprehensive answers
        global_context = {}
        try:
            # Get fleet summary
            fleet_query = """
                SELECT 
                    vehicle_id,
                    MIN(lap_time_ms) / 1000.0 as best_lap,
                    AVG(lap_time_ms) / 1000.0 as avg_lap,
                    COUNT(*) as lap_count
                FROM laps
                WHERE lap_number < 1000 AND lap_time_ms > 30000
                GROUP BY vehicle_id
                ORDER BY best_lap
            """
            fleet_df = query_to_df(fleet_query)
            
            if not fleet_df.empty:
                fastest_driver = fleet_df.iloc[0]
                global_context = {
                    "fastest_driver": fastest_driver['vehicle_id'],
                    "fastest_lap": f"{fastest_driver['best_lap']:.3f}s",
                    "total_drivers": len(fleet_df),
                    "top_3_drivers": fleet_df.head(3)[['vehicle_id', 'best_lap']].to_dict('records')
                }
        except Exception as e:
            logger.warning(f"Failed to fetch global context: {e}")
        
        # Merge global and page-specific context
        full_context = {**global_context, **context}
        
        # Enhanced system prompt with global knowledge
        system_prompt = f"""
You are the 'Antigravity Racing Assistant', an expert AI race engineer with comprehensive knowledge of the entire fleet.

GLOBAL FLEET DATA:
- Fastest Driver: {global_context.get('fastest_driver', 'Unknown')} ({global_context.get('fastest_lap', 'N/A')})
- Total Drivers: {global_context.get('total_drivers', 'Unknown')}
- Top 3: {json.dumps(global_context.get('top_3_drivers', []))}

CURRENT PAGE CONTEXT:
{json.dumps(context, indent=2)}

CAPABILITIES:
1. Answer questions about ANY driver or fleet-wide data (you have global knowledge)
2. Explain platform features (DPTAD, SIWTL, Evidence Explorer, etc.)
3. Provide racing insights (braking, racing lines, telemetry analysis)
4. Help users navigate the platform based on their current page

RULES:
- If asked about "fastest driver" or fleet stats, use the GLOBAL DATA above
- If on a specific page, provide page-relevant suggestions
- Keep responses concise (2-3 sentences) unless detail is requested
- Be encouraging and professional
- Always provide actionable insights
"""
        
        if llm_client.client:
            completion = llm_client.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=300,
                top_p=1,
                stream=False
            )
            response_text = completion.choices[0].message.content
            
            # Generate smart suggestions based on question
            suggestions = generate_smart_suggestions(message, context.get('page', 'Dashboard'), global_context)
        else:
            # Fallback with global context
            if 'fastest' in message.lower() and global_context.get('fastest_driver'):
                response_text = f"The fastest driver is {global_context['fastest_driver']} with a lap time of {global_context['fastest_lap']}!"
                suggestions = ["How can they improve?", "Show sector breakdown", "Compare with others"]
            else:
                response_text = "I'm currently in offline mode (No Groq API Key). However, I can help with basic queries!"
                suggestions = ["Analyze lap times", "Explain DPTAD", "Compare drivers"]

        return {
            "type": "ai_response",
            "message": response_text,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Chat AI failed: {e}")
        return {
            "type": "error",
            "message": "I'm having trouble connecting to my brain right now. Try asking about 'lap times' or 'DPTAD'.",
            "suggestions": ["Lap times", "DPTAD", "Help"]
        }


def generate_smart_suggestions(question: str, page: str, global_context: dict) -> List[str]:
    """Generate contextual suggestions based on question and page"""
    lower_q = question.lower()
    
    # Question-based suggestions
    if 'fastest' in lower_q or 'best' in lower_q:
        return ["How can they improve?", "Show sector breakdown", "Compare with others"]
    elif 'compare' in lower_q:
        return ["Sector analysis", "Consistency comparison", "Lap progression"]
    elif 'consistency' in lower_q:
        return ["What causes variance?", "Show lap times", "Coaching tips"]
    elif 'sector' in lower_q:
        return ["Analyze telemetry", "Compare sectors", "Optimal racing line"]
    elif 'dptad' in lower_q or 'anomaly' in lower_q:
        return ["Explain anomalies", "How to fix?", "Impact on performance"]
    elif 'siwtl' in lower_q or 'theoretical' in lower_q:
        return ["How is it calculated?", "Achievability score", "Sector weights"]
    
    # Page-based fallback suggestions
    page_suggestions = {
        'Dashboard': ["Who's the fastest?", "Fleet consistency", "Top performers"],
        'Driver Analysis': ["DPTAD analysis", "Coaching tips", "Lap consistency"],
        'Compare': ["Sector comparison", "Who's improving?", "Consistency gap"],
        'Evidence Explorer': ["Explain telemetry", "Sector breakdown", "Anomaly details"],
        'Strategy Center': ["Pit strategy", "Tire management", "Race tactics"]
    }
    
    return page_suggestions.get(page, ["Analyze performance", "Show insights", "Help me understand"])


@router.get("/help/topics")
async def get_help_topics():
    """
    Get available help topics and AI capabilities
    """
    return {
        "ai_assistant": "ANTIGRAVITY Racing Intelligence Assistant",
        "capabilities": [
            "Driver performance analysis",
            "Lap time insights",
            "ML algorithm explanations (DPTAD, SIWTL)",
            "Telemetry data interpretation",
            "Sector timing analysis",
            "Weather impact assessment",
            "Performance comparisons",
            "Platform navigation help"
        ]
    }


@router.get("/context/{vehicle_id}")
async def get_driver_context(vehicle_id: str):
    """
    Get contextual information about a specific driver for AI assistance
    """
    try:
        from db import query_to_dict
        
        context_query = f"""
            SELECT 
                d.driver_id,
                d.vehicle_number,
                d.vehicle_class,
                COUNT(l.lap_number) as total_laps,
                MIN(l.lap_time_ms) / 1000.0 as best_lap
            FROM drivers d
            LEFT JOIN laps l ON d.vehicle_id = l.vehicle_id
            WHERE d.vehicle_id = '{vehicle_id}'
            GROUP BY d.driver_id, d.vehicle_number, d.vehicle_class
        """
        
        context_data = query_to_dict(context_query)
        
        if context_data:
            driver = context_data[0]
            return {
                "vehicle_id": vehicle_id,
                "context": driver
            }
        else:
            return {
                "vehicle_id": vehicle_id,
                "context": {}
            }
            
    except Exception as e:
        logger.error(f"Driver context failed: {e}")
        return {
            "vehicle_id": vehicle_id,
            "context": {},
            "error": str(e)
        }