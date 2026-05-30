/*======================================================================*\
|| #################################################################### ||
|| # Copyright ©2006-2009 Youjoomla LLC. All Rights Reserved.           ||
|| # This file may not be redistributed in whole or significant part. # ||
|| # ---------------- THIS IS NOT FREE SOFTWARE ---------------- #      ||
|| # http://www.youjoomla.com | http://www.youjoomla.com/license.html # ||
|| #################################################################### ||
\*======================================================================*/
/**
 * TabbedContent - mootools 1.1 tabs
 * @version		1.0.0
 * @MooTools version 1.1
 * @author		Constantin Boiangiu <info [at] constantinb.com>
 * Copyright Youjoomla LLC
 */

var Tabs = new Class({
	initialize: function(options) {
		this.options = Object.extend({
			container: null,
			tabsContainer: null,
			classContent: null
		}, options || {});
		
		this.container = $(this.options.container);
this.selectedTab = Cookie.get('selectedTab') ? Cookie.get('selectedTab').toInt() : 0;
	this.start();		
	},
	
	start: function(){
		this.tabs = $(this.options.tabsContainer).getElements('li');
		this.tabsContent = $(this.options.container).getElements('.'+this.options.classContent);		
		this.addFunctionality();		
	},
	
	addFunctionality: function(){
		this.tabs.each(function(tab, i){
			this.tabsContent[i]['fx'] = new Fx.Styles(this.tabsContent[i], {duration:400, wait:false, transition:Fx.Transitions.Sine.easeIn});
			var size = this.tabsContent[i].getCoordinates();
			this.tabsContent[i]['height'] = size.height;			
			
			tab.addEvent('click', function(){
				this.selectTab(i);
			}.bind(this));
			
			if(i!==this.selectedTab){
				this.tabsContent[i].setStyles({'display':'none'});		
			}else{
				tab.addClass('selected');
				// last tab add class last
				this.tabs[this.tabs.length-1].addClass( 'last' );
			}			
		}.bind(this));
	},
	
	selectTab: function(tab){
		if( tab == this.selectedTab ) return;
		/* deselect previous tab */
		this.tabs[this.selectedTab].removeClass( 'selected' );
		if(this.selectedTab == this.tabs.length-1) 
			this.tabs[this.selectedTab].addClass( 'last' );
		/* select current tab */
		this.tabs[tab].addClass( 'selected' );
		this.showContent(tab);
	},
	
	showContent: function(tab){
		this.tabsContent[this.selectedTab]['fx'].start({'height':35, 'opacity':0}).chain(function(){
			this.tabsContent[this.selectedTab].setStyle('display','none');
			this.tabsContent[tab].setStyles({'display':'block', 'height':35, 'opacity':0});
			this.tabsContent[tab]['fx'].start({'height':this.tabsContent[tab]['height'], 'opacity':1});
			/* change selected tab */
			this.selectedTab = tab;
			//Cookie.set('selectedTab', tab);
		}.bind(this));	
	}
});