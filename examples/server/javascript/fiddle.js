const express = require('express');
const { createServer } = require("http");
const { Server } = require("socket.io");
const { instrument } = require("@socket.io/admin-ui");

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: { origin: 'https://admin.socket.io', credentials: true },
});
const port = process.env.PORT || 5000;

app.use(express.static(__dirname + '/fiddle_public'));

io.on('connection', socket => {
  console.log(`connect auth=${JSON.stringify(socket.handshake.auth)} sid=${socket.id}`);

  socket.emit('hello', 1, '2', {
    hello: 'you'
  });

  socket.on('disconnect', () => {
    console.log(`disconnect ${socket.id}`);
  });
});

instrument(io, {auth: false, mode: 'development'});
httpServer.listen(port, () => console.log(`server listening on port ${port}`));
