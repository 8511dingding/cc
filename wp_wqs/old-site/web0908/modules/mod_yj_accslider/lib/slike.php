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

	// no direct access
	defined('_JEXEC') or die('Restricted access');
	/**
	 * Image detection inside article. Searches in intro text and if not found, in full article text
	 *
	 * @param object $row
	 * @return string - image path
	 */
	function articleaccs_image ($row)
	{
		$img = searchaccs_image( $row->introtext );
		if( $img ) return $img;
				
		$img = searchaccs_image( $row->fulltext );
		return $img;		
	}
	/**
	 * Searches for all images inside a text and returns the first one found
	 *
	 * @param string $text
	 * @return string
	 */
	function searchaccs_image( $text )
	{		
		preg_match_all("#\<img(.*)src\=\"(.*)\"#Ui", $text, $mathes);		
		return isset($mathes[2][0]) ? $mathes[2][0] : '';			
	}	
?>