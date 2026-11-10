HTTP
// Simple development script for the Discord Bot Dashboard
const http = require('http');
const path = require('path');

const hostname = 'localhost';
const port = 3000;

const server = http.createServer((req, res) => {
  console.log(`${req.method} ${req.url}`);
  
  // Handle API routes
  if (req.url.startsWith('/api/')) {
    let data = '';
    
    req.on('data', chunk => {
      data += chunk;
    });
    
    req.on('end', () => {
      let responseData = {};
      
      if (req.url === '/api/bot/status') {
        responseData = {
          status: 'online',
          latency: Math.random() * 100 + 20,
          uptime: '99.9%',
          commandsExecuted: 89234,
          users: 12345
        };
      } else if (req.url === '/api/commands') {
        responseData = [
          { name: 'ping', description: 'Check bot latency', category: 'General' },
          { name: 'ban', description: 'Ban a user', category: 'Moderation' },
          { name: 'play', description: 'Play music', category: 'Music' },
          { name: 'balance', description: 'Check balance', category: 'Economy' },
          { name: 'giveaway', description: 'Start a giveaway', category: 'Fun' },
          { name: 'afk', description: 'Set AFK status', category: 'Auto' },
          { name: 'prefix', description: 'Change command prefix', category: 'Admin' }
        ];
      } else if (req.url === '/api/users') {
        responseData = [
          { id: '1', username: 'nighty_user', discriminator: '7342', level: 42, avatar: 'https://i.pinimg.com/736x/32/2d/3e/322d3e9037387874bc0e4358832a4af3.jpg', badges: ['Developer', 'Booster'] },
          { id: '2', username: 'alex_gaming', discriminator: '1234', level: 15, avatar: 'https://i.pinimg.com/736x/32/2d/3e/322d3e9037387874bc0e4358832a4af3.jpg', badges: [] },
          { id: '3', username: 'sara_dev', discriminator: '5678', level: 28, avatar: 'https://i.pinimg.com/736x/32/2d/3e/322d3e9037387874bc0e4358832a4af3.jpg', badges: ['Developer'] },
          { id: '4', username: 'mike_admin', discriminator: '9999', level: 50, avatar: 'https://i.pinimg.com/736x/32/2d/3e/322d3e9037387874bc0e4358832a4af3.jpg', badges: ['Admin', 'Booster'] }
        ];
      } else {
        responseData = { message: 'Not Found', status: 404 };
      }
      
      res.writeHead(responseData.status || 200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(responseData));
    });
    return;
  }
  
  // Serve static files
  let filePath = path.join(__dirname, 'public', req.url);
  if (filePath === path.join(__dirname, 'public', '/')) {
    filePath = path.join(__dirname, 'public', 'index.html');
  }
  
  const fs = require('fs');
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/html' });
      res.end('<h1>404 Not Found</h1>');
      return;
    }
    const ext = path.extname(filePath);
    const contentType = ext === '.html' ? 'text/html' :
                       ext === '.css' ? 'text/css' :
                       ext === '.js' ? 'application/javascript' :
                       'text/plain';
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
});

server.listen(port, hostname, () => {
  console.log(`Dashboard development server running at http://${hostname}:${port}/`);
});
