// helper
function $ (id) { return document.getElementById(id); }

// chart
let smoothie;
let time;

function render () {
  if (smoothie) smoothie.stop();
  $('chart').width = document.body.clientWidth;
  smoothie = new SmoothieChart();
  smoothie.streamTo($('chart'), 1000);
  time = new TimeSeries();
  smoothie.addTimeSeries(time, {
    strokeStyle: 'rgb(255, 0, 0)',
    fillStyle: 'rgba(255, 0, 0, 0.4)',
    lineWidth: 2
  });
}

// socket
const socket = io();
let last;
function send () {
  last = new Date();
  socket.emit('ping_from_client');
  $('transport').innerHTML = socket.io.engine.transport.name;
}

socket.on('connect', () => {
  if ($('chart').getContext) {
    render();
    window.onresize = render;
  }
  send();
});

socket.on('disconnect', () => {
  if (smoothie) smoothie.stop();
  $('transport').innerHTML = '(disconnected)';
});

socket.on('pong_from_server', () => {
  const latency = new Date() - last;
  $('latency').innerHTML = latency + 'ms';
  if (time) time.append(+new Date(), latency);
  setTimeout(send, 100);
});
