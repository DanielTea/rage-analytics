var socket = io.connect('http://127.0.0.1:5000/');

socket.on('connect', function()
{
    socket.emit('message', 'HELLO FROM EXTENSION JOOOOOOO');
});


setInterval( function()
{
  console.log("send data");
  socket.emit('sendTopFiveStreamer', getData());

}, 5000);


function getData()
{
  let list = Array.from( document.querySelectorAll(".live-channel-card__channel") );

  let fiveFirst = list.slice(0,5);
  let data = [];

  fiveFirst.forEach(item => data.push(item.getAttribute("href")));

  return data;
}

socket.on("rageIncoming", function(msg)
{
  console.log(msg);
  let old = getData();

  old.forEach( function(item)
  {
      document.querySelector("a[href='" + item + "'] > div").style.border = "" ;
  });

  document.querySelector("a[href='" + msg + "'] > div").style.border = "50px solid #e2b719"
});
