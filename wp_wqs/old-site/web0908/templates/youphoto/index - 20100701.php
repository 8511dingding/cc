<?php

defined( '_JEXEC' ) or die( 'Restricted index access' );

define( 'TEMPLATEPATH', dirname(__FILE__) );
require( TEMPLATEPATH.DS."settings.php");



?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="<?php echo $this->language; ?>" lang="<?php echo $this->language; ?>" >
<head>
<jdoc:include type="head" />
<?php JHTML::_('behavior.mootools'); ?>

<link href="<?php echo $yj_site ?>/css/template.<?php echo $cssextens; ?>" rel="stylesheet" type="text/css" />
<link href="<?php echo $yj_site ?>/css/<?php echo $css_file; ?>.<?php echo $cssextens; ?>" rel="stylesheet" type="text/css" />

<link rel="shortcut icon" href="<?php echo $yj_site ?>/favicon.ico" />
<?php require( TEMPLATEPATH.DS."head.php");?>

<link rel="stylesheet" type="text/css" href="plugins/shadowbox/shadowbox.css">
<script type="text/javascript" src="plugins/shadowbox/shadowbox.js"></script>
<script type="text/javascript">
Shadowbox.init();
</script>

<!--jswide-->
<link rel="stylesheet" type="text/css" href="templates/youphoto/jswide/jswide.css">
<script src="templates/youphoto/jswide/jswide.js" type="text/javascript"></script>
<script src="templates/youphoto/jswide/prototype.js" type="text/javascript"></script>
<script src="templates/youphoto/jswide/drag.js" type="text/javascript"></script>

</head>

<body id="color">



<div id="centertop" style="font-size:<?php echo $css_font; ?>; width:<?php echo $css_width; ?>;">

<!-- notices -->
<?php if ($ie6notice == 1){ ?>
<!--[if lte IE 6]>
<p class="clip" style="text-align:center" >Hello visitor.You are using IE6 , an outdated version of Internet Explorer. Please consider upgrading. Click <a href="http://www.webstandards.org/action/previous-campaigns/buc/" target="_blank" >here</a> for more info .</p>
<![endif]-->
<?php } ?>
<?php if($nonscript == 1 ){?>
        <noscript><p class="error" style="text-align:center" >The site (Wangqingsong.com) is equiped with JavaScript. Your browser does not support JavaScript! Please enable it for maximum experience. Thank you.</p></noscript>
        <?php } ?>
<!--end  notices -->


<!--header-->
<div id="header">
<div id="logo" class="png">

<div id="tags"><h1>
<a href="index.php" title="<?php echo $tags?>"><?php echo $seo ?></a>
</h1></div><!-- end tags -->

</div><!-- end logo -->

<?php if ($this->countModules('banner')) {?>
<div id="banner">
<jdoc:include type="modules" name="banner" style="raw" />
</div><!-- end banner -->
<?php } ?>

</div><!-- end header -->


<!--top menu-->
<div id="<?php echo $topmenuclass ?>" style="font-size:<?php echo $css_font; ?>;">
  <div id="<?php echo $menuclass ?>">
	<?php echo $topmenu; ?>
</div>
</div><!-- end top menu -->



</div><!-- end centartop-->


<!-- BOTTOM PART OF THE SITE LAYOUT -->
<div id="centerbottom" style="font-size:<?php echo $css_font; ?>; width:<?php echo $css_width; ?>;">


<?php if ($this->countModules('advert1')) {?>
<!-- avdert 1 -->
<div id="advert1">
<jdoc:include type="modules" name="advert1" style="yjsquare" />
</div>
<!-- end -->
<?php } ?>

<?php if ($this->countModules('user1') || $this->countModules('user2') || $this->countModules('user3') || $this->countModules('user4')) {?>
	<div id="tops">
    <?php if ($this->countModules('user1')) {?>
    	<div id="user1" style="width:<?php echo $topswidth ?>;"><div class="tops_ins"><jdoc:include type="modules" name="user1" style="yjsquare" /></div></div>
    <?php } ?>
        <?php if ($this->countModules('user2')) {?>
    	<div id="user2" style="width:<?php echo $topswidth ?>;"><div class="tops_ins"><jdoc:include type="modules" name="user2" style="yjsquare" /></div></div>
    <?php } ?>
        <?php if ($this->countModules('user3')) {?>
    	<div id="user3" style="width:<?php echo $topswidth ?>;"><div class="tops_ins"><jdoc:include type="modules" name="user3" style="yjsquare" /></div></div>
    <?php } ?>
        <?php if ($this->countModules('user4')) {?>
    	<div id="user4" style="width:<?php echo $topswidth ?>;"><div class="tops_ins"><jdoc:include type="modules" name="user4" style="yjsquare" /></div></div>
    <?php } ?>
    </div>
   <?php } ?>

