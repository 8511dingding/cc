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

// No direct access
defined( '_JEXEC' ) or die( 'Restricted access' );

// Import library dependencies
jimport( 'joomla.event.plugin' );

// Include the syndicate functions only once
if ( is_file( JPATH_SITE.DS.'plugins'.DS.'system'.DS.'sourcerer.php' ) ) {
	require_once JPATH_SITE.DS.'plugins'.DS.'system'.DS.'sourcerer.php';
}

/**
* Button Plugin that places a Sourcerer code block into the text
*/
class plgButtonSourcerer extends JPlugin
{
	/**
	* Constructor
	*
	* For php4 compatability we must not use the __constructor as a constructor for
	* plugins because func_get_args ( void ) returns a copy of all passed arguments
	* NOT references. This causes problems with cross-referencing necessary for the
	* observer design pattern.
	*/
	function plgButtonSourcerer( &$subject, $config )
	{
		if ( !is_file( JPATH_SITE.DS.'plugins'.DS.'system'.DS.'sourcerer.php' ) ) {
			return;
		}

		parent::__construct( $subject, $config );

		// Load plugin parameters
		$params = new JParameter( $config['params'], JPATH_PLUGINS.DS.$config['type'].DS.$config['name'].'.xml' );
		$this->params = $this->getParamValues( $params );

		// Load plugin language
		$this->loadLanguage();
	}

	/**
	* Display the button
	*
	* @return array A two element array of ( imageName, textToInsert )
	*/
	function onDisplay( $name )
	{
		$mainframe =& JFactory::getApplication();

		$button = new JObject();

		if ( !$mainframe->isAdmin() ) {
			$enable_frontend = $this->params->enable_frontend;
			if ( !$enable_frontend ) {
				return $button;
			}
		}
		
		JHTML::_( 'behavior.modal' );

		$document =& JFactory::getDocument();

		$button_style = 'blank';
		if ( $this->params->button_icon ) {
			$button_style = 'sourcerer';
		}
		$document->addStyleSheet( JURI::root( true ).'/plugins/editors-xtd/sourcerer/css/sourcerer.css' );

		$link = 'index.php?nn_qp=1'
			.'&folder=plugins.editors-xtd.sourcerer'
			.'&file=sourcerer.inc.php'
			.'&name='.$name;

		$button->set( 'modal', true );
		$button->set( 'link', $link );
		$button->set( 'text', JText::_( $this->params->button_text ) );
		$button->set( 'name', $button_style );
		$button->set( 'options', "{handler: 'iframe', size: {x:window.getSize().scrollSize.x-100, y: window.getSize().size.y-100}}" );

		return $button;
	}

	function getParamValues( &$params ) {
		$values = '';
		if ( isset( $params->_xml ) ) {
			foreach ( $params->_xml as $xml_group ) {
				foreach ( $xml_group->children() as $xml_child ) {
					$key = $xml_child->attributes('name');
					if ( !empty( $key ) && $key['0'] != '@' ) {
						$val = $params->get( $key );
						if ( !strlen( $val ) ) {
							$val = $xml_child->attributes('default');
							if ( $xml_child->attributes('type') == 'textarea' ) {
								$val = str_replace( '<br />', "\n", $val );
							}
						}
						$values->$key = $val;
					}
				}
			}
		}

		return $values;
	}
}