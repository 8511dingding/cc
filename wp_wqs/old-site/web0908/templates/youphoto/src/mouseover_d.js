/**
	MooMenu 
**/

window.addEvent('domready',function(){var main=$("horiznav_d");levels=new Array();effects1=new Array();var nodes=main.getChildren();nodes.each(function(el,i){levels[i]=new Array();effects1[i]=new Array();var subs=el.getElementsBySelector('ul');subs.each(function(elm,j){levels[i][j]=elm.getParent();effects1[i][j]=new Fx.Style(elm,'opacity',{wait:false,duration:500});effects1[i][j].set(0)})});levels.each(function(e,k){e.each(function(a,l){a.addEvent("mouseenter",function(){effects1[k][l].start(1)});if(!a.hasClass('active')){a.addEvent("mouseleave",function(){effects1[k][l].start(0)})}})})});
