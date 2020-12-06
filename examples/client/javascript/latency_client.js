const io = require('socket.io-client')
const port = process.env.PORT || 5000;

const socket = io('http://localhost:' + port);
let last;
function send () {
  last = new Date();
  socket.emit('ping_from_client');
}

socket.on('connect', () => {
  console.log(`connect ${socket.id}`);
  send();
});

socket.on('disconnect', () => {
  console.log(`disconnect ${socket.id}`);
});

socket.on('pong_from_server', () => {
  const latency = new Date() - last;
  console.log('latency is ' + latency + ' ms');
  setTimeout(send, 1000);
});
