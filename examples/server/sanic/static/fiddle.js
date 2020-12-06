'use strict';

(function() {

  const socket = io();

  socket.on('connect', () => {
    console.log(`connect ${socket.id}`);
  });

  socket.on('disconnect', () => {
    console.log(`disconnect ${socket.id}`);
  });

  socket.on('hello', (a, b, c) => {
    console.log(a, b, c);
  });

})();
