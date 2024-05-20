// * OZ.HTML

//* Elements
const approveButton = document.getElementById("approve-message");
const rejectButton = document.getElementById("reject-message");
const editButton = document.getElementById("edit-message");
const completeButton = document.getElementById("edit-complete");

//* Channels
let url = `ws://${window.location.host}/ws/socket-server/`;
const chatSocket = new WebSocket(url);

// Listen for incoming messages and display them
chatSocket.onmessage = function (e) {
  let data = JSON.parse(e.data);
  if (data.type === "chat") {
    document.getElementById("message").innerHTML = data.message;
  }
};

function clearFields() {
  document.getElementById("edit-textarea").value = "";
  document.getElementById("message").innerHTML = "";
}

rejectButton.addEventListener("click", (event) => {
  event.preventDefault();
  raw_msg = document.getElementById("message").innerHTML;
  if (!raw_msg) return;

  message = "HIPAA! The message has been rejected!";
  fetch("", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      csrfmiddlewaretoken: document.querySelector("[name=csrfmiddlewaretoken]")
        .value,
      type: "reject",
      message: message,
    }),
  }).then(() => {
    chatSocket.send(
      JSON.stringify({
        type: "reject",
        message: message,
      })
    );
  });

  clearFields();
});

editButton.addEventListener("click", (event) => {
  event.preventDefault();
  raw_msg = document.getElementById("message").innerHTML;
  if (!raw_msg) return;
  document.getElementById("edit-textarea").value = raw_msg;
});

approveButton.addEventListener("click", (event) => {
  event.preventDefault();
  raw_msg = document.getElementById("message").innerHTML;
  if (!raw_msg) return;

  fetch("", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      csrfmiddlewaretoken: document.querySelector("[name=csrfmiddlewaretoken]")
        .value,
      type: "approve",
      message: raw_msg,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Access the data from the JSON response
      console.log("Dataa", data)
      const messageId = data.message_id;
      const responseText = data.response;
      chatSocket.send(
        JSON.stringify({
          type: "approve",
          message_id: messageId,
          message: responseText,
        })
      );
    });

  clearFields();
});

completeButton.addEventListener("click", (event) => {
  event.preventDefault();
  edit_content = document.getElementById("edit-textarea").value;
  if (!edit_content) return;

  fetch("", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      csrfmiddlewaretoken: document.querySelector("[name=csrfmiddlewaretoken]")
        .value,
      type: "complete",
      message: edit_content,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Access the data from the JSON response
      const messageId = data.message_id;
      const responseText = data.response;
      chatSocket.send(
        JSON.stringify({
          type: "complete",
          message_id: messageId,
          message: responseText,
        })
      );
    });

  clearFields();
});
