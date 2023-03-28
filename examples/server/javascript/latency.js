const express = require('express');
const { createServer } = require("http");
const { Server } = require("socket.io");

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer);

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

httpServer.listen(port, () => console.log(`server listening on port ${port}`));
