let connectionStatus = document.querySelector("#connection-status");
let user = null;
let chatSocket;

function connectWebSocket() {
    connectionStatus.style.color = "green";
    connectionStatus.textContent = "Connection is establishing...";
    console.log("Connection started.")
    chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/chat/'
        + 'room/'
    );

    chatSocket.onopen = function () {
        connectionStatus.textContent = "Connection was successfully established.";
        connectionStatus.style.color = "green";

        console.log("CONNECTED")

        navbar.style.marginTop = "-80vh";
    }


    chatSocket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');

        if (chatSocket.readyState === WebSocket.CLOSED) {
            connectionStatus.style.color = "red";
            document.querySelector('#connection-status').textContent = "Connection closed";
            let defaultReconnectTime = 5000;

            document.querySelector('#connection-status').textContent = `Reconnecting in ${Math.min(4000, defaultReconnectTime += defaultReconnectTime) / 1000} seconds`;
            setTimeout(
                function () {
                    console.log("Trying to reconnect websocket...")
                    connectWebSocket();

                }, Math.min(4000, defaultReconnectTime += defaultReconnectTime));

        }


    };

    function drawMessage(message) {
        var username;
        console.log(message)
        if (message.user !== undefined) {
            username = message.user.username;
            if (username === undefined) {
                username = message.user;
            }

        } else {
            username = message.user__username;
            if (username === undefined || username === null) {
                username = "Anon"
            }
        }
        let messageRow = document.createElement("div");
        messageRow.classList.add("row");
        messageRow.classList.add("w-100");
        let messageColumn = document.createElement("div");

        let messageBubble = document.createElement("div");
        messageBubble.classList.add("message-bubble");
        console.log(username, user.username)
        if (username === `${user.username}`) {
            messageBubble.classList.add("message-bubble-self");
            messageColumn.classList.add("offset-sm-8");
            messageColumn.classList.add("col-sm-4");
        } else {
            messageColumn.classList.add("col-sm-12");
        }

        let spanMessage = document.createElement("div");
        let messageMeta = document.createElement("div")
        messageMeta.classList.add("message-meta");
        let usernameDiv = document.createElement("div");
        let dateDiv = document.createElement("div");
        dateDiv.classList.add("date");
        usernameDiv.classList.add("username");
        usernameDiv.textContent = username;
        dateDiv.textContent = message['date'];
        messageMeta.appendChild(usernameDiv)
        messageMeta.appendChild(dateDiv)
        messageBubble.appendChild(messageMeta)
        spanMessage.textContent = message['text'];

        messageBubble.appendChild(spanMessage);
        messageColumn.appendChild(messageBubble);
        messageRow.appendChild(messageColumn);
        document.querySelector('#chat-log').appendChild(messageRow);
    }

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        if (data.room_id) {
            $('.room-header span').text(data.room_id)
        }
        if (data.user) {
            user = data.user;
            $(".username-change input").val(user.username)
            saveUser(user.id);
            return;
        }
        if (data.old_messages) {
            console.log("receiving old messages by user", user.id)
            let messages = JSON.parse(data.old_messages);
            for (i = 0; i < messages.length; i++) {
                drawMessage(messages[i])
            }
        } else {
            drawMessage(data.message)
        }
        scrollMessagesBottom();

    };
}

connectWebSocket()