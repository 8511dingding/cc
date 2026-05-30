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

//remove notice msg from lay_out
ini_set('error_reporting',E_ALL ^ E_NOTICE);

// no direct access
defined('_JEXEC') or die('Restricted access');
	
	// Include the syndicate functions only once
	include( dirname(__FILE__).'/helper.php' );
	include(JModuleHelper::getLayoutPath('mod_yj_twitter'));
?>