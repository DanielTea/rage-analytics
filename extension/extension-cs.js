var socket = io.connect('http://127.0.0.1:5000/stream');

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
let timeOutNoRageInViewport;

let rageLimit = 0.6;

// tell the background script o start a new Session
let toDo = checkUrl();
toDo();
buildSettingsIcon();


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
  console.log("Rage Incoming " + msg.link + " " + msg.confidence);
  if (msg.confidence > rageLimit && msg.game == activeGame)
  {
    if( regExForStreamerSelection.test(currentUrl) )
    {
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

      checkIfNoRageIsInViewport();

    }
    else if(regExForWatchingAStream.test(currentUrl))
    {
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

function checkIfNoRageIsInViewport()
{

  let ragingStreamers = S(".rage-overlay");
  let flag = ragingStreamers.some(raging => raging.getBoundingClientRect().top < window.innerHeight);

  if (!flag && S(".no-rage-viewport-outer").length == 0)
  {
    let outerDiv = document.createElement("div");
    let innerDiv = document.createElement("div");
    let span = document.createElement("span");

    outerDiv.classList.add("no-rage-viewport-outer");
    outerDiv.classList.add("animated");
    outerDiv.classList.add("slideInLeft");
    innerDiv.classList.add("no-rage-viewport-inner");
    span.classList.add("no-rage-viewport-text");

    document.body.appendChild(outerDiv);
    outerDiv.appendChild(innerDiv);
    innerDiv.appendChild(span);

    span.textContent = "Scroll down to see the rage!"
  }
  else
  if (flag && S(".no-rage-viewport-outer").length != 0)
  {
    let oldElem = S(".no-rage-viewport-outer")[0];
    oldElem.classList.add("slideOutLeft");
    setTimeout( function() {
      oldElem.remove()
    }, 1000);
  }
  console.log("IS IN VIEWPORT " + flag)

  clearTimeout(timeOutNoRageInViewport);
  timeOutNoRageInViewport = setTimeout(function () {
    let oldElem = S(".no-rage-viewport-outer")[0];
    if (oldElem != null)
    {
      oldElem.classList.add("slideOutLeft");
      setTimeout( function() {
        oldElem.remove()
      }, 1000);
    }
  },3000);

}

function buildSettingsIcon()
{
  let parentElement = document.body;
  let divOuter = document.createElement("div");
  let divInner = document.createElement("div");

  let barContainer = document.createElement("div");
  let timeout;


  divOuter.classList.add("settings-outer");
  divInner.classList.add("settings-inner");
  barContainer.classList.add("settings-container")

  divInner.innerHTML = `<?xml version="1.0" encoding="utf-8"?> <!-- Generator: Adobe Illustrator 16.0.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
  <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1 Tiny//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11-tiny.dtd">
  <svg version="1.1" baseProfile="tiny" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
  	 x="0px" y="0px" width="100px" height="100px" viewBox="0 0 100 100" xml:space="preserve">
  <g>
  	<path fill="#FFFFFF" d="M92.229,56.212c0,0.826-0.662,1.816-1.538,1.98l-10.174,1.539c-0.604,1.76-1.267,3.411-2.145,5.007
  		c1.868,2.692,3.848,5.11,5.885,7.587c0.327,0.385,0.549,0.878,0.549,1.375c0,0.493-0.164,0.877-0.493,1.263
  		c-1.322,1.759-8.746,9.844-10.614,9.844c-0.496,0-0.99-0.221-1.431-0.498l-7.587-5.935c-1.595,0.824-3.299,1.538-5.002,2.087
  		c-0.389,3.355-0.718,6.931-1.596,10.229c-0.22,0.877-0.99,1.538-1.979,1.538H43.896c-0.99,0-1.868-0.712-1.98-1.65l-1.54-10.117
  		c-1.703-0.549-3.354-1.21-4.946-2.031l-7.756,5.879c-0.385,0.333-0.878,0.498-1.375,0.498c-0.493,0-0.99-0.221-1.375-0.605
  		c-2.914-2.637-6.762-6.048-9.07-9.238c-0.277-0.386-0.385-0.822-0.385-1.263c0-0.497,0.164-0.882,0.437-1.267
  		c1.872-2.529,3.904-4.946,5.776-7.531c-0.934-1.76-1.704-3.575-2.257-5.442l-10.06-1.487c-0.934-0.165-1.595-1.043-1.595-1.98
  		V43.788c0-0.826,0.661-1.816,1.483-1.979l10.228-1.54c0.55-1.759,1.267-3.411,2.145-5.058c-1.868-2.642-3.848-5.114-5.884-7.592
  		c-0.329-0.385-0.549-0.821-0.549-1.319c0-0.492,0.22-0.877,0.493-1.262c1.323-1.816,8.746-9.845,10.613-9.845
  		c0.497,0,0.99,0.221,1.431,0.55l7.587,5.884c1.595-0.825,3.299-1.539,5.002-2.088c0.389-3.354,0.718-6.931,1.596-10.229
  		c0.22-0.877,0.99-1.538,1.98-1.538h12.208c0.989,0,1.868,0.713,1.979,1.65l1.539,10.117c1.704,0.549,3.355,1.21,4.947,2.032
  		l7.812-5.88c0.327-0.333,0.821-0.498,1.317-0.498c0.493,0,0.991,0.221,1.375,0.55c2.915,2.693,6.763,6.104,9.07,9.347
  		c0.276,0.333,0.385,0.77,0.385,1.21c0,0.498-0.164,0.883-0.436,1.268c-1.873,2.529-3.905,4.946-5.776,7.531
  		c0.934,1.759,1.704,3.575,2.256,5.391l10.061,1.539c0.934,0.164,1.596,1.042,1.596,1.979V56.212z M50,35.924
  		c-7.751,0-14.077,6.325-14.077,14.076c0,7.752,6.325,14.076,14.077,14.076c7.751,0,14.076-6.324,14.076-14.076
  		C64.076,42.249,57.751,35.924,50,35.924z"/>
  </g>
  <g>
  </g>
  <g>
  </g>
  <g>
  </g>
  <g>
  </g>
  <g>
  </g>
  <g>
  </g>
  </svg>`;

  parentElement.appendChild(divOuter);
  divOuter.appendChild(divInner);
  divOuter.appendChild(barContainer);

  for (let i = 0; i <= 4; i++)
  {
    let bar = document.createElement("div");
    bar.classList.add("settings-bar");
    let height = 5*(i+1);
    let left = 20*(i+1);
    bar.setAttribute("style", "height: " + height + "px; left: " + left + "px;")
    bar.setAttribute("data-index", i);
    barContainer.appendChild(bar);

    if (i < 4)
      bar.classList.add("selected")

    bar.addEventListener("click", function(evt) {
      if (evt.currentTarget.classList.contains("selected"))
      {
        let allBars = S(".settings-bar");
        let index = evt.currentTarget.getAttribute("data-index");
        let checkIfOthers = true;
        allBars.forEach( b => {
          if (b.getAttribute("data-index") > index)
          {
            b.classList.remove("selected");
          }
        });

        rageLimit = 0.2 * index;
        console.log("NEW LIMIT " + rageLimit);
      }
      else
      {
        let elem = evt.currentTarget;
        let index = elem.getAttribute("data-index");

        for (let j = 0; j <= index; j++)
        {
          let barToSelect = S(".settings-bar[data-index='" + j + "']")[0];
          barToSelect.classList.add("selected");
        }
        rageLimit = 0.2 * index;
        console.log("NEW LIMIT " + rageLimit);

      }
      clearTimeout(timeout);
      timeout = setTimeout(function() {
        divInner.children[0].classList.remove("rotated");
        divOuter.classList.remove("expanded")
      }, 3000);
    })
  }
  divInner.addEventListener("click", function() {
    if (  divOuter.classList.contains("expanded"))
    {
      divInner.children[0].classList.remove("rotated");
      divOuter.classList.remove("expanded")
      clearTimeout(timeout);
    }
    else
    {
      divInner.children[0].classList.add("rotated");
      divOuter.classList.add("expanded");
      timeout = setTimeout(function() {
        divInner.children[0].classList.remove("rotated");
        divOuter.classList.remove("expanded")
      }, 3000);
    }
  });
}

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
