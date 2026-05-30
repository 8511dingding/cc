<?php

defined('_JEXEC') or die('Restricted access');

class TableCategory extends JTable
{
	var $id 				= null;
	var $name 				= null;
	var $width 				= null;
	var $quality 			= null;
	var $width_thumb 		= null;
	var $quality_thumb 		= null;
	var $published 			= null;
	
	function __construct(&$db)
	{
		parent::__construct( _FPSS_TABLE_CATEGORIES, 'id', $db );
	}
}
?>