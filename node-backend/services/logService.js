const Call = require('../models/Call');

/**
 * Append-only logging
 * Store AI output with reasoning and confidence
 */
const logAIEvent = async (session_id, data) => {
  try {
    const { risk, confidence, reasoning, operator_action } = data;
    
    // append-only (never overwrite logs)
    await Call.findOneAndUpdate(
      { session_id },
      { 
        $push: { 
          ai_logs: { timestamp: new Date(), risk, confidence, reasoning, operator_action } 
        }
      },
      { new: true, upsert: true }
    );
  } catch (error) {
    console.error('Error logging AI Event (Non-blocking):', error);
  }
};

module.exports = {
  logAIEvent
};
