const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

console.log('🚀 CV Parser WebSocket Test Server - PROMPT 2 Validation');

// Health endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'UP',
    timestamp: new Date().toISOString(),
    service: 'CV Parser Test v2.0'
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'CV Parser WebSocket Test',
    status: 'ready',
    version: '2.0.0-test'
  });
});

// WebSocket handling
io.on('connection', (socket) => {
  console.log('🔌 Client connected:', socket.id);
  
  // Send welcome message
  socket.emit('connected', {
    socketId: socket.id,
    timestamp: new Date().toISOString(),
    capabilities: ['real_time_parsing', 'progress_tracking'],
    version: '2.0.0-test'
  });

  // Handle CV parsing requests
  socket.on('parse_cv', (data) => {
    console.log('📄 Parse CV request:', data.taskId);
    
    const startTime = Date.now();
    let progress = 0;
    const stages = ['upload', 'ocr_processing', 'ai_extraction', 'validation'];
    
    const interval = setInterval(() => {
      progress += Math.random() * 20 + 10;
      if (progress > 100) progress = 100;
      
      const stageIndex = Math.floor((progress / 100) * stages.length);
      const stage = stages[Math.min(stageIndex, stages.length - 1)];
      
      // Send progress update
      socket.emit('parsing_progress', {
        type: 'parsing_progress',
        taskId: data.taskId,
        progress: Math.round(progress),
        stage: stage,
        timestamp: Date.now()
      });
      
      if (progress >= 100) {
        clearInterval(interval);
        
        // Send final result
        socket.emit('parsing_completed', {
          type: 'parsing_completed',
          taskId: data.taskId,
          data: {
            extractedFields: {
              name: 'Jean Dupont',
              email: 'jean.dupont@email.com',
              phone: '+33 6 12 34 56 78'
            },
            confidence: 0.95
          },
          duration: Date.now() - startTime,
          timestamp: new Date().toISOString()
        });
        
        console.log('✅ Parsing completed:', data.taskId);
      }
    }, 150);
  });

  socket.on('disconnect', () => {
    console.log('🔌 Client disconnected:', socket.id);
  });
});

const PORT = 5051;
server.listen(PORT, () => {
  console.log(`🎯 Test Server running on port ${PORT}`);
  console.log(`🔌 WebSocket ready for PROMPT 2 validation`);
  console.log('✅ Ready to test!');
});
