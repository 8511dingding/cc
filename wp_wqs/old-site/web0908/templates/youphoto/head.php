<?php 
/*======================================================================*\
|| #################################################################### ||
|| # Youjoomla LLC - YJ- Licence Number 2511TV810
|| # Licensed to - Vlad Serov
|| # ---------------------------------------------------------------- # ||
|| # Copyright (C) 2006-2009 Youjoomla LLC. All Rights Reserved.        ||
|| # This file may not be redistributed in whole or significant part. # ||
|| # ---------------- THIS IS NOT FREE SOFTWARE ---------------- #      ||
|| # http://www.youjoomla.com | http://www.youjoomla.com/license.html # ||
|| #################################################################### ||
\*======================================================================*/
defined( '_JEXEC' ) or die( 'Restricted index access' ); ?>
<script type="text/javascript">
window.addEvent('domready', function() {
new SmoothScroll({duration: 1000});	
});
</script>

<!--[if IE 6]>
<link href="<?php echo $yj_site ?>/css/ifie.php" rel="stylesheet" type="text/css" />
<style type="text/css">
#horiznav_d ul li ul{
width:<?php echo $css_width; ?>;
}
#tabs_holder, 
#tabs_holder2, 
#tabs_holder3{background: url(<?php echo $yj_site ?>/images/<?php echo $css_file; ?>/h3.jpg) repeat-x left 30px;}
</style>
<![endif]-->

<?php if ( $menustyle == 1 || $menustyle == 2 || $menustyle == 5) {?>
<!--[if lte IE 8]>
		<script type="text/javascript">
		sfHover = function() {
			var sfEls = document.getElementById("horiznav").getElementsByTagName("LI");
			for (var i=0; i<sfEls.length; i++) {
				sfEls[i].onmouseover=function() {
					this.className+=" sfHover";
				}
				sfEls[i].onmouseout=function() {
					this.className=this.className.replace(new RegExp(" sfHover\\b"), "");
				}
			}
		}
		if (window.attachEvent) window.attachEvent("onload", sfHover);
		</script>
<![endif]-->
<?php }?>
 <?php if ( $menustyle == 3 || $menustyle == 4) {?>

<!--[if lte IE 8]>
		<script type="text/javascript">
		sfHover = function() {
			var sfEls = document.getElementById("horiznav_d").getElementsByTagName("LI");
			for (var i=0; i<sfEls.length; i++) {
				sfEls[i].onmouseover=function() {
					this.className+=" sfHover";
				}
				sfEls[i].onmouseout=function() {
					this.className=this.className.replace(new RegExp(" sfHover\\b"), "");
				}
			}
		}
		if (window.attachEvent) window.attachEvent("onload", sfHover);
		</script>
<![endif]-->
<?php }?>
<?php if ( $menustyle == 2 ) {
echo '<script type="text/javascript" src="'.$yj_site.'/src/mouseover.js"></script>';
}?>
<?php if ( $menustyle == 4) {
echo '<script type="text/javascript" src="'.$yj_site.'/src/mouseover_d.js"></script>';
}?>
<?php if ( $menustyle == 3 || $menustyle == 4) {
echo '<script type="text/javascript" src="'.$yj_site.'/src/dropd.js"></script>';
}?>