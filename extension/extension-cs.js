var socket = io.connect('http://127.0.0.1:5000/stream');

const heartbeatTime = 3000;
const overlayStyle = "rage-overlay-style-darker";
const selectorsAndClasses =
  [
    {selector: ".top-nav__menu", className: "rage-red-bg" },
    {selector: ".tw-button", className: "rage-red-bg-second" },
    {selector: ".tw-button", className: "rage-no-border" },
    {selector: ".top-nav__nav-link, .tw-button__text, .directory-header__link, .tw-button--hollow", className: "rage-color"},
    {selector: ".directory-tabs__item", className: "rage-color-darker" },
    {selector: ".directory-tabs__item--selected", className: "rage-red-bottom-border" },

  ];

const sessionId = Date.now();
const numberOfConcurrentStreamers = 10;

const overlayMessages = {"rage": [  "don't cry, NAME",
                                    "too bad,  NAME",
                                    "git gud, NAME",
                                    "chin up, NAME",
                                    "poor NAME",
                                    "gg, NAME",
                                    "R.I.P. NAME",
                                    ">:( NAME >:(",
                                    "get rekt, NAME",
                                    "NAME smash!",
                                    "NAME quits",
                                    "NAME rages",
                                    "NAME loses it"]};

const streamerSelection = "SELECTION";
const streamerWatching = "WATCHING";

let currentStreamer = new Map();
let activeGame = "";

let currentUrl = window.location.href;
let intervalUrl;

// tell the background script o start a new Session
 let toDo = checkUrl();
 toDo();

window.addEventListener("load", function()
{
  // tell the background script o start a new Session
  let toDo = checkUrl();
  toDo();

});

window.addEventListener("newUrl", function()
{
  currentUrl = window.location.href;
  let toDo = checkUrl();
  toDo();

});


function initEventsAndIntervalsSelection()
{
  clearInterval(intervalUrl);

  // for checking the current url -> twitch is react so i cant listen on load events
  intervalUrl = setInterval( function()
  {
    let url = window.location.href;
    if (currentUrl != url)
    {
      let event = new CustomEvent('newUrl', {});
      window.dispatchEvent(event);
    }
  }, heartbeatTime);

  if (activeGame != currentUrl)
  {
    // For getting getting and sending the data;
    setTimeout( function() {
      let streamerList = getStreamerData();
      let streamerNameList = streamerList.map(streamer => streamer.name)

      console.log("send data " + streamerNameList);
      console.log(streamerList.length);

      socket.emit('sendStreamer', streamerNameList);

      streamerNameList.forEach(streamer => currentStreamer.set(streamer, {"timeout": ""}));
    }, heartbeatTime);
  }
  else
  {
    console.log("still the same game")
  }
}

function initEventsAndIntervalsWatching()
{
  clearInterval(intervalUrl);

  // for checking the current url -> twitch is react so i cant listen on load events
  intervalUrl = setInterval( function()
  {
    let url = window.location.href;
    if (currentUrl != url)
    {
      let event = new CustomEvent('newUrl', {});
      window.dispatchEvent(event);
    }
  }, heartbeatTime);

}

