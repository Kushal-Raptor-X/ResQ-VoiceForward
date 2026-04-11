const express = require('express');
const router = express.Router();
const analysisService = require('../services/analysisService');

router.post('/', async (req, res) => {
  try {
    const { transcript, session_id } = req.body;
    // API responds even if DB fails internally via non-blocking catches inside the service
    const result = await analysisService.processAnalysis(transcript, session_id);
    res.json(result);
  } catch (error) {
    console.error('Error in /analyze endpoint:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

module.exports = router;
