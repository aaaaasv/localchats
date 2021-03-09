let currentScroll = $(window).scrollTop();
let navbar = document.querySelector("#navbar-main");
$(document).ready(function () {
    $(window).on('scroll', function () {
        check_scroll(2)
    })
})
let scrollingElement = $(window);
let pos;
connectionStatus.style.transition = "1s";

function showConnectionStatus() {
    $("#connection-status").show()
}

function hideConnectionStatus() {
    $("#connection-status").hide()
}


function check_scroll(page) {

    var scrollBottom = $('html').height() - scrollingElement.scrollTop() - $(window).height()
    var scrollTop = $(window).scrollTop();
    if (scrollTop - currentScroll < -2000 * page) {
        alert("DOWNLOADING...")
    }
    if (scrollBottom >= 60) {
        +$('#scroll-bottom-arrow').fadeIn()
        hideConnectionStatus()
    } else {
        showConnectionStatus()
        $('#scroll-bottom-arrow').fadeOut()
    }
}

function scrollMessagesBottom() {
    document.querySelector('#chat-log').scrollTo(0, document.querySelector('#chat-log').scrollHeight);
    document.querySelector('html').scrollTo(0, document.querySelector('html').scrollHeight);
}

$('.scroll-bottom').on('click', function () {
    scrollMessagesBottom()
})
scrollMessagesBottom()


document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function (e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};


document.querySelector('#chat-message-submit').onclick = function (e) {
    scrollMessagesBottom()
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'message': message,
        'location': pos,
        'old_room_id': $(".room-header span").text()

    }));
    messageInputDom.value = '';
};

function showLocation(position) {

    setTimeout(function () {

        pos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
        };
        console.log(pos.lat, pos.lng)
        if (chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify({
                'location': pos,
                'old_room_id': $(".room-header span").text()
            }));
        } else {
            showLocation(position)
        }
        console.log("Location has been sent")
    }, 500)
}

function errorHandler(err) {
    if (err.code === 1) {
        alert("Error: Access is denied!");
    } else if (err.code === 2) {
        alert("Error: Position is unavailable!");
    }
}

function getLocationUpdate() {

    if (navigator.geolocation) {
        // timeout at 60000 milliseconds (60 seconds)

        var options = {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0
        };
        var geoLoc = navigator.geolocation;
        console.log(geoLoc)
        geoLoc.watchPosition(showLocation, errorHandler, options);
    }
}

getLocationUpdate()

let isSettingsMenuOpen = false;

function openSettingsMenu() {
    $(".navbar").css("margin-top", 0);
    $(".open-menu-arrow").css("transform", "rotate(180deg) translateY(50px)");
    $(this).css("color", "white");
    $(".username-change").show()
    isSettingsMenuOpen = true;
}

function closeSettingsMenu() {
    $(".navbar").css("margin-top", "-80vh");
    $(".open-menu-arrow").css("transform", "translateY(5px)");
    $(this).css("color", "black");
    $(".username-change").hide()
    isSettingsMenuOpen = false;
}

$(".open-menu").on("click", function () {
    if (isSettingsMenuOpen) {
        closeSettingsMenu();
    } else {
        openSettingsMenu();
    }
})


$(".username-change").on("change", function () {
    chatSocket.send(JSON.stringify({
        'username':$(this).val()
    }));
})