<?php
/**
 * Popup page
 * Displays the Sourcerer Code Helper
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

$class = new plgButtonSourcererPopup();
$class->render();

class plgButtonSourcererPopup
{
	/**
	* Constructor
	*
	* For php4 compatability we must not use the __constructor as a constructor for
	* plugins because func_get_args ( void ) returns a copy of all passed arguments
	* NOT references. This causes problems with cross-referencing necessary for the
	* observer design pattern.
	*/
	function plgButtonSourcererPopup()
	{
		// Include the syndicate functions only once
		jimport( 'joomla.plugin.plugin' );

		$plugin = JPluginHelper::getPlugin( 'editors-xtd', 'sourcerer' );
		$params = '';
		if ( is_object( $plugin ) && isset( $plugin->params ) ) {
			$params = $plugin->params;
		}
		$params = new JParameter( $params, JPATH_PLUGINS.DS.'editors-xtd'.DS.'sourcerer.xml' );
		$this->params = $this->getParamValues( $params );

		$plugin = JPluginHelper::getPlugin( 'system', 'sourcerer' );
		$params = '';
		if ( is_object( $plugin ) && isset( $plugin->params ) ) {
			$params = $plugin->params;
		}
		$params = new JParameter( $params, JPATH_PLUGINS.DS.'system'.DS.'sourcerer.xml' );
		$this->system_params = $this->getParamValues( $params );
	}

	function render()
	{
		jimport( 'joomla.filesystem.file' );

		global $mainframe;

		// Load plugin language
		$lang =& JFactory::getLanguage();
		$lang->load( 'plg_editors-xtd_sourcerer', JPATH_ADMINISTRATOR );
		$language = 'en';
		foreach ( $lang->getLocale() as $locale ) {
			if ( JFile::exists( JPATH_SITE.DS.'plugins'.DS.'editors-xtd'.DS.'sourcerer'.DS.'editarea'.DS.'langs'.DS.$locale.'.js' ) ) {
				$language = $locale;
				break;
			}
		}

		// Add scripts and styles
		$document =& JFactory::getDocument();
		$document->addScript( JURI::root( true ).'/plugins/editors-xtd/sourcerer/editarea/edit_area_full.js' );
		$document->addScript( JURI::root( true ).'/plugins/editors-xtd/sourcerer/js/sourcerer.js' );

		$script = "
			editAreaLoader.init({
				id: 'source',	// id of the textarea to transform
				start_highlight: true,	// if start with highlight
				allow_resize: 'y',
				allow_toggle: false,
				word_wrap: true,
				language: '".$language."',
				syntax: 'php',
				toolbar: 'fullscreen, |, undo, redo, |, select_font, |, syntax_selection, |, highlight, reset_highlight, word_wrap',
				syntax_selection_allow: 'css,html,js,php'
			});

			var sourcerer_syntax_word = '".$this->system_params->syntax_word."';
			var sourcerer_editorname = '".JRequest::getCmd( 'name', 'text' )."';
			var sourcerer_default_addsourcetags = '".$this->params->addsourcetags."';
			var sourcerer_root = '".JURI::root( true )."';

			window.addEvent( 'domready', function() { sourcerer_init(); });
		";
		$document->addScriptDeclaration( $script );
		$document->addStyleSheet( JURI::root( true ).'/plugins/editors-xtd/sourcerer/css/sourcerer_popup.css' );

		$this->params->code = '';
		if ( $this->params->use_example_code == 1 || ( $mainframe->isAdmin() && $this->params->use_example_code == 2 ) ) {
			$this->params->code = $this->params->example_code;
		}

		echo $this->getHTML();
	}

	function getHTML()
	{
		global $mainframe;

		JHTML::_( 'behavior.tooltip' );

		ob_start();
?>
			<form action="index.php" id="sourceForm" method="post">
				<fieldset><legend style="display:none;"></legend>
					<div style="float: left">
						<h1><?php echo JText::_( 'Sourcerer Code Helper' ); ?></h1>
					</div>
					<div style="float: right; text-align: right;">
						<div class="button2-left"><div class="blank hasicon apply">
							<a rel="" onclick="sourcerer_insertText();window.parent.document.getElementById('sbox-window').close();" href="javascript://" title="<?php echo JText::_('Insert') ?>"><?php echo JText::_('Insert') ?></a>
						</div></div>
						<div class="button2-left"><div class="blank hasicon cancel">
							<a rel="" onclick="if ( confirm( '<?php echo JText::_( 'Are you sure?' ); ?>' ) ) { window.parent.document.getElementById('sbox-window').close(); }" href="javascript://" title="<?php echo JText::_('Cancel') ?>"><?php echo JText::_('Cancel') ?></a>
						</div></div>
					</div>
				</fieldset>
				
			 	<p><?php echo JText::_( 'Textarea (description)' ); ?></p>
				<textarea id="source" class="source" name="source" cols="" rows=""><?php echo $this->params->code ?></textarea>

				<fieldset><legend style="display:none;"></legend>
					<div style="float: right; text-align: right;">
						<div class="bar-option">
							<input type="checkbox" name="keepindent" id="keepindent" class="checkbox" value="1"<?php if ( $this->params->keepindent ) { echo ' checked="checked"'; } ?> />
								<label class="hasTip" title="<?php echo JText::_( 'Preserve indentation' ).'::'.JText::_( 'Preserve indentation (description)' ); ?>">
									<?php echo JText::_('Preserve Indentation') ?>
								</label>
						</div>
						<div class="bar-option">
							<input type="checkbox" name="keepcolors" id="keepcolors" class="checkbox" value="1"<?php if ( $this->params->keepcolors ) { echo ' checked="checked"'; } ?> />
								<label class="hasTip" title="<?php echo JText::_( 'Preserve colors' ).'::'.JText::_( 'Preserve colors (description)' ); ?>">
									<?php echo JText::_('Preserve Colors') ?>
								</label>
						</div>
						<div class="button2-left"><div class="blank hasicon apply">
							<a rel="" onclick="sourcerer_insertText();window.parent.document.getElementById('sbox-window').close();" href="javascript://" title="<?php echo JText::_('Insert') ?>"><?php echo JText::_('Insert') ?></a>
						</div></div>
						<div class="button2-left"><div class="blank hasicon cancel">
							<a rel="" onclick="if ( confirm( '<?php echo JText::_( 'Are you sure?' ); ?>' ) ) { window.parent.document.getElementById('sbox-window').close(); }" href="javascript://" title="<?php echo JText::_('Cancel') ?>"><?php echo JText::_('Cancel') ?></a>
						</div></div>
					</div>
					
					<div class="button2-left"><div class="blank">
						<label class="hasTip" title="<?php echo JText::_( 'Toggle editor' ).'::'.JText::_( 'Toggle editor (description)' ); ?>">
							<a rel="" onclick="eAL.toggle( 'source' );return false;" href="javascript://;"><?php echo JText::_('Toggle editor') ?></a>
						</label>
					</div></div>
					<div class="button2-left"><div class="blank hasicon sourcetags_0" id="sourcetags_button">
						<label class="hasTip" title="<?php echo JText::_( 'Toggle {source} tags' ).'::'.JText::_( 'Toggle {source} tags (description)' ); ?>">
							<a rel="" onclick="sourcerer_toggleSourceTags();return false;" href="javascript://;"><?php echo JText::_('Toggle {source} tags') ?></a>
						</label>
					</div></div>
					<div class="button2-left"><div class="blank hasicon tagstyle_0" id="tagstyle_button">
						<label class="hasTip" title="<?php echo JText::_( 'Toggle tag style' ).'::'.JText::_( 'Toggle tag style (description)' ); ?>">
							<a rel="" onclick="sourcerer_toggleTagStyle();return false;" href="javascript://;"><?php echo JText::_('Toggle tag style') ?></a>
						</label>
					</div></div>

				</fieldset>
			</form>
<?php
			if ( $mainframe->isAdmin() ) {
				$user = JFactory::getUser();
				if ( $user->usertype == 'Super Administrator' ) {
					$db =& JFactory::getDBO();
					$query = "
						SELECT id
						FROM #__plugins
						WHERE folder = 'editors-xtd'
						AND element = 'sourcerer'
						LIMIT 1";
					$db->setQuery( $query );
					$pluginid = $db->loadResult();
					if ( $pluginid ) {
						echo '<em>'.JText::_( 'See the plugin for settings' ).' (<a href="'.JURI::base( true ).'/index.php?option=com_plugins&view=plugin&client=site&task=edit&cid[]='.$pluginid.'" target="_blank">'.JText::_( 'Editor Button' ).' - '.JText::_( 'Sourcerer' ).'</a>)</em>';
					}
				}
			}
			$html = ob_get_contents();
		ob_end_clean();
		return $html;
	}

	function getParamValues( &$params ) {
		$values = '';
		if ( isset( $params->_xml ) ) {
			foreach ( $params->_xml as $xml_group ) {
				foreach ( $xml_group->children() as $xml_child ) {
					$key = $xml_child->attributes('name');
					if ( !empty( $key ) && $key['0'] != '@' ) {
						$val = $params->get( $key );
						if ( !is_array( $val ) && !strlen( $val ) ) {
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