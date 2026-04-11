"""Decision agent for risk assessment and routing."""

def decide(rule, ml, context):
    """
    Make decision based on rule, ML, and context signals.
    
    Args:
        rule: Output from rule_agent.detect (None or "CRITICAL")
        ml: Output from ml_agent.classify (dict with label/confidence)
        context: List of previous messages from context_agent.get
    
    Returns:
        dict with risk level and whether to call LLM
    """
    
    # Rule-based override
    if rule == "CRITICAL":
        return {"risk": "CRITICAL", "call_llm": True}
    
    # ML confidence thresholds
    score = ml["confidence"]
    
    if score > 0.8:
        return {"risk": "HIGH", "call_llm": True}
    
    if score > 0.5:
        return {"risk": "MEDIUM", "call_llm": False}
    
    return {"risk": "LOW", "call_llm": False}