<!-- pathway -->

<?php if ($this->countModules('breadcrumb')) { ?> 
<div id="pathway">
You are here:&nbsp;&nbsp;<jdoc:include type="modules" name="breadcrumb" /></div>
<?php } ?>

<!-- end pathway -->



<!--MAIN LAYOUT HOLDER -->
<div id="holder">

<!-- messages -->
<jdoc:include type="message" />
<!-- end messages -->





<?php if ($this->countModules('left')) { ?>
<!-- left block -->
<!-- <div id="leftblock" style="width:<?php echo $leftblock ?>;"> -->
<div id="leftblock" style="width:135px;">
<div class="inside">
<jdoc:include type="modules" name="left" style="yjsquare" />
</div>
</div>
<!-- end left block -->
<?php } ?>




<!-- MID BLOCK WITH TOP AND BOTTOM MODULE POSITION -->
<!-- <div id="midblock" style="width:<?php echo $midblock ?>;"> -->
<div id="midblock" style="width:805px; overflow:auto;">
<div class="insidem">

<?php if ($this->countModules('top')) { ?>
<!-- top module-->
<div id="topmodule">
<jdoc:include type="modules" name="top" style="yjsquare" /> 
</div>
<!-- end top module-->
<?php } ?>

<!-- component -->
<jdoc:include type="component"  />
<!-- end component -->


<?php if ($this->countModules('bottom')) { ?>
<!-- bottom module position -->
<div id="bottommodule">
<jdoc:include type="modules" name="bottom" style="yjsquare" />
</div>
<!-- end module position -->
<?php } ?>



</div><!-- end mid block insidem class -->
<!-- 宽幅照片展示滑动的java代码 -->
<script>
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
</script>

</div><!-- end mid block div -->
<!-- END MID BLOCK -->






<?php if ($this->countModules('right')) { ?>
<!-- right block -->
<div id="rightblock" style="width:<?php echo $rightblock ?>;">
<div class="inside">
<jdoc:include type="modules" name="right" style="yjsquare" />
</div>
</div>
<!-- end right block -->
<?php } ?>



</div><!-- end holder div -->



<?php if ($this->countModules('user5') || $this->countModules('user6') || $this->countModules('user7') || $this->countModules('user8')) {?>
	<div id="bottoms">
    <?php if ($this->countModules('user5')) {?>
    	<div id="user5" style="width:<?php echo $bottomswidth ?>;"><div class="tops_ins"><jdoc:include type="modules" name="user5" style="yjsquare" /></div></div>
    <?php } ?>
        <?php if ($this->countModules('user6')) {?>
    	<div id="user6" style="width:<?php echo $bottomswidth ?>;"><div class="tops_ins"><jdoc:include type="modules" name="user6" style="yjsquare" /></div></div>
    <?php } ?>
        <?php if ($this->countModules('user7')) {?>
    	<div id="user7" style="width:<?php echo $bottomswidth ?>;"><div class="tops_ins"><jdoc:include type="modules" name="user7" style="yjsquare" /></div></div>
    <?php } ?>
        <?php if ($this->countModules('user8')) {?>
    	<div id="user8" style="width:<?php echo $bottomswidth ?>;"><div class="tops_ins"><jdoc:include type="modules" name="user8" style="yjsquare" /></div></div>
    <?php } ?>
    </div>
   <?php } ?>

</div><!-- end centerbottom-->
<!-- END BOTTOM PART OF THE SITE LAYOUT -->
<!-- footer -->

<div id="footer"  style="font-size:<?php echo $css_font; ?>; width:<?php echo $css_width; ?>;">
<div id="youjoomla">

<?php if ($this->countModules('footer')) { ?>
<div id="footmod">
<jdoc:include type="modules" name="footer" style="yjsquare" />
</div><?php } ?>

<div id="cp">
<?php echo getYJLINKS()  ?>
</div>

<!--<p class="copyright">&nbsp;&copy; 2010 <a href="http://www." title="#"><span>#</span></a>
 | Site by <a href="http://www.jianing.name" title="Email:mail@jianing.name" target="_blank"><span>jianing</span></a>
		| <a href="mailto:mail@jianing.name" title="mail to jianing">mail</a></p>-->

</div>
</div>

<!-- end footer -->

</body>
</html>