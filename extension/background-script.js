
console.log("HELLO FROM BACKGROUND SCRIPT");

let numberOfConcurrentStreamers;
let currentStreamer = new Map();
let currentSessionId;

chrome.runtime.onMessage.addListener(function(msg, sender, sendResponse)
{
    console.log(msg);

    // console.log("Received %o from %o, frame", msg, sender.tab, sender.frameId);
    if (msg.type == "initSession")
    {
      currentStreamer.clear();
      sendResponse("cleared bg");
    }
    else
    if (msg.type == "saveStreamer")
    {
      updateStreamer(msg);
      sendResponse("Gotcha! " + msg.type);
    }
    else
    if (msg.type == "getStreamer")
    {
      if (currentStreamer.has(msg.data))
      {
        sendResponse(JSON.stringify(currentStreamer.get(msg.data)));
      }
      else
      {
        sendResponse(JSON.stringify(false));
      }
    }
    else
    {
        console.log("SOMETHING FUUUUUNKY");
        console.log(msg);
    }

});

function initSession(msg)
{
  currentSessionId = msg.sessionId;
  numberOfConcurrentStreamers = msg.numberOfConcurrentStreamers;
  console.log("Set session Id");
}

function updateStreamer(msg)
{
    let data  = JSON.parse(msg.data);
    data.forEach(streamer => currentStreamer.set(streamer.name, streamer))
    console.log(currentStreamer);
}
