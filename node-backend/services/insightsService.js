const Call = require('../models/Call');

const getOverview = async () => {
  try {
    const totalCalls = await Call.countDocuments();
    if (totalCalls === 0) return { totalCalls: 0, highRiskPercentage: 0, escalationRate: 0 };
    
    const highRiskCalls = await Call.countDocuments({ 'ai_logs.risk': 'HIGH' });
    const escalatedCalls = await Call.countDocuments({ final_outcome: 'escalated' });
    
    return {
      totalCalls,
      highRiskPercentage: (highRiskCalls / totalCalls) * 100,
      escalationRate: (escalatedCalls / totalCalls) * 100
    };
  } catch (error) {
    console.error(error);
    return { error: 'Failed to generate overview insights' };
  }
};

const getCommonHighRiskPhrases = async () => {
    try {
      const results = await Call.aggregate([
        { $match: { 'ai_logs.risk': 'HIGH' } },
        { $unwind: '$phrases' },
        { $group: { _id: '$phrases', count: { $sum: 1 } } },
        { $sort: { count: -1 } },
        { $limit: 10 }
      ]);
      return results.map(r => ({ phrase: r._id, prob: 'Unknown', occurrences: r.count }));
    } catch (error) {
       console.error(error);
       return [];
    }
};

const getResponseEffectiveness = async () => {
  try {
    const results = await Call.aggregate([
      { $unwind: '$operator_actions' },
      {
         $group: {
           _id: '$operator_actions.action',
           total: { $sum: 1 },
           calmed: { $sum: { $cond: [{ $eq: ['$final_outcome', 'calmed'] }, 1, 0] } }
         }
      },
      {
         $project: {
            action: '$_id',
            successRate: { $multiply: [{ $divide: ['$calmed', '$total'] }, 100] }
         }
      },
      { $sort: { successRate: -1 } }
    ]);
    return results;
  } catch (error) {
    console.error(error);
    return [];
  }
};

const getResourceEffectiveness = async () => {
   try {
     const results = await Call.aggregate([
       { $match: { resource_used: { $ne: '', $exists: true } } },
       {
         $group: {
           _id: '$resource_used',
           totalReferred: { $sum: 1 },
           completed: { $sum: { $cond: [{ $eq: ['$follow_through', true] }, 1, 0] } }
         }
       },
       {
         $project: {
           resource: '$_id',
           followThroughRate: { $multiply: [{ $divide: ['$completed', '$totalReferred'] }, 100] }
         }
       }
     ]);
     return results;
   } catch (error) {
     console.error(error);
     return [];
   }
};

module.exports = {
  getOverview,
  getCommonHighRiskPhrases,
  getResponseEffectiveness,
  getResourceEffectiveness
};
