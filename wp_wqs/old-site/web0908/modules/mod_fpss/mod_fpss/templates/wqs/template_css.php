<?php
header("Content-type: text/css; charset: UTF-8");
$width = $_GET['w'];
$height = $_GET['h'];
$sidebar_width = $_GET['sw'];
?>

/* --- Slideshow Containers --- */
#fpss-outer-container {width:<?php echo $width; ?>px;padding:0;margin:4px auto;border:2px solid #ccc;}
#fpss-container {/*clear:both;*/border:none;padding:0;margin:0;position:relative;width:<?php echo $width; ?>px;}
#fpss-slider {overflow:hidden;background:none;/*clear:both;*/width:<?php echo $width; ?>px;height:<?php echo $height; ?>px;}
#slide-loading {background:#000 url(loading_black.gif) no-repeat center;text-align:center;width:<?php echo $width; ?>px;height:<?php echo $height; ?>px;}
#slide-wrapper {display:none;font-size:11px;text-align:left;width:<?php echo $width; ?>px;height:<?php echo $height; ?>px;}
#slide-wrapper #slide-outer {height:<?php echo $height; ?>px;}
#slide-wrapper #slide-outer .slide {position:absolute;right:0;overflow:hidden;width:<?php echo $width; ?>px;height:<?php echo $height; ?>px;}
#slide-wrapper #slide-outer .slide .slide-inner {position:relative;margin:0px;color:#fff;overflow:hidden;background:#000;height:<?php echo $height; ?>px;}
#slide-wrapper #slide-outer .slide .slide-inner a.fpss_img span span span {background:none;}

/* --- Content --- */
.fpss-introtext {margin:0;padding:0;position:absolute;bottom:0px;left:0;background:url(transparent_bg.png);width:500px;height:62px;overflow:hidden;}
.fpss-introtext .slidetext {margin:0;padding:0 8px;font-size:11px;}

/* --- Navigation Buttons --- */
#pseudobox {position:absolute;float:right;top:3px;left:0;right:0;height:62px;margin:0;padding:0;background:url(transparent_bg.png);opacity:0.8;-moz-opacity:0.8;filter:alpha(opacity=80);width:<?php echo $sidebar_width; ?>px;}
#navi-outer {position:absolute;left:500px;right:0;z-index:9;bottom:0px;width:<?php echo $sidebar_width; ?>px;}
#navi-outer ul {margin:0;padding:0;text-align:right;display:block;}
#navi-outer li {display:inline;background:none;padding:0;margin:0;}
#navi-outer li a,
#navi-outer li a:hover,
#navi-outer li a.navi-active {display:block;float:left;overflow:hidden;width:98px;height:65px;padding:0;margin:0 2px;text-decoration:none;position:relative;}
#navi-outer li a {background:none;}
#navi-outer li a:hover,
#navi-outer li a.navi-active {no-repeat 49% 0;}
#navi-outer li a img,
#navi-outer li a:hover img,
#navi-outer li a.navi-active img {width:87px;height:58px;margin:8px 0 0 0;padding:0;}
#navi-outer li a img {opacity:0.7;-moz-opacity:0.7;filter:alpha(opacity=70);border:1px solid #aaa;}
#navi-outer li a:hover img,
#navi-outer li a.navi-active img {opacity:1.0;-moz-opacity:1.0;filter:alpha(opacity=100);border:1px solid #DCD6A9;width:90px;height:62px;margin:6px 0 0 0;padding:0;}
#navi-outer li a span.navbar-key {display:none;}
#navi-outer li a span.navbar-title {display:none;}
#navi-outer li a span.navbar-tagline {display:none;}
#navi-outer li a span.navbar-clr {display:none;}
#navi-outer li.noimages a {display:none;}
#navi-outer li.noimages a:hover {display:none;}
#navi-outer li.noimages a#fpss-container_prev {display:none;}
#navi-outer li.noimages a#fpss-container_playButton {display:none;}
#navi-outer li.noimages a#fpss-container_next {display:none;}

/* Notice: Add custom text styling here to overwrite your template's CSS styles! */
.fpss-introtext .slidetext h1 {font-size:20px;margin:0;padding:0;color:#dcdcdc;font-weight:bold;}
.fpss-introtext .slidetext h1 a {color:#DCD6A4;font-weight:bold;font-size:20px;}
.fpss-introtext .slidetext h1 a:hover {color:#f7f7f7;font-weight:bold;font-size:20px;}
.fpss-introtext .slidetext h2 {display:none;}
.fpss-introtext .slidetext h3 {margin:0;padding:0;color:#fff;font-size:11px;}
.fpss-introtext .slidetext p {display:none;}
.fpss-introtext .slidetext a.readon {display:none;}
.fpss-introtext .slidetext a.readon:hover {display:none;}

/* --- Generic Styling (highly recommended) --- */
a:active,a:focus {outline:0;}
#fpss-container img {border:none;}
.fpss-introtext .slidetext img,
.fpss-introtext .slidetext p img {display:none;} /* this will hide images inside the introtext */
.fpss-clr {/*clear:both;*/height:0;line-height:0;}

/* --- End of stylesheet --- */