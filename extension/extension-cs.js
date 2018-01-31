var socket = io.connect('http://127.0.0.1:5000/stream');

const confidenceThreshold = 0.0;
const heartbeatTime = 3000;
const overlayStyle = "rage-overlay-style-darker";
const selectorsAndClasses =
  [
    {selector: ".top-nav__menu", className: "rage-red-bg-moved" },
    {selector: ".tw-button", className: "rage-red-bg-second" },
    {selector: ".tw-button", className: "rage-no-border" },
    {selector: ".tw-button--hollow", className: "rage-hollow"},
    {selector: ".top-nav__nav-link, .tw-button__text, .directory-header__link, .tw-button--hollow", className: "rage-color"},
    {selector: ".directory-tabs__item", className: "rage-color-darker" },
    {selector: ".directory-tabs__item--selected", className: "rage-red-bottom-border" },
  ];

const sessionId = Date.now();
const numberOfConcurrentStreamers = 200;

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

const stringForStreamerSelection = /^https:\/\/www\.twitch\.tv\/directory\/game\/[\w%\-']{3,}$/;
const stringForWatchingAStream = /^https:\/\/www\.twitch\.tv\/[\w%']{3,}$/;
const subdomainsToExclude = ["directory"];

const regExForStreamerSelection = new RegExp(stringForStreamerSelection);
const regExForWatchingAStream = new RegExp(stringForWatchingAStream);


let currentStreamer = new Map();
let streamerShownWhileWatching = new Map();


let currentUrl = window.location.href;
let activeGame = "";

let intervalUrl;
let timeOutDeredify;

let rageLimit = 0.3;

// tell the background script o start a new Session
let toDo = checkUrl();
toDo();

// window.addEventListener("load", function()
// {
//   // tell the background script o start a new Session
//   let toDo = checkUrl();
//   toDo();
//   console.log("WindowLoadEvent")
// });

window.addEventListener("newUrl", function()
{
  currentUrl = window.location.href;
  let toDo = checkUrl();
  toDo();
});

socket.on('connect', function()
{
  console.log("conncted")
  socket.emit('message', 'HELLO FROM EXTENSION JOOOOOOO  SELCETION');
});

socket.on('test', function(e)
{
  console.log(e)
});

 socket.on('disconnect', function()
{
  console.log("Disconnected");
});

socket.on("sessionStatus", function(msg) { handleSessionStatus(msg) });

socket.on("rageIncoming", function(msg)
{
  console.log("MESSAGE: ", msg)
  if (msg.confidence > confidenceThreshold && msg.game == activeGame)
  {
    if(regExForStreamerSelection.test(currentUrl))
    {
      console.log("RAGE INCOMING SELECTION");

      let oldText = S("a[href='" + msg.link + "']  > span.rage-overlay-text");
      oldText.forEach(item => item.remove());

      showRage(msg.link);
      let thisStreamer = currentStreamer.get(msg.link);
      clearTimeout(thisStreamer.timeout);
      thisStreamer.timeout = setTimeout(function () {
          unshowRage(msg.link);
      }, 3000);

      redify();
      clearTimeout(timeOutDeredify);
      timeOutDeredify = setTimeout( function() { deredify() }, 3000);

    }
    else if(regExForWatchingAStream.test(currentUrl))
    {
      console.log("RAGE INCOMING WATCHING " + msg.link);
      let streamer;

      redify();
      clearTimeout(timeOutDeredify);
      timeOutDeredify = setTimeout( function() { deredify() }, 3000);

      if (currentStreamer.has(msg.link))
      {
        streamer = currentStreamer.get(msg.link).streamer;
        showCustomNotification(streamer)
      }
      else
      {
          createCustomNotificationFromSavedStreamer(msg.link);
      }
    }
  }
});

chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    rageLimit = request.confidence;
    console.log(rageLimit);
  });



function handleSessionStatus(msg)
{
  console.log(msg);
  if (msg == 0)
  {
    createSessionStatusOverlay()
    setSessionStatusOverlayText("Initialising streams...");
  }
  else
  if (msg == 1)
  {
    setSessionStatusOverlayText("Downloading streams...");
  }
  else
  if (msg == 2)
  {
    setSessionStatusOverlayText("Started analysing!");
    setTimeout(deleteSessionStatusOverlay, 2000);
  }
}

function createSessionStatusOverlay()
{;

  const outerDiv = document.createElement("div");
  outerDiv.setAttribute("id", "sessionStatusOverlay");
  outerDiv.classList.add("animated");
  outerDiv.classList.add("slideInRight");

  const innerDiv = document.createElement("div");
  innerDiv.setAttribute("id", "sessionStatusInner");


  const spinner  = document.createElement("div");
  spinner.setAttribute("id", "loading");

  const span = document.createElement("span");
  span.setAttribute("id", "sessionStatusOverlayText");

  outerDiv.appendChild(innerDiv);
  innerDiv.appendChild(span);

  S("main")[0].appendChild(outerDiv);
}

function setSessionStatusOverlayText(text)
{
  S("#sessionStatusOverlayText")[0].textContent = text;
}

