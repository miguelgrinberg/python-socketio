const express = require('express');
const app = express();
const server = require('http').createServer(app);
const io = require('socket.io')(server);
const port = process.env.PORT || 5000;

app.use(express.static(__dirname + '/latency_public'));

io.on('connection', socket => {
  console.log(`connect ${socket.id}`);

  socket.on('ping_from_client', () => {
    socket.emit('pong_from_server');
  });

  socket.on('disconnect', () => {
    console.log(`disconnect ${socket.id}`);
  });
});

server.listen(port, () => console.log(`server listening on port ${port}`));
