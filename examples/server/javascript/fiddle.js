const express = require('express');
const app = express();
const server = require('http').createServer(app);
const io = require('socket.io')(server);
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

server.listen(port, () => console.log(`server listening on port ${port}`));
