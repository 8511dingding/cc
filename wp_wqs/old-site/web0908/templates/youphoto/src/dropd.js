/*======================================================================*\
|| #################################################################### ||
|| # Copyright ©2006-2009 Youjoomla LLC. All Rights Reserved.           ||
|| # This file may not be redistributed in whole or significant part. # ||
|| # ---------------- THIS IS NOT FREE SOFTWARE ---------------- #      ||
|| # http://www.youjoomla.com | http://www.youjoomla.com/license.html # ||
|| #################################################################### ||
\*======================================================================*/
window.addEvent('domready', function(){
	
	var main = $("horiznav_d");
	var myEffects = new Fx.Styles(main, {wait: false, duration: 350, transition: Fx.Transitions.linear});

	lvls = new Array();
	var nodes = main.getChildren();	
	var lis = nodes[0].getChildren();
	var selectedWithChildren = 0;


	lis.each(function(el, i){
		var subs = el.getElements('ul');
		
		lvls[i] = ( subs=='' ? el : new Array() );
		
		if( subs!=='' ){
			subs.each(function(elm,j){
				lvls[i][j] = elm.getParent();	
				
				if( lvls[i][j].hasClass('active') ){
					selected_m = lvls[i][j];
					
					selected_m.addEvent("mouseover",function(){
						myEffects.start({
							'height': 93
						});
					});
					
					selected_m.fireEvent('mouseenter');	
					selected_m.fireEvent('mouseover');
					selectedWithChildren = 1;
				}
			});
		}		
	})
	
	lvls.each(function(e,k){
		
		if( $type(e)=='element' ){
			e.addEvent('mouseover',function(){
				myEffects.start({
					'height': 56
				})			
			});
			if( selectedWithChildren == 1 ){
				e.addEvent('mouseout', function(){
					selected_m.fireEvent('mouseenter');	
					selected_m.fireEvent('mouseover');
				})
			}
		}
		
		if( $type(e) == 'array' )
		{
			e.each(function(a,l){
				
				if( !a.hasClass('active') ){
				
					a.addEvent('mouseover',function(){
						myEffects.start({
							'height': 93 
						})			
					});			
		
					a.addEvent('mouseout',function(){
						myEffects.start({
							'height': 56
						})
						if( selectedWithChildren == 1 ){
							selected_m.fireEvent('mouseenter');	
							selected_m.fireEvent('mouseover');
						}
					});
					
				}	
			});
		}
	});	
})