function deleteSessionStatusOverlay()
{
  let list = S("#sessionStatusOverlay, #sessionStatusOverlayText");
  addClassToList(list, "status-fadeOut");

  setTimeout(function() {
    S("#sessionStatusOverlay")[0].remove();
  }, 1500)

}

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

  console.log("ACTIVE GAME " + activeGame);
  console.log("URL         " + currentUrl);
  if (activeGame != currentUrl && activeGame != "")
  {
    location.reload()
  }
  else
  if (activeGame != currentUrl)
  {
    console.log("new game")
    activeGame = currentUrl;
    safeLastGame(activeGame);
    clearBackgroundScript();

    // For getting getting and sending the data;
    setTimeout( function() {
      let streamerList = getStreamerData();
      let streamerNameList = streamerList.map(streamer => streamer.name)

      console.log("send data for selection " + streamerNameList);
      console.log(streamerList.length);

      let msg = {"game": currentUrl, "streamer": streamerNameList};
      socket.emit('sendStreamer', msg);

      streamerList.forEach(streamer => currentStreamer.set(streamer.name, {"streamer": streamer, "timeout": ""}));
      saveStreamer(streamerList);
    },heartbeatTime);
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

  if (activeGame == "")
  {
    getSafedGame();
  }

  console.log("initEventsAndIntervalsWatching");
}

