$(".field").on("focus", function () {
    $(this).next().css("background-color", "transparent");
    $(this).next().css("top", "-60%");
})

$(".field").on("focusout", function () {
    $(this).next().css("background-color", "white");
    $(this).next().css("top", "-25%");
})