var socket = io.connect('http://127.0.0.1:5000/');


const selectorsAndClasses =
  [
    {selector: ".top-nav__menu", className: "rage-red-bg" },
    {selector: ".tw-button", className: "rage-red-bg-second" },
    {selector: ".tw-button", className: "rage-no-border" },
    {selector: ".top-nav__nav-link, .tw-button__text, .directory-header__link, .tw-button--hollow", className: "rage-color"},
    {selector: ".directory-tabs__item", className: "rage-color-darker" },
    {selector: ".directory-tabs__item--selected", className: "rage-red-bottom-border" },

  ];


socket.on('connect', function()
{
  addAnimationInit();
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

function addAnimationInit()
{
  let selector = ".top-nav__menu, .tw-button, .top-nav__nav-link, .tw-button__text, .directory-header__link, .tw-button--hollow, .directory-tabs__item";
  addClassToList( S(selector) , "rage-animation-init" )
}
function redify()
{
  selectorsAndClasses.forEach(item => addClassToList( S(item.selector) , item.className ));
}

function deredify()
{
  selectorsAndClasses.forEach(item => removeClassToList( S(item.selector) , item.className ));
}

socket.on("rageIncoming", function(msg)
{
  let old = getData();

  old.forEach( function(item)
  {
      document.querySelector("a[href='" + item + "'] > div").style.border = "" ;
  });

  if (msg == "%no-rage")
  {
    deredify();
    console.log("NO RAGE");
  }
  else
  {
    redify();
    document.querySelector("a[href='" + msg + "'] > div").style.border = "50px solid #e2b719"
    console.log("RAGE RAGE BABY");
  }
});

function addClassToList(list, className)
{
  list.forEach(item => item.classList.add(className));
}

function removeClassToList(list, className)
{
  list.forEach(item => item.classList.remove(className));
}

function S(selector)
{
  return document.querySelectorAll(selector);
}
