$(".field").on("focus", function () {
    $(this).next().css("background-color", "transparent");
    $(this).next().css("top", "-60%");
})

$(".field").on("focusout", function () {
    $(this).next().css("background-color", "white");
    $(this).next().css("top", "-25%");
})

$(".login-btn").on("click", function () {
    $(".form-container .signup-form").css("margin-right", "400%");
    $(".login-form").css("margin-right", "0%");
    $(".auth-type-btn .signup-btn").css("color", "rgba(0, 0, 0, .3)");
    $(".auth-type-btn .login-btn").css("color", "black");
})


$(".signup-btn").on("click", function () {
    $(".form-container .signup-form").css("margin-right", "0");
    $(".login-form").css("margin-right", "-200%");
    $(".auth-type-btn .signup-btn").css("color", "black");
    $(".auth-type-btn .login-btn").css("color", "rgba(0, 0, 0, .3)");
})

$(window).on("load", function () {


    let pathArray = window.location.pathname.split('/');
    if (pathArray[pathArray.length - 2] !== "signup") {
        $(".login-btn").trigger("click")
    }
})