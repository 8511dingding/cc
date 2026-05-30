// JavaScript Document

var sld = new Slider("idSlider", "idBar", {
	MaxValue: $("idContent").scrollWidth - $("idContent").clientWidth,
	onMin: function(){ $("idSliderLeft").style.backgroundPosition = "bottom left"; },
	onMax: function(){ $("idSliderRight").style.backgroundPosition = "bottom right"; },
	onMid: function(){ $("idSliderLeft").style.backgroundPosition = "top left"; $("idSliderRight").style.backgroundPosition = "top right"; },
	onMove: function(){ $("idContent").scrollLeft = this.GetValue(); }
});

sld.SetPercent(.5);
sld.Ease = true;

$("idSliderLeft").onmouseover = function(){ sld.Run(false); }
$("idSliderLeft").onmouseout = function(){ sld.Stop(); }

$("idSliderRight").onmouseover = function(){ sld.Run(true); }
$("idSliderRight").onmouseout = function(){ sld.Stop(); }