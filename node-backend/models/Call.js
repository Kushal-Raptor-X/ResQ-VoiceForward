const mongoose = require('mongoose');

const callSchema = new mongoose.Schema({
  session_id: { type: String, required: true, unique: true },
  transcript: { type: String, default: '' },
  phrases: [{ type: String }],
  timeline: [{
    minute: Number,
    risk: String,
    phrases: [{ type: String }],
    confidence: Number
  }],
  ai_logs: [{
    timestamp: { type: Date, default: Date.now },
    risk: String,
    confidence: Number,
    reasoning: [{ type: String }],
    operator_action: { type: String, default: '' }
  }],
  operator_actions: [{
    suggestion: String,
    action: String,
    timestamp: { type: Date, default: Date.now }
  }],
  final_outcome: { type: String, enum: ['calmed', 'escalated', 'unknown'], default: 'unknown' },
  resource_used: { type: String, default: '' },
  follow_through: { type: Boolean, default: false },
  created_at: { type: Date, default: Date.now },
  ai_assisted: { type: Boolean, default: true } // AI disclosure & control (Layer 5)
});

const Call = mongoose.model('Call', callSchema);
module.exports = Call;
