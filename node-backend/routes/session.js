const express = require('express');
const router = express.Router();
const Call = require('../models/Call');

// Layer 5: Replay System
router.get('/:id/replay', async (req, res) => {
  try {
    const { id } = req.params;
    const callDoc = await Call.findOne({ session_id: id });
    
    if (!callDoc) {
      return res.status(404).json({ error: 'Session not found' });
    }
    
    const events = [];
    
    callDoc.ai_logs.forEach(log => {
      events.push({ type: 'ai_log', data: log.toObject() });
    });
    
    callDoc.operator_actions.forEach(action => {
      events.push({ type: 'operator_action', data: action.toObject() });
    });
    
    // Sort chronology
    events.sort((a, b) => new Date(a.data.timestamp) - new Date(b.data.timestamp));
    
    res.json({ session_id: id, replay: events });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to generate replay' });
  }
});

// Layer 5: Privacy & Compliance - Right to erasure
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await Call.deleteOne({ session_id: id });
    if (result.deletedCount === 0) {
       return res.status(404).json({ error: 'Session not found' });
    }
    res.json({ message: 'Session data successfully deleted' });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to delete session' });
  }
});

module.exports = router;
