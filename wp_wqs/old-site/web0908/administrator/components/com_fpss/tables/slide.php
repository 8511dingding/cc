<?php

defined('_JEXEC') or die('Restricted access');

class TableSlide extends JTable
{
	var $id 			= null;
	var $catid			= null;
	var $name 			= null;
	var $path 			= null;
	var $path_type 		= null;
	var $thumb 			= null;
	var $state 			= null;
	var $publish_up 	= null;
	var $publish_down 	= null;
	var $itemlink 		= null;
	var $menulink 		= null;
	var $target 		= null;
	var $customlink 	= null;
	var $nolink 		= null;
	var $ctext 			= null;
	var $plaintext 		= null;
	var $registers 		= null;
	var $showtitle 		= null;
	var $showseccat 	= null;
	var $showcustomtext = null;
	var $showplaintext 	= null;
	var $showreadmore 	= null;
	var $ordering 		= null;
	
	function __construct(&$db)
	{
		parent::__construct( _FPSS_TABLE_SLIDES, 'id', $db );
	}
}
?>