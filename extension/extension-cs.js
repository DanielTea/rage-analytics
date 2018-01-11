var socket = io.connect('http://127.0.0.1:5000/');

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
const numberOfConcurrentStreamers = 5;

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

let currentUrl = window.location.href;
let intervalData;
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
  clearInterval(intervalData);

  // For getting getting and sending the data;
  intervalData = setTimeout( function()
  {
    let streamerList = getStreamerData();
    console.log(streamerList);
    let streamerNameList = streamerList.map(streamer => streamer.name)
    console.log(streamerNameList);
    //example: ["/shantao", "/summonersinnlive", "/gurke4life", "/players_hub", "/sallicex"]

    console.log("send data " + streamerNameList);
    socket.emit('sendStreamer', streamerNameList);
    //saveCurrentStreamers(streamerList);
  }, heartbeatTime);

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

function initEventsAndIntervalsWatching()
{
  clearInterval(intervalUrl);
  clearInterval(intervalData);

  // For getting getting and sending the data;
  intervalData = setInterval( function()
  {
    getSavedStreamer();
  }, heartbeatTime);

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
  clearInterval(intervalData);

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
  console.log("getrStreamerData list:", list);

  let fiveFirst = list.slice(0,numberOfConcurrentStreamers);
  console.log("getrStreamerData 5first:", fiveFirst);

  let data = [];
  fiveFirst.forEach(item => data.push(createStreamerData(item)));
  console.log(data);

  return data;
}

function createStreamerData(elem)
{
  console.log(elem)

  /*
  <div class="tw-card tw-relative">
     <div class="tw-flex tw-flex-column tw-flex-nowrap">
        <div class="tw-full-width ">
           <figure class="tw-aspect tw-aspect--overflow tw-aspect--16x9 tw-aspect--align-top">
              <div>
!                 <a title="[GER] Teemo Clizckbait Dia 4 MMR Wuhu Yeah Lol Yeah" data-a-target="live-channel-card-thumbnail-link" href="/shantao">
                    <div class="tw-card-img tw-flex-shrink-0">
                       <figure class="tw-aspect tw-aspect--16x9 tw-aspect--align-top"><img src="https://static-cdn.jtvnw.net/previews-ttv/live_user_shantao-320x180.jpg" alt="shantao cover image"></figure>
                    </div>
                    <div class="rage-overlay rage-overlay-style-darker" id="rage-overlay-shantao"></div>
                    <span class="rage-overlay-text rage-font-4 shake">too bad,  shantao</span>
                 </a>
              </div>
           </figure>
        </div>
        <div class="tw-card-body tw-relative">
           <a class="live-channel-card__channel" data-a-target="live-channel-card-title-link" href="/shantao">
              <h3 class="live-channel-card__title tw-mg-t-05 tw-ellipsis tw-font-size-5 tw-line-height-body" title="[GER] Teemo Clickbait Dia 4 MMR Wuhu Yeah Lol Yeah">[GER] Teemo Clickbait Dia 4 MMR Wuhu Yeah Lol Yeah</h3>
           </a>
           <div class="live-channel-card__meta tw-flex tw-flex-nowrap">
              <span class="tw-ellipsis">
                 <a class="live-channel-card__videos" data-a-target="live-channel-card-channel-name-link" href="/shantao/videos">Shantao</a><!-- react-text: 1813 --> hat 1.095 Zuschauer<!-- /react-text -->
              </span>
           </div>
        </div>
     </div>
  </div>
   */
  console.log(elem)
  let aTag = elem.firstChild.firstChild.firstChild.firstChild.firstChild;
  let streamerName = aTag.href.replace("https://www.twitch.tv", "");

  let example = { "name" : streamerName,
                  "title" : aTag.title,
                  "img" : "https://static-cdn.jtvnw.net/previews-ttv/live_user_" + streamerName.substr(1) + "-320x180.jpg"
  }

  console.log("new Streamer Object:", example);

  return example
}

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
  let old = getData();

  old.forEach( function(item)
  {
      document.querySelector("a[href='" + item + "'] > div").style.border = "" ;
  });

  unshowRage();

  if (msg == "%no-rage")
  {
    deredify();
    console.log("NO RAGE");
  }
  else
  {
    redify();
    showRage(msg);
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

function unshowRage()
{
  let allOverlays = S(".rage-overlay, .rage-overlay-text");

  allOverlays.forEach(item => {
      item.remove();
  });
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

function saveCurrentStreamers(streamerList)
{
  let message = {"type": "updateStreamer", "data": streamerList, "sessionId": sessionId }
  chrome.runtime.sendMessage(message, function(response) {
      console.log(response);
  });
}

function getSavedStreamer()
{
  let message = {"type": "getStreamer", "sessionId": sessionId }
  chrome.runtime.sendMessage(message, function(response) {
      console.log("GOT FUCKING STREAMER FROM BG")
      console.log(response);
  });
}

// first para is the message, the sencond the callback which will be again in the scope of this content script
// chrome.runtime.sendMessage({text: "hey"}, function(response) {
//     console.log("Response: ", response);
// });