function checkUrl()
{

  if (regExForStreamerSelection.test(currentUrl))
  {
    return toDoSelection;
  }
  else
  if (regExForWatchingAStream.test(currentUrl))
  {
    let splittedUrl = currentUrl.split("/");
    let subdomain = splittedUrl[splittedUrl.length-1];

    if (subdomainsToExclude.includes(subdomain))
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
  //initSession();
  addAnimationInit();
  initEventsAndIntervalsSelection();


}

function toDoWatching()
{
  console.log("STREAMER WATCHING");

  addAnimationInit();
  initEventsAndIntervalsWatching();



}

function toDoNothing()
{
  console.log("LAME! NOTHING TO DO");


  clearInterval(intervalUrl);

  streamerShownWhileWatching.clear();
  streamerShownWhileWatching.forEach(streamer => clearTimeout(streamer.timeout));
  let oldNotificationContainer = S(".notification-container")[0];
  if (oldNotificationContainer != null) { oldNotificationContainer.remove(); }

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
function  getSavedStreamer(streamerName)
{
  let msg = {"type": "getStreamer", "data": streamerName}
  chrome.runtime.sendMessage(msg, function(response) {
    console.log("Response: ", response);
  });
}

function clearBackgroundScript()
{
  chrome.runtime.sendMessage({"type":"initSession"}, function(response) {console.log(response);})
}

function safeLastGame(game)
{
  chrome.runtime.sendMessage({"type":"safeGame", "data": game}, function(response) {console.log(response);})
}

function getSafedGame()
{
  chrome.runtime.sendMessage({"type":"getSafedGame"}, function(response)
  {
    activeGame = response;
    console.log("got Safed Game")
  })

}

function createCustomNotificationFromSavedStreamer(streamerName)
{
  let msg = {"type": "getStreamer", "data": streamerName}
  chrome.runtime.sendMessage(msg, function(response) {
    let data = JSON.parse(response);
    if (data)
    {
      showCustomNotification(data);
    }
    else
    {
      console.log("couldnt find stream in bg");
    }
  });
}

function saveStreamer(streamer)
{
  let msg = {"type": "saveStreamer", "data": JSON.stringify(streamer)}
  chrome.runtime.sendMessage(msg, function(response) {
    console.log("Response: ", response);
  });
}

function getStreamerData()
{
  let list = S(".live-channel-card > .tw-card");
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

  // console.log("new Streamer tracked:", newStreamer);

  return newStreamer
}


function showRageNotification(streamer)
{
  console.log("showing RAGE notifications");
  let notification = new Notification('Rage incoming!', {
    icon: streamer.img,
    body: streamer.name.substr(1) + " is raging! Check it out here",
  });
}

function insertNotificationContainer()
{
  if (S(".notification-container")[0] == null)
  {
    let notificationContainer = document.createElement("div");
    notificationContainer.className = "notification-container";
    let parentForNotificationContainer = S("body")[0];
    if (parentForNotificationContainer != null)
    {
      parentForNotificationContainer.appendChild(notificationContainer);
    }
    else
    {
      console.log("infobar doesnt exists anymore")
    }
  }

}

function showCustomNotification(streamer)
{
  if(streamerShownWhileWatching.size == 0)
  {
    insertNotificationContainer();
  }

  let numberOfNotifications = streamerShownWhileWatching.size

  let nameFromUrl = "/" + currentUrl.split("/")[3];
  if (streamer.name == nameFromUrl)
  {
    console.log("No notification because we are watching this streamer")

  }
  else
  if(!streamerShownWhileWatching.has(streamer.name) && numberOfNotifications <  3)
  {
    let container  = S(".notification-container")[0]
    if (container != null)
    {
      let notification = createCustomNotification(streamer);
      let timeout = removeCustomNotification(streamer.name)

      streamerShownWhileWatching.set(streamer.name, {"notification": notification, "timeout": timeout});
      container.appendChild(notification);
    }
    else
    {
      console.log("container doesnt exists anymore")
    }
  }
  else
  if (streamerShownWhileWatching.has(streamer.name))
  {
    clearTimeout(streamerShownWhileWatching.get(streamer.name).timeout);
    let timeout = removeCustomNotification(streamer.name)
    streamerShownWhileWatching.get(streamer.name).timeout = timeout;

    updateStreamerText(streamer.name, streamerShownWhileWatching.get(streamer.name));

  }
}


function updateStreamerText(streamerName, streamer)
{
  let notification = streamer.notification;
  let span = notification.children[0].children[1].children[0].children[2];
  span.textContent = getRandomMessage("rage").replace("NAME", streamerName.substring(1));

  span.classList.remove("rage-font-1");
  span.classList.remove("rage-font-2");
  span.classList.remove("rage-font-3");
  span.classList.remove("rage-font-4");

  span.classList.add("rage-font-" + getRandomInt(1,5));
  span.classList.remove("shake");
  setTimeout(function () {
    span.classList.add("shake");
  }, 10);
}

function removeCustomNotification(streamerName)
{
  return setTimeout(function () {
    streamerShownWhileWatching.get(streamerName).notification.classList.add("status-fadeOut");
    setTimeout(function() {
      streamerShownWhileWatching.get(streamerName).notification.remove();
      streamerShownWhileWatching.delete(streamerName);
    }, 1500)
  }, 3000);
}


function createCustomNotification(streamer)
{
    let streamerName = streamer.name.substring(1);
    console.log("creating notification for " + streamerName);
    let wrapper = document.createElement("div");
    wrapper.className = "notification-box-wrapper";

    let notification = document.createElement("div");
    notification.className = "notification-box animated slideInRight";
    notification.id = "notification_" + streamerName;

    // ---- Top Bar ----

    let topBar = document.createElement("div");
    topBar.className = "notification-box__top-bar";

    let title = document.createElement("span");
    title.className = "notification-box__top-bar__title";
    title.innerHTML = streamer.title;

    let xButton = document.createElement("span");
    xButton.className = "x-button";
    xButton.innerHTML = `
        <svg class="button-svg"
               width="18px"
               height="18px"
               version="1.1"
               viewBox="0 0 16 16"
               onclick=document.getElementById("notification_` + streamerName + `").remove()>
            <path d="M8 6.586L3.757 2.343 2.343 3.757 6.586 8l-4.243 4.243 1.414 1.414L8 9.414l4.243 4.243 1.414-1.414L9.414 8l4.243-4.243-1.414-1.414"
                  fill-rule="evenodd">
            </path>
         </svg>
    `;

    // ---- Body ----
    let atag = document.createElement("a");
    atag.setAttribute("data-a-target", "live-channel-card-thumbnail-link");
    atag.setAttribute("href", "/" + streamerName);

    // atag.addEventListener("click", function(e) {e.preventDefault();});


    let notificationBody = document.createElement("div");
    notificationBody.className = "notification-box__body";

    let streamImg = document.createElement("img");
    streamImg.className = "notification-box__image";
    streamImg.src = "https://static-cdn.jtvnw.net/previews-ttv/live_user_" + streamerName + "-320x180.jpg";

    let overlay = document.createElement("div");
    overlay.className = "notification-box__overlay";

    let rageText = document.createElement("span");
    rageText.className = "notification-box__rage";
    rageText.innerHTML = getRandomMessage("rage").replace("NAME", streamerName);
    rageText.classList.add("rage-font-" + getRandomInt(1,5));
    rageText.classList.add("shake");

    // ---- Append Children ----

    notificationBody.appendChild(streamImg);
    notificationBody.appendChild(overlay);
    notificationBody.appendChild(rageText);

    topBar.appendChild(title);
    topBar.appendChild(xButton);

    atag.appendChild(notificationBody);

    notification.appendChild(topBar);
    notification.appendChild(atag);

    wrapper.appendChild(notification);

    return wrapper;

}


function addAnimationInit()
{
  let selector = ".top-nav__menu, .tw-button, .top-nav__nav-link, .tw-button__text, .directory-header__link, .tw-button--hollow, .directory-tabs__item";
  addClassToList( S(selector) , "rage-animation-init" );

  let topbar = S(".top-nav__menu")[0];
  if (topbar != null)
  {
    topbar.classList.add("rage-red-bg");
  }
}

function redify()
{
  selectorsAndClasses.forEach(item => addClassToList( S(item.selector) , item.className ));
}

function deredify()
{
  selectorsAndClasses.forEach(item => removeClassToList( S(item.selector) , item.className ));

}

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

  if(rageItem != null)
  {
    rageItem.appendChild(overlayDiv);
    rageItem.appendChild(overlayText);
  }
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
    addClassToList(divsToDelete, "status-fadeOut");
    setTimeout(function() { divsToDelete.forEach(item => item.remove()) }, 1500)

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
