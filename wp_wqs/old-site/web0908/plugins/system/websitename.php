<?php
defined( '_JEXEC' ) or die( 'Restricted access' );
/**
 * Plugin Website Name
 *
 * @autor : Nicolas Ogier
 * thanks to :
 *  JM Simonet (infograph768) for the English translation
 *  Joaoh Bruni for the Brazilian Portuguese translation
 *
 * last update : 15 november 2007
 *
 **/
class plgSystemWebsitename extends JPlugin
{
/**
	 * Constructor
	 *
	 * For php4 compatability we must not use the __constructor as a constructor for plugins
	 * because func_get_args ( void ) returns a copy of all passed arguments NOT references.
	 * This causes problems with cross-referencing necessary for the observer design pattern.
	 *
	 * @access	protected
	 * @param	object $subject The object to observe
	 * @param 	array  $config  An array that holds the plugin configuration
	 * @since	1.0
	 */
	function plgSystemWebsitename(& $subject, $config)
	{
	
		parent::__construct($subject,$config);
	}

	function onAfterDisplayContent()
	{
		global $mainframe;
		$plugin=&JPluginHelper::getPlugin('system','websitename');
		$botParams = new JParameter($plugin->params);
		$botParams->def( 'separator', '-' );
		$botParams->def( 'position', 0 );
    $titre = $mainframe->getCfg( 'sitename' );
    $document =& JFactory::getDocument();
    $title = $document->getTitle();
    $pos = strpos($title, $titre);
    // Notez l'utilisation de ===.  Un simple == ne donnerait pas le résultat escompté
    // car la chaine peut etre à la position 0 (la première).
    if ($pos === false) {
       if($botParams->get('position')==1) { $title = $title.' '.$botParams->get('separator').' '.$titre;} else { $title=  $titre.' '.$botParams->get('separator').' '.$title;}
      $document->setTitle( $title );
    } 
	}

}
?>
