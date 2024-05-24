//* LEARN.HTML

//* Elements
const main = document.querySelector("main");
const darkModeCheckbox = document.getElementById("checkbox");
const dyslexicCheckbox = document.getElementById("dyslexic-checkbox");
const twoColRight = document.querySelector(".two-col-right");
const twoColLeft = document.querySelector(".two-col-left");
const container = document.querySelector(".chat-two-col");
const sessions = document.querySelector(".sessions-scrollbar");
const collapseButton = document.querySelector(".collapse-history");
const sendBtn = document.querySelector(".btn-send");
const messagesList = document.querySelector(".messages-list");
const messageForm = document.querySelector(".new-message-form");
const messageInput = document.querySelector(".new-message-input");

//* Channels
let url = `ws://${window.location.host}/ws/socket-server/`;
const chatSocket = new WebSocket(url);

//* Flags
let isDarkMode = false;

//* This function directs where to display messages and responses
chatSocket.onmessage = function (e) {
  let data = JSON.parse(e.data);
  //* @see https://www.hiclipart.com/free-transparent-background-png-clipart-dcdxh/
  const avatarUrl = "/static/media/robot.png";

  if (data.type !== "chat" && data.type !== "connected") {
    console.log("Dataaa", data);
    let messageId = data.message_id;
    let response = data.message;
    let remove_spinner = messagesList.lastChild;
    const messageItem = document.createElement("div");
    messageItem.classList.add("message-container");
    data.type !== "reject"
      ? isDarkMode
        ? (messageItem.innerHTML = `
          <img src="${avatarUrl}" alt="Robot Avatar" class="avatar-ai" />
          <li class="message received dark">
            <div class='message-text'>
              <p class='message-sender'>
                <b>Chatbot</b>
              </p>
              <p class='message-content'>
                ${response}
              </p>
              <div class='feedback-buttons'>
                <button class="like-button" data-message-id="${messageId}">👍</button>
                <button class="dislike-button" data-message-id="${messageId}">👎</button>
                <input type="text" class="feedback-input" id="feedback-input" data-message-id="${messageId}" maxlength=280 placeholder="Type your feedback here and press Enter"/>
              </div>
            </div>
          </li>
          `)
        : (messageItem.innerHTML = `
          <img src="${avatarUrl}" alt="Robot Avatar" class="avatar-ai" />
          <li class="message received">
            <div class='message-text'>
              <p class='message-sender'>
                <b>Chatbot</b>
              </p>
              <p class='message-content'>
                ${response}
              </p>
              <div class='feedback-buttons'>
                <button class="like-button" data-message-id="${messageId}">👍</button>
                <button class="dislike-button" data-message-id="${messageId}">👎</button>
                <input type="text" class="feedback-input" id="feedback-input" data-message-id="${messageId}" maxlength=280 placeholder="Type your feedback here and press Enter"/>
              </div>
            </div>
          </li>
          `)
      : isDarkMode
      ? (messageItem.innerHTML = `
              <img src="${avatarUrl}" alt="Robot Avatar" class="avatar-ai" />
              <li class="message received dark">
                <div class='message-text'>
                  <p class='message-sender'>
                      <b>Chatbot</b>
                  </p>
                  <p class='message-content'>
                      ${response}
                  </p>
                </div>
              </li>
          `)
      : (messageItem.innerHTML = `
              <img src="${avatarUrl}" alt="Robot Avatar" class="avatar-ai" />
              <li class="message received">
                <div class='message-text'>
                  <p class='message-sender'>
                      <b>Chatbot</b>
                  </p>
                  <p class='message-content'>
                      ${response}
                  </p>
                </div>
              </li>
          `);
    messagesList.appendChild(messageItem);
    messagesList.removeChild(remove_spinner);
    sendBtn.disabled = false;
  }
};

