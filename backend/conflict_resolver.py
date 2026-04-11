"""
Multi-Agent Conflict Resolution & Explainable Decision Engine
Handles conflict resolution between multiple AI agents analyzing crisis calls
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentOutput:
    level: str
    signals: List[str]
    reasoning: str
    confidence: int


@dataclass
class ResolvedDecision:
    final_risk: str
    confidence_summary: str
    uncertainty: bool
    explanation: str
    contributing_factors: List[str]
    conflicting_signals: List[str]
    agent_votes: Dict[str, str]
    weighted_score: float


class ConflictResolver:
    """Resolves conflicts between multiple AI agents with full explainability"""
    
    RISK_VALUES = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4
    }
    
    AGENT_NAMES = {
        "language_agent": "Language Agent",
        "emotion_agent": "Emotion Agent",
        "audio_agent": "Ambient Audio Agent",
        "narrative_agent": "Narrative Agent"
    }
    
    def resolve(self, agent_outputs: Dict[str, Dict[str, Any]]) -> ResolvedDecision:
        """
        Main resolution logic with full explainability
        
        Args:
            agent_outputs: Dictionary of agent outputs with structure:
                {
                    "language_agent": {
                        "level": "HIGH",
                        "signals": ["I've decided"],
                        "reasoning": "Finality language detected",
                        "confidence": 82
                    },
                    ...
                }
        
        Returns:
            ResolvedDecision with final risk level and full explanation
        """
        # Parse agent outputs
        agents = {}
        for key, data in agent_outputs.items():
            agents[key] = AgentOutput(**data)
        
        # Calculate weighted scores
        weighted_score = self._calculate_weighted_score(agents)
        
        # Get majority agreement
        risk_levels = [agent.level for agent in agents.values()]
        majority_level = self._get_majority(risk_levels)
        
        # Detect conflicts
        has_conflict = self._detect_conflict(risk_levels)
        
        # Apply safety-first rules
        final_risk = self._apply_safety_rules(risk_levels, majority_level, has_conflict)
        
        # Detect uncertainty
        uncertainty = self._detect_uncertainty(agents, risk_levels)
        
        # Generate explanation
        explanation = self._generate_explanation(agents, final_risk, has_conflict, uncertainty)
        
        # Extract contributing factors
        contributing_factors = self._extract_contributing_factors(agents, final_risk)
        
        # Identify conflicting signals
        conflicting_signals = self._identify_conflicting_signals(agents, has_conflict)
        
        # Confidence summary
        confidence_summary = self._calculate_confidence_summary(agents, uncertainty)
        
        # Agent votes
        agent_votes = {self.AGENT_NAMES[k]: v.level for k, v in agents.items()}
        
        return ResolvedDecision(
            final_risk=final_risk,
            confidence_summary=confidence_summary,
            uncertainty=uncertainty,
            explanation=explanation,
            contributing_factors=contributing_factors,
            conflicting_signals=conflicting_signals,
            agent_votes=agent_votes,
            weighted_score=weighted_score
        )
    
    def _calculate_weighted_score(self, agents: Dict[str, AgentOutput]) -> float:
        """Calculate weighted risk score based on confidence"""
        total_weight = 0
        weighted_sum = 0
        
        for agent in agents.values():
            risk_value = self.RISK_VALUES[agent.level]
            confidence = agent.confidence / 100.0
            weighted_sum += risk_value * confidence
            total_weight += confidence
        
        return weighted_sum / total_weight if total_weight > 0 else 0
    
    def _get_majority(self, risk_levels: List[str]) -> str:
        """Get the most common risk level"""
        from collections import Counter
        counts = Counter(risk_levels)
        return counts.most_common(1)[0][0]
    
    def _detect_conflict(self, risk_levels: List[str]) -> bool:
        """Detect if agents have conflicting assessments"""
        unique_levels = set(risk_levels)
        
        # Conflict if HIGH and LOW both present
        if "HIGH" in unique_levels and "LOW" in unique_levels:
            return True
        
        # Conflict if CRITICAL and LOW/MEDIUM both present
        if "CRITICAL" in unique_levels and ("LOW" in unique_levels or "MEDIUM" in unique_levels):
            return True
        
        # Conflict if more than 2 different levels
        if len(unique_levels) > 2:
            return True
        
        return False
    
    def _apply_safety_rules(self, risk_levels: List[str], majority: str, has_conflict: bool) -> str:
        """Apply safety-first rules to determine final risk"""
        unique_levels = set(risk_levels)
        
        # Rule 1: If CRITICAL present, always escalate
        if "CRITICAL" in unique_levels:
            return "CRITICAL"
        
        # Rule 2: If conflict with HIGH present, default to HIGH
        if has_conflict and "HIGH" in unique_levels:
            return "HIGH"
        
        # Rule 3: If majority is HIGH, return HIGH
        if majority == "HIGH":
            return "HIGH"
        
        # Rule 4: If mixed MEDIUM/HIGH, lean HIGH
        if "HIGH" in unique_levels and "MEDIUM" in unique_levels and "LOW" not in unique_levels:
            return "HIGH"
        
        # Rule 5: If all LOW, return LOW
        if all(level == "LOW" for level in risk_levels):
            return "LOW"
        
        # Default to majority
        return majority
    
    def _detect_uncertainty(self, agents: Dict[str, AgentOutput], risk_levels: List[str]) -> bool:
        """Detect if there's significant uncertainty in the assessment"""
        # Check for strong disagreement
        unique_levels = set(risk_levels)
        if len(unique_levels) >= 3:
            return True
        
        # Check for wide confidence variance
        confidences = [agent.confidence for agent in agents.values()]
        if max(confidences) - min(confidences) > 30:
            return True
        
        # Check for low average confidence
        avg_confidence = sum(confidences) / len(confidences)
        if avg_confidence < 60:
            return True
        
        return False
    
    def _generate_explanation(
        self, 
        agents: Dict[str, AgentOutput], 
        final_risk: str, 
        has_conflict: bool,
        uncertainty: bool
    ) -> str:
        """Generate plain-language explanation of the decision"""
        explanation_parts = []
        
        # Opening statement
        explanation_parts.append(f"I'm flagging {final_risk} risk because:")
        
        # Contributing factors from each agent
        for key, agent in agents.items():
            agent_name = self.AGENT_NAMES[key]
            if agent.level in ["HIGH", "CRITICAL", "MEDIUM"]:
                signals_text = ", ".join([f"'{s}'" for s in agent.signals[:2]])
                explanation_parts.append(
                    f"• The {agent_name} detected {signals_text} — {agent.reasoning.lower()}"
                )
        
        # Uncertainty section
        if uncertainty or has_conflict:
            explanation_parts.append("\nThere is some uncertainty because:")
            
            # Find dissenting agents
            for key, agent in agents.items():
                agent_name = self.AGENT_NAMES[key]
                if agent.level == "LOW" and final_risk in ["HIGH", "CRITICAL"]:
                    explanation_parts.append(
                        f"• The {agent_name} did not detect strong risk signals"
                    )
            
            # Confidence variance
            confidences = [agent.confidence for agent in agents.values()]
            if max(confidences) - min(confidences) > 30:
                explanation_parts.append(
                    "• Confidence levels vary significantly across agents"
                )
            
            # Safety default
            if has_conflict:
                explanation_parts.append(
                    f"• Due to conflicting signals, the system is defaulting to {final_risk} risk as a safety measure"
                )
        
        return "\n".join(explanation_parts)
    
    def _extract_contributing_factors(self, agents: Dict[str, AgentOutput], final_risk: str) -> List[str]:
        """Extract key contributing factors for bullet point display"""
        factors = []
        
        for agent in agents.values():
            if agent.level in ["HIGH", "CRITICAL", "MEDIUM"]:
                factors.append(agent.reasoning)
        
        return factors[:5]  # Limit to top 5
    
    def _identify_conflicting_signals(self, agents: Dict[str, AgentOutput], has_conflict: bool) -> List[str]:
        """Identify which signals are conflicting"""
        if not has_conflict:
            return []
        
        conflicts = []
        risk_levels = [agent.level for agent in agents.values()]
        
        if "HIGH" in risk_levels and "LOW" in risk_levels:
            conflicts.append("Some agents indicate HIGH risk while others indicate LOW")
        
        if len(set(risk_levels)) > 2:
            conflicts.append("Agents disagree across multiple risk levels")
        
        return conflicts
    
    def _calculate_confidence_summary(self, agents: Dict[str, AgentOutput], uncertainty: bool) -> str:
        """Calculate overall confidence summary"""
        avg_confidence = sum(agent.confidence for agent in agents.values()) / len(agents)
        
        if uncertainty:
            return "UNCERTAIN"
        elif avg_confidence >= 80:
            return "HIGH"
        elif avg_confidence >= 60:
            return "MODERATE"
        else:
            return "LOW"


# Example usage
if __name__ == "__main__":
    resolver = ConflictResolver()
    
    test_input = {
        "language_agent": {
            "level": "HIGH",
            "signals": ["I've decided", "final statements"],
            "reasoning": "Finality language detected",
            "confidence": 82
        },
        "emotion_agent": {
            "level": "MEDIUM",
            "signals": ["flat tone"],
            "reasoning": "Low emotional variation",
            "confidence": 65
        },
        "audio_agent": {
            "level": "LOW",
            "signals": ["quiet background"],
            "reasoning": "No distress audio cues",
            "confidence": 70
        },
        "narrative_agent": {
            "level": "HIGH",
            "signals": ["story conclusion pattern"],
            "reasoning": "Narrative reaching endpoint",
            "confidence": 78
        }
    }
    
    result = resolver.resolve(test_input)
    print(f"Final Risk: {result.final_risk}")
    print(f"Confidence: {result.confidence_summary}")
    print(f"Uncertainty: {result.uncertainty}")
    print(f"\nExplanation:\n{result.explanation}")
