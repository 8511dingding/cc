var jwfs = jQuery.noConflict();
    var crossFadeDelay = 6000;
    var crossFadeSpeed = 1000;
    var fpssLoaderDelay = 1000;
    var navTrigger = "click";
    var autoslide = true;
    var fpssPlayText = "Play";
    var fpssPauseText = "Pause";
    var fpssCookieName = "fpssCookie";
    var slideLoader = "slide-loading";
    var slideWrapper = "slide-wrapper";
    var slideClass = "slide";
    var navClass = "navi";
    var navClassActiveSuffix = "-active";
    var playPauseID = "fpss-container_playButton";
    var isShowing = 0;
    var firstDelay = false;
    var pauseFlag = false;
    var ppButton;
    var timer;
    var slideElements;
    var navElements;

    function initFrontpageSlideshow() {
        fpssDisplay(slideLoader, slideWrapper);
        ppButton = document.getElementById(playPauseID);
        if (autoslide) {
            showPauseButton();
        } else {
            showPlayButton();
        }
        slideElements = jwfs("body").find("." + slideClass);
        navElements = jwfs("body").find("." + navClass);
        if (slideElements.length == 0 || navElements.length == 0) {
            return false;
        }
        for (var i = 0; i < slideElements.length; i++) {
            if (navTrigger == "click") {
                navElements[i].onclick = function () {crossFade(this);};
            } else {
                navElements[i].onmouseover = function () {crossFade(this);};
            }
            if (i != 0) {
                jwfs(slideElements[i]).fadeOut(crossFadeSpeed);
            } else {
                navElements[i].className = navClass + navClassActiveSuffix;
            }
        }
    }


    function fpssDisplay(a, b) {
        var c = document.getElementById(a);
        var d = document.getElementById(b);
        if (c || d) {
            jwfs(c).show();
            jwfs(d).hide();
            setTimeout(function () {jwfs(c).hide();jwfs(d).fadeIn("def");}, fpssLoaderDelay);
        } else {
            return false;
        }
    }


    function crossFade(a) {
        currentSlide = null;
        for (var i = 0; i < navElements.length; i++) {
            if (a == navElements[i]) {
                currentSlide = i;
            }
        }
        if (currentSlide != isShowing) {
            if (slideElements[isShowing].offsetHeight) {
                jwfs(slideElements[isShowing]).fadeOut(crossFadeSpeed);
            }
            jwfs(slideElements[currentSlide]).fadeIn(crossFadeSpeed);
            navElements[isShowing].className = navClass;
            navElements[currentSlide].className = navClass + navClassActiveSuffix;
            isShowing = currentSlide;
            clearSlide();
        }
        return false;
    }


    function showPlayButton() {
        createCookie(fpssCookieName, "false");
        ppButton.innerHTML = fpssPlayText;
        ppButton.title = fpssPlayText;
        pauseFlag = true;
        clearTimeout(timer);
        firstDelay = false;
    }


    function showPauseButton() {
        createCookie(fpssCookieName, "true");
        ppButton.innerHTML = fpssPauseText;
        ppButton.title = fpssPauseText;
        pauseFlag = false;
        autoSlide();
    }


    function ppButtonClicked() {
        if (pauseFlag) {
            showPauseButton();
        } else {
            showPlayButton();
        }
    }


    function showNext() {
        if (slideElements.length <= 1) {
            return false;
        }
        if (slideElements[isShowing].offsetHeight) {
            jwfs(slideElements[isShowing]).fadeOut(crossFadeSpeed);
        }
        navElements[isShowing].className = navClass;
        if (isShowing == slideElements.length - 1) {
            isShowing = 0;
            jwfs(slideElements[isShowing]).fadeIn(crossFadeSpeed);
        } else {
            jwfs(slideElements[++isShowing]).fadeIn(crossFadeSpeed);
        }
        navElements[isShowing].className = navClass + navClassActiveSuffix;
    }


    function showPrev() {
        if (slideElements.length <= 1) {
            return false;
        }
        if (slideElements[isShowing].offsetHeight) {
            jwfs(slideElements[isShowing]).fadeOut(crossFadeSpeed);
        }
        navElements[isShowing].className = navClass;
        if (isShowing == 0) {
            isShowing = slideElements.length - 1;
            jwfs(slideElements[isShowing]).fadeIn(crossFadeSpeed);
        } else {
            jwfs(slideElements[--isShowing]).fadeIn(crossFadeSpeed);
        }
        navElements[isShowing].className = navClass + navClassActiveSuffix;
    }


    function autoSlide() {
        if (!pauseFlag) {
            timer = setTimeout("autoSlide()", crossFadeDelay);
            if (!firstDelay) {
                firstDelay = true;
            } else {
                showNext();
            }
        }
    }


    function clearSlide() {
        if (!pauseFlag) {
            clearTimeout(timer);
            firstDelay = false;
            autoSlide();
        }
    }


    function createCookie(a, b, c) {
        if (c) {
            var d = new Date;
            d.setTime(d.getTime() + c * 24 * 60 * 60 * 1000);
            var e = "; expires=" + d.toGMTString();
        } else {
            e = "";
        }
        document.cookie = a + "=" + b + e + "; path=/";
    }


    function readCookie(a) {
        var b = a + "=";
        var d = document.cookie.split(";");
        for (var i = 0; i < d.length; i++) {
            var c = d[i];
            while (c.charAt(0) == " ") {
                c = c.substring(1, c.length);
            }
            if (c.indexOf(b) == 0) {
                return c.substring(b.length, c.length);
            }
        }
        return null;
    }

    jwfs(document).ready(function () {initFrontpageSlideshow();});