function checkUrl()
{
  const stringForStreamerSelection = /^https:\/\/www\.twitch\.tv\/directory\/game\/[\w%']{3,}$/;
  const stringForWatchingAStream = /^https:\/\/www\.twitch\.tv\/[\w%']{3,}$/;
  const subdomainsToExculde = ["directory"]

  const regExForStreamerSelection = new RegExp(stringForStreamerSelection);
  const regExForWatchingAStream = new RegExp(stringForWatchingAStream);

  if (regExForStreamerSelection.test(currentUrl))
  {
    return toDoSelection;
  }
  else
  if (regExForWatchingAStream.test(currentUrl))
  {
    let splittedUrl = currentUrl.split("/");
    let subdomain = splittedUrl[splittedUrl.length-1];

    if (subdomainsToExculde.includes(subdomain))
    {
      return toDoNothing;
    }
    else
    {
        return toDoWatching;
    }

  }
  else
  {
    return toDoNothing
  }
}

function toDoSelection()
{
  console.log("STREAMER SELECTION");

  initSession();
  addAnimationInit();
  initEventsAndIntervalsSelection();

  socket.on('connect', function()
  {
    socket.emit('message', 'HELLO FROM EXTENSION JOOOOOOO  SELCETION');
  });

   socket.on('disconnect', function()
  {
    console.log("BITCHES");
  });
}

function toDoWatching()
{
  console.log("STREAMER WATCHING");

  addAnimationInit();
  initEventsAndIntervalsWatching();

  socket.on('connect', function()
  {
    socket.emit('message', 'HELLO FROM EXTENSION JOOOOOOO WATCHING');
  });
}

function toDoNothing()
{
  console.log("LAME! NOTHING TO DO");

  clearInterval(intervalUrl);

  // for checking the current url -> twitch is react so i cant listen on load events
  intervalUrl = setInterval( function()
  {
    let url = window.location.href;
    if (currentUrl != url)
    {
      let event = new CustomEvent('newUrl', {});
      window.dispatchEvent(event);
    }
  }, heartbeatTime);

  deredify();
}

function getData()
{
  let list = S(".live-channel-card__channel");

  let fiveFirst = list.slice(0,numberOfConcurrentStreamers);
  let data = [];

  fiveFirst.forEach(item => data.push(item.getAttribute("href")));

  return data;
}

function getStreamerData()
{
  let list = S(".tw-card");
  let fiveFirst = list.slice(0,numberOfConcurrentStreamers);

  let data = [];
  fiveFirst.forEach(item => data.push(createStreamerData(item)));

  return data;
}

function createStreamerData(elem)
{
  let aTag = elem.firstChild.firstChild.firstChild.firstChild.firstChild;
  let streamerName = aTag.href.replace("https://www.twitch.tv", "");

  let newStreamer = { "name" : streamerName,
                      "title" : aTag.title,
                      "img" : "https://static-cdn.jtvnw.net/previews-ttv/live_user_" + streamerName.substr(1) + "-320x180.jpg"
  };

  console.log("new Streamer tracked:", newStreamer);

  return newStreamer
}


function showRageNotification(streamer)
{
  var notification = new Notification('Rage incoming!', {
    icon: streamer.img,
    body: streamer.name.substr(1) + " is raging! Check it out here",
  });

  notification.onclick = function () {
    window.open("https://www.twitch.tv" + streamerName);
  };
}


/*

HTML EXAMPLE

<link href="https://fonts.googleapis.com/css?family=Permanent+Marker" rel="stylesheet">

<div class="notification-box">
  <div class="notification-box__top-bar">
   <span class="notification-box__top-bar__title">
     Kraaaaaaaankes league Gameplay + Stoooryyytime!! :D | neues YouTube Video incoming | !instagram MAIN !prowerden !baron !YouTube !merch
   </span>
   <span class="x-button">
      <svg class="button-svg"
           width="18px"
           height="18px"
           version="1.1"
           viewBox="0 0 16 16">
        <path d="M8 6.586L3.757 2.343 2.343 3.757 6.586 8l-4.243 4.243 1.414 1.414L8 9.414l4.243 4.243 1.414-1.414L9.414 8l4.243-4.243-1.414-1.414"
              fill-rule="evenodd">
        </path>
      </svg>
   </span>
  </div>
  <div class="notification-box__body">
    <div class="notification-box__overlay"></div>
  <img class="notification-box__image" src="https://static-cdn.jtvnw.net/previews-ttv/live_user_xoynuzi-320x180.jpg" alt="" width="70px">
  <div class="notification-box__overlay">

  </div>
  <span class="notification-box__rage">RAGE!</span>
  </div>


</div>

*/


function addAnimationInit()
{
  let selector = ".top-nav__menu, .tw-button, .top-nav__nav-link, .tw-button__text, .directory-header__link, .tw-button--hollow, .directory-tabs__item";
  addClassToList( S(selector) , "rage-animation-init" );
}

function redify()
{
  selectorsAndClasses.forEach(item => addClassToList( S(item.selector) , item.className ));
}

function deredify()
{
  selectorsAndClasses.forEach(item => removeClassToList( S(item.selector) , item.className ));

}

socket.on("test", function(msg) {console.log(msg)});

socket.on("rageIncoming", function(msg)
{
  if (msg.link == "%no-rage")
  {
    deredify();
    console.log("NO RAGE");
  }
  else
  {
    redify();

    let oldText = S("a[href='" + msg.link + "']  > span.rage-overlay-text");
    oldText.forEach(item => item.remove());

    showRage(msg.link);
    let thisStreamer = currentStreamer.get(msg.link);
    clearTimeout(thisStreamer.timeout);
    thisStreamer.timeout = setTimeout(function () {
        unshowRage(msg.link);
    }, 3000);
    console.log("RAGE RAGE BABY");
  }
});

function showRage(msg)
{
  let streamerName = msg.split("/")[1];
  let rageItem = document.querySelector("a[data-a-target='live-channel-card-thumbnail-link'][href='" + msg + "']");

  let overlayDiv = document.createElement("div");
  overlayDiv.classList.add("rage-overlay");

  setTimeout(function() {
    overlayDiv.classList.add(overlayStyle);
  }, 0);

  overlayDiv.setAttribute("id", "rage-overlay-" + streamerName);

  let overlayText = document.createElement("span");
  overlayText.textContent = getRandomMessage("rage").replace("NAME", streamerName);
  overlayText.classList.add("rage-overlay-text");
  overlayText.classList.add("rage-font-" + getRandomInt(1,5));

  overlayText.classList.add("shake");

  rageItem.appendChild(overlayDiv);
  rageItem.appendChild(overlayText);

}

function unshowRage(streamer)
{
  if (streamer == null)
  {
    let allOverlays = S(".rage-overlay, .rage-overlay-text");

    allOverlays.forEach(item => item.remove());
  }
  else
  {
    let divsToDelete = S("a[href='" + streamer + "'] > div.rage-overlay.rage-overlay-style-darker, a[href='" + streamer + "']  > span.rage-overlay-text");
    divsToDelete.forEach(item => item.remove());
  }
}

function getRandomMessage(emotion) {
  let index = Math.floor(Math.random() * overlayMessages[emotion].length);
  return overlayMessages[emotion][index];
}

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
  return Array.from( document.querySelectorAll(selector) );
}

function getRandomInt(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min)) + min; //The maximum is exclusive and the minimum is inclusive
}
function initSession()
{
  let message = {"type": "initSession", "sessionId": sessionId, "numberOfConcurrentStreamers": numberOfConcurrentStreamers};
  chrome.runtime.sendMessage(message, function(response) {
      console.log(response);
  });
}

// function saveCurrentStreamers(streamerList)
// {
//   let message = {"type": "updateStreamer", "data": streamerList, "sessionId": sessionId }
//   chrome.runtime.sendMessage(message, function(response) {
//       console.log(response);
//   });
// }
//
// function getSavedStreamer()
// {
//   let message = {"type": "getStreamer", "sessionId": sessionId }
//   chrome.runtime.sendMessage(message, function(response) {
//       console.log(response);
//   });
// }

// first para is the message, the sencond the callback which will be again in the scope of this content script
// chrome.runtime.sendMessage({text: "hey"}, function(response) {
//     console.log("Response: ", response);
// });
