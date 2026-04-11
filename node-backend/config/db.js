const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    // Disable buffering so that if DB is down, operations fail immediately and are caught, allowing graceful degradation
    mongoose.set('bufferCommands', false);
    const conn = await mongoose.connect(process.env.MONGO_URI, {
       serverSelectionTimeoutMS: 5000
    });
    console.log(`MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    console.error(`Error connecting to MongoDB (Non-blocking): ${error.message}`);
    // DO NOT process.exit(1), allow app to run and degrade gracefully
  }
};

module.exports = connectDB;
