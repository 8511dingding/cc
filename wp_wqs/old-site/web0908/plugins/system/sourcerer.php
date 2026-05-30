<?php
/**
 * Main Plugin File
 * Does all the magic!
 *
 * @package     Sourcerer
 * @version     2.4.3
 *
 * @author      Peter van Westen <peter@nonumber.nl>
 * @link        http://www.nonumber.nl
 * @copyright   Copyright (C) 2010 NoNumber! All Rights Reserved
 * @license     http://www.gnu.org/licenses/gpl-2.0.html GNU/GPL
 */

// Ensure this file is being included by a parent file
defined( '_JEXEC' ) or die( 'Restricted access' );

// Import library dependencies
jimport( 'joomla.plugin.plugin' );

/**
* Plugin that replaces Sourcerer code with its HTML / CSS / JavaScript / PHP equivalent
*/
class plgSystemSourcerer extends JPlugin
{
	/**
	* Constructor
	*
	* For php4 compatability we must not use the __constructor as a constructor for
	* plugins because func_get_args ( void ) returns a copy of all passed arguments
	* NOT references. This causes problems with cross-referencing necessary for the
	* observer design pattern.
	*/
	function plgSystemSourcerer( &$subject, $config )
	{
		$mainframe =& JFactory::getApplication();
		$option = JRequest::getCmd( 'option' );

		// return if current page is an administrator page
		// or a joomfishplus page
		if ( $mainframe->isAdmin() || $option == 'com_joomfishplus' ) { return; }
		
		if ( JRequest::getCmd( 'disable_sourcerer' ) ) { return; }

		parent::__construct( $subject, $config );

		//load the language file
		$this->loadLanguage();
		
		// Load plugin parameters
		$params = new JParameter( $config['params'], JPATH_PLUGINS.DS.$config['type'].DS.$config['name'].'.xml' );
		
		// Include the Helper
		require_once JPATH_SITE.DS.'plugins'.DS.'system'.DS.'sourcerer'.DS.'helper.php';
		$this->helper = new plgSystemSourcererHelper;
		
		$this->helper->init( $params );
	}

	function onPrepareContent( &$article, &$params )
	{
		$this->helper->replaceInArticles( $article, $params );
	}

	function onAfterDispatch()
	{
		$this->helper->replaceInComponents();
	}

	function onAfterRender()
	{
		$this->helper->replaceInOtherAreas();
	}
}