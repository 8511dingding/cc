<?php

// no direct access
defined('_JEXEC') or die('Restricted access');

class HTML_FPSlideShow {

	function showHeaderIM($option, $task) {
		global $mainframe, $option, $Itemid;

		$jw_fpss_head = '
<!-- JoomlaWorks "Frontpage Slideshow" v2.0.0 starts here -->
<link href="administrator/components/'.$option.'/style/fpss.css" rel="stylesheet" type="text/css" />
<!-- JoomlaWorks "Frontpage Slideshow" v2.0.0 ends here -->
			';
		$mainframe->addCustomHeadTag($jw_fpss_head);

		echo '
<!-- JoomlaWorks "Frontpage Slideshow" v2.0.0 starts here -->
<div id="jwfpss" class="jwfpss-fp">
<h2 id="jwfpss-logo"></h2>
		';
	}

	function showFooter() {
		echo '
	<div id="jwfpss-footer">'._FPSS_COPYRIGHTS.'</div>
</div>
<!-- JoomlaWorks "Frontpage Slideshow" v2.0.0 ends here -->
	';
	}
	// END CLASS
}

?>