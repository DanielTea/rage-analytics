console.log("POPOPOPOPUP");

// left Max
let pointer = document.getElementById("slider-pointer");
let slider = document.querySelector(".confidence-slider-outer");
let text = document.getElementById("sensibility");
let startedCorrect = false;

let timeout;


slider.addEventListener("mouseup", function(evt) {
    if (timeout != null)
    {
        clearTimeout(timeout);
    }
    let mouseX = evt.clientX > 280 ? 260 : evt.clientX -20; 
    console.log(evt.clientX) 
    console.log(mouseX)    
    let percent = (mouseX) / 260;
    percent = percent < 0 ? 0 : percent;
    console.log(percent);
    pointer.setAttribute("style", "left: " + mouseX + "px;")

    let percentDisplay = percent * 100;
    sensibility.textContent = "RAGOMETER " + Math.round(percentDisplay) + "%";

    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {confidence: percent}, function(response) {
    console.log(response.farewell);
  });
});

//     timeout = setTimeout(window.close, 3000);
 })


