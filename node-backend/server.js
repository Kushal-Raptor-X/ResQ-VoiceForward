require('dotenv').config();
const express = require('express');
const cors = require('cors');
const connectDB = require('./config/db');

const analyzeRoutes = require('./routes/analyze');
const insightsRoutes = require('./routes/insights');
const sessionRoutes = require('./routes/session');

const app = express();
const PORT = process.env.PORT || 3000;

// Connect to MongoDB
connectDB();

app.use(cors());
app.use(express.json());

app.use('/analyze', analyzeRoutes);
app.use('/insights', insightsRoutes);
app.use('/session', sessionRoutes);

app.get('/', (req, res) => res.json({ status: 'VoiceForward Node Backend Running' }));

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
