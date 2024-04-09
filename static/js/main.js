document.addEventListener("DOMContentLoaded", function () {
    let prevScrollPos = window.scrollY || window.pageYOffset;

    window.onscroll = function () {
        let currentScrollPos = window.scrollY || window.pageYOffset;
        if (prevScrollPos > currentScrollPos) {
            // Scrolling up
            document
                .getElementById("navbar")
                .classList.remove("navbar-scrolled");
        } else {
            // Scrolling down
            document.getElementById("navbar").classList.add("navbar-scrolled");
        }
        prevScrollPos = currentScrollPos;
    };
});