//* Event listeners
darkModeCheckbox.addEventListener("change", toggleDarkMode);
dyslexicCheckbox.addEventListener("change", () =>
  main.classList.toggle("dyslexic")
);
collapseButton.addEventListener("click", toggleTwoColumn);
messageForm.addEventListener("submit", submitMessage);
messagesList.addEventListener("click", handleLikeClick);
messagesList.addEventListener("click", handleDislikeClick);
messagesList.addEventListener("keypress", handleWrittenFeedback);

//* Dark mode
function toggleDarkMode() {
  const received = document.querySelectorAll(".received");
  const sent = document.querySelectorAll(".sent");

  twoColRight.classList.toggle("dark");
  twoColLeft.classList.toggle("dark");
  isDarkMode = !isDarkMode;

  if (received) {
    received.forEach((rec) => {
      r = rec.classList;
      r.toggle("dark");
    });
  }
  if (sent) {
    sent.forEach((sen) => {
      s = sen.classList;
      s.toggle("dark");
    });
  }
}

//* Expand two-column style
function toggleTwoColumn() {
  cl = container.classList;
  sl = sessions.classList;
  cl.toggle("expanded");
  sl.toggle("hidden");
}

//* Submit message to Oz
function submitMessage(event) {
  event.preventDefault();
  sendBtn.disabled = true;

  const message = messageInput.value.trim();
  if (message.length === 0) return;

  // Append message to chat
  const messageItem = document.createElement("div");
  messageItem.classList.add("message-container", "sent-end");
  isDarkMode
    ? (messageItem.innerHTML = `
          <li class="message sent dark">
            <div class='message-text'>
                <p class='message-sender'>
                    <b>You</b>
                </p>
                <p class='message-content'>
                    ${message}
                </p>
            </div>
          </li>
          `)
    : (messageItem.innerHTML = `
          <li class="message sent">
            <div class='message-text'>
                <p class='message-sender'>
                    <b>You</b>
                </p>
                <p class='message-content'>
                    ${message}
                </p>
            </div>
          </li>
          `);
  messagesList.appendChild(messageItem);
  messageInput.value = "";

  // Append spinner to chat temporarily
  const spinner = document.createElement("div");
  spinner.classList.add("stage");
  spinner.innerHTML = `
    <div class="dot-typing"></div>
  `;
  messagesList.appendChild(spinner);

  fetch("", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      csrfmiddlewaretoken: document.querySelector("[name=csrfmiddlewaretoken]")
        .value,
      message: message,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("dataa", data);
      // Send message to learn/oz.html
      chatSocket.send(
        JSON.stringify({
          type: "chat",
          message_id: 0,
          message: message,
        })
      );
    });
}

//* Thumbs up clicked by user
async function handleLikeClick(event) {
  console.log();
  if (!event.target.classList.contains("like-button")) return; // Check for like button

  const messageId = event.target.dataset.messageId;
  const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  const response = await fetch("/learn/thumbs-up", {
    method: "POST",
    body: JSON.stringify({ message_id: messageId }),
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
  });
  console.log(response);
  event.target.classList.toggle("active");
  if (event.target.nextElementSibling.classList.contains("active")) {
    event.target.nextElementSibling.classList.toggle("active");
  }
}

//* Thumbs down clicked by user
async function handleDislikeClick(event) {
  if (!event.target.classList.contains("dislike-button")) return;

  const messageId = event.target.dataset.messageId;
  const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  const response = await fetch("/learn/thumbs-down", {
    method: "POST",
    body: JSON.stringify({ message_id: messageId }),
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
  });
  console.log(response);

  event.target.classList.toggle("active");
  if (event.target.previousElementSibling.classList.contains("active")) {
    event.target.previousElementSibling.classList.toggle("active");
  }
}

async function handleWrittenFeedback(event) {
  if (!event.target.classList.contains("feedback-input")) return;
  if (event.key === "Enter") {
    const feedbackInput = event.target;
    const messageId = event.target.dataset.messageId;
    const feedbackText = feedbackInput.value;
    const csrftoken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    const response = await fetch("/learn/written-feedback", {
      method: "POST",
      body: JSON.stringify({ message_id: messageId, feedback: feedbackText }),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
    });
    feedbackInput.value = "";
    console.log(response);
  }
}
