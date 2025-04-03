const mongoose = require('mongoose');

const commitmentSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    trim: true
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  category: {
    type: String,
    enum: ['personal', 'work', 'health', 'education', 'finance', 'other'],
    default: 'personal'
  },
  startDate: {
    type: Date,
    default: Date.now
  },
  endDate: {
    type: Date
  },
  frequency: {
    type: String,
    enum: ['daily', 'weekly', 'monthly', 'once'],
    default: 'daily'
  },
  completed: {
    type: Boolean,
    default: false
  },
  progress: {
    type: Number,
    min: 0,
    max: 100,
    default: 0
  },
  checkpoints: [{
    date: {
      type: Date,
      default: Date.now
    },
    status: {
      type: String,
      enum: ['completed', 'missed', 'postponed'],
      default: 'completed'
    },
    note: String
  }],
  priority: {
    type: String,
    enum: ['low', 'medium', 'high'],
    default: 'medium'
  },
  tags: [{
    type: String,
    trim: true
  }],
  isPublic: {
    type: Boolean,
    default: false
  }
}, {
  timestamps: true
});

// Index for faster queries
commitmentSchema.index({ userId: 1, category: 1 });
commitmentSchema.index({ userId: 1, completed: 1 });
commitmentSchema.index({ tags: 1 });

const Commitment = mongoose.model('Commitment', commitmentSchema);

module.exports = Commitment;