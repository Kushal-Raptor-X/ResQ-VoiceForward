const { logAIEvent } = require('./logService');
const Call = require('../models/Call');
const { v4: uuidv4 } = require('uuid');

const extractPhrases = (text) => {
    if (!text) return [];
    const words = text.replace(/[^\w\s]/gi, '').toLowerCase().split(' ');
    return words.filter(w => w.length > 5).slice(0, 5); 
};

const processAnalysis = async (transcript, session_idInput = null) => {
  let session_id = session_idInput;

  // Layer 5 session Initialization (no PII, UUID)
  if (!session_id) {
    session_id = uuidv4();
    try {
      await Call.create({ session_id, transcript, phrases: [], timeline: [] });
    } catch (e) {
      console.error('Initial DB creation failed, but continuing for degradation... ', e);
    }
  } else {
    try {
      await Call.findOneAndUpdate({ session_id }, { transcript }, { upsert: true });
    } catch(e) {}
  }

  // Layer 5: AI Disclosure check
  let isAiAssisted = true;
  try {
    const callDoc = await Call.findOne({ session_id });
    if (callDoc && callDoc.ai_assisted === false) {
       isAiAssisted = false;
    }
  } catch(e) {}
  
  if (!isAiAssisted) {
     return {
        session_id,
        risk: 'N/A',
        confidence: 0,
        reasoning: ['AI assistance opted out by user.'],
        insights: {}
     };
  }
  
  // Layer 5: STT Failure Mode check
  if (!transcript || transcript.trim().length === 0) {
     const fallbackRisk = 'UNKNOWN';
     const fallbackConfidence = 0.0;
     const fallbackReasoning = ['STT Failure: Empty transcript or low confidence.'];
     
     await logAIEvent(session_id, {
         risk: fallbackRisk,
         confidence: fallbackConfidence,
         reasoning: fallbackReasoning,
         operator_action: 'WARNING_ISSUED'
     });
     
     return {
       session_id,
       risk: fallbackRisk,
       confidence: fallbackConfidence,
       reasoning: fallbackReasoning,
       insights: {
         similar_case_risk: 'UNKNOWN',
         best_response_success: 'NA'
       }
     };
  }

  // Graceful degradation / rule-based fallback
  let risk = 'LOW';
  let confidence = 0.95;
  let reasoning = ['Routine call detected based on vocabulary.'];
  
  const lowerTranscript = transcript.toLowerCase();
  
  if (lowerTranscript.includes("emergency") || lowerTranscript.includes("help")) {
    risk = 'HIGH';
    confidence = 0.88;
    reasoning = ['Critical keywords detected: emergency protocols may be needed.'];
  }
  
  // Layer 5: Emotion Mismatch fallback (pseudo-logic based on keywords)
  if (lowerTranscript.includes("calm down") && lowerTranscript.includes("angry")) {
    risk = 'HIGH';
    confidence = 0.99;
    reasoning = ['Emotion Mismatch: Language conflicts with expressed tone. Defaulting to HIGH risk.'];
  }

  const phrases = extractPhrases(transcript);
  
  await logAIEvent(session_id, { risk, confidence, reasoning, operator_action: '' });
  
  try {
     await Call.findOneAndUpdate({ session_id }, { $addToSet: { phrases: { $each: phrases } } });
  } catch (err) {}
  
  return {
    session_id,
    risk,
    confidence,
    reasoning,
    insights: {
      similar_case_risk: risk,
      best_response_success: '85%'
    }
  };
};

module.exports = { processAnalysis };
