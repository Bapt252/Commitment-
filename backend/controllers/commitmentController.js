const { Commitment } = require('../models');

// Create new commitment
exports.create = async (req, res) => {
  try {
    const { 
      title, description, category, startDate, 
      endDate, frequency, priority, tags, isPublic 
    } = req.body;

    const newCommitment = new Commitment({
      title,
      description,
      userId: req.user.id,
      category,
      startDate: startDate || Date.now(),
      endDate,
      frequency,
      priority,
      tags,
      isPublic
    });

    const savedCommitment = await newCommitment.save();

    res.status(201).json({
      success: true,
      message: 'Commitment created successfully',
      commitment: savedCommitment
    });
    
  } catch (error) {
    console.error('Commitment creation error:', error);
    res.status(500).json({
      success: false,
      message: 'Error creating commitment',
      error: error.message
    });
  }
};

// Get all commitments for a user
exports.getAllForUser = async (req, res) => {
  try {
    const { category, completed, sort = 'createdAt', order = 'desc' } = req.query;
    
    // Build query
    const query = { userId: req.user.id };
    
    if (category) {
      query.category = category;
    }
    
    if (completed !== undefined) {
      query.completed = completed === 'true';
    }
    
    // Build sort options
    const sortOptions = {};
    sortOptions[sort] = order === 'asc' ? 1 : -1;
    
    const commitments = await Commitment.find(query)
      .sort(sortOptions)
      .exec();

    res.status(200).json({
      success: true,
      count: commitments.length,
      commitments
    });
    
  } catch (error) {
    console.error('Commitment fetch error:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching commitments',
      error: error.message
    });
  }
};

// Get a single commitment
exports.getById = async (req, res) => {
  try {
    const commitment = await Commitment.findOne({ 
      _id: req.params.id,
      userId: req.user.id
    });

    if (!commitment) {
      return res.status(404).json({
        success: false,
        message: 'Commitment not found'
      });
    }

    res.status(200).json({
      success: true,
      commitment
    });
    
  } catch (error) {
    console.error('Commitment fetch error:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching commitment',
      error: error.message
    });
  }
};

// Update a commitment
exports.update = async (req, res) => {
  try {
    const { 
      title, description, category, startDate, 
      endDate, frequency, completed, progress, priority, tags, isPublic 
    } = req.body;
    
    // Build update object
    const updateData = {};
    
    if (title !== undefined) updateData.title = title;
    if (description !== undefined) updateData.description = description;
    if (category !== undefined) updateData.category = category;
    if (startDate !== undefined) updateData.startDate = startDate;
    if (endDate !== undefined) updateData.endDate = endDate;
    if (frequency !== undefined) updateData.frequency = frequency;
    if (completed !== undefined) updateData.completed = completed;
    if (progress !== undefined) updateData.progress = progress;
    if (priority !== undefined) updateData.priority = priority;
    if (tags !== undefined) updateData.tags = tags;
    if (isPublic !== undefined) updateData.isPublic = isPublic;
    
    const updatedCommitment = await Commitment.findOneAndUpdate(
      { _id: req.params.id, userId: req.user.id },
      { $set: updateData },
      { new: true }
    );

    if (!updatedCommitment) {
      return res.status(404).json({
        success: false,
        message: 'Commitment not found or unauthorized'
      });
    }

    res.status(200).json({
      success: true,
      message: 'Commitment updated successfully',
      commitment: updatedCommitment
    });
    
  } catch (error) {
    console.error('Commitment update error:', error);
    res.status(500).json({
      success: false,
      message: 'Error updating commitment',
      error: error.message
    });
  }
};

// Delete a commitment
exports.delete = async (req, res) => {
  try {
    const deleted = await Commitment.findOneAndDelete({ 
      _id: req.params.id,
      userId: req.user.id
    });

    if (!deleted) {
      return res.status(404).json({
        success: false,
        message: 'Commitment not found or unauthorized'
      });
    }

    res.status(200).json({
      success: true,
      message: 'Commitment deleted successfully'
    });
    
  } catch (error) {
    console.error('Commitment deletion error:', error);
    res.status(500).json({
      success: false,
      message: 'Error deleting commitment',
      error: error.message
    });
  }
};

// Add checkpoint to commitment
exports.addCheckpoint = async (req, res) => {
  try {
    const { date, status, note } = req.body;
    
    const commitment = await Commitment.findOne({ 
      _id: req.params.id,
      userId: req.user.id
    });

    if (!commitment) {
      return res.status(404).json({
        success: false,
        message: 'Commitment not found or unauthorized'
      });
    }

    commitment.checkpoints.push({
      date: date || Date.now(),
      status,
      note
    });

    // Update progress based on checkpoints
    if (commitment.checkpoints.length > 0) {
      const completedCheckpoints = commitment.checkpoints.filter(
        cp => cp.status === 'completed'
      ).length;
      
      commitment.progress = Math.floor(
        (completedCheckpoints / commitment.checkpoints.length) * 100
      );
    }

    await commitment.save();

    res.status(200).json({
      success: true,
      message: 'Checkpoint added successfully',
      commitment
    });
    
  } catch (error) {
    console.error('Checkpoint addition error:', error);
    res.status(500).json({
      success: false,
      message: 'Error adding checkpoint',
      error: error.message
    });
  }
};

// Get public commitments
exports.getPublic = async (req, res) => {
  try {
    const { category, limit = 10, page = 1 } = req.query;
    
    // Build query
    const query = { isPublic: true };
    
    if (category) {
      query.category = category;
    }
    
    const skip = (parseInt(page) - 1) * parseInt(limit);
    
    const commitments = await Commitment.find(query)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(parseInt(limit))
      .exec();

    const total = await Commitment.countDocuments(query);

    res.status(200).json({
      success: true,
      count: commitments.length,
      total,
      pages: Math.ceil(total / parseInt(limit)),
      currentPage: parseInt(page),
      commitments
    });
    
  } catch (error) {
    console.error('Public commitments fetch error:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching public commitments',
      error: error.message
    });
  }
};