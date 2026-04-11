const express = require('express');
const router = express.Router();
const insightsService = require('../services/insightsService');

router.get('/overview', async (req, res) => {
  try {
    const data = await insightsService.getOverview();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Server Error' });
  }
});

router.get('/phrases', async (req, res) => {
  try {
    const data = await insightsService.getCommonHighRiskPhrases();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Server Error' });
  }
});

router.get('/responses', async (req, res) => {
  try {
    const data = await insightsService.getResponseEffectiveness();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Server Error' });
  }
});

router.get('/resources', async (req, res) => {
  try {
    const data = await insightsService.getResourceEffectiveness();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Server Error' });
  }
});

module.exports = router;
