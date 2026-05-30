<?php
/**
 * @package	JNavigation
 * @author	Selim Alamo aka selimoff <selimovsky@yahoo.es>
 * @license	http://www.gnu.org/copyleft/gpl.html GNU/GPL
 * Based on: Page Navigation Plugin 
*/

// no direct access
defined( '_JEXEC' ) or die( 'Restricted access' );

$mainframe->registerEvent( 'onBeforeDisplayContent', 'plgContentNavigation' );

global $mainframe;
    $header .= '<link type="text/css" href="' . JURI::base() . 'plugins/content/jnavigation/css/style.css" rel="stylesheet" />';
    $mainframe->addCustomHeadTag($header);

function plgContentNavigation( &$row, &$params, $page=0 )
{
	$view		= JRequest::getCmd('view');

	// Get Plugin info
	$plugin =& JPluginHelper::getPlugin('content', 'jnavigation');

	// Get the plugin parameters
	$pluginParams = new JParameter( $plugin->params );
	$position 	  = $pluginParams->get('position', 1);
    $alignment 	  = $pluginParams->get('alignment', 1);	
    $navStyling   = $pluginParams->get('navStyling');

	if ($params->get('show_item_navigation') && ($view == 'article'))
	{

		$html 		= '';
		$db 		= & JFactory::getDBO();
		$user		= & JFactory::getUser();
		$nullDate	= $db->getNullDate();

		$date		=& JFactory::getDate();
		$config 	= & JFactory::getConfig();
		$now 		= $date->toMySQL();

		$uid 		= $row->id;
		$option 	= 'com_content';
		$canPublish = $user->authorize('com_content', 'publish', 'content', 'all');
		
		// Determine alignment of html output
		switch ($alignment)
		{
			case '0' :
				$alignmentText = 'left';
			break;
			case '1' :
				$alignmentText = 'right';
			break;
			case '2' :
				$alignmentText = 'center';
			break;
		}
		
		// Determine Navigation Styling
		switch ($navStyling)
		{
			case '0' :
				$navStyling = 'light';
			break;
			case '1' :
				$navStyling = 'dark';
			break;
			case '2' :
				$navStyling = 'vimeo';
			break;
			case '3' :
				$navStyling = 'youtube';
			break;
			case '4' :
				$navStyling = 'panoramio';
			break;
			case '5' :
				$navStyling = 'rocket';
			break;
			case '6' :
				$navStyling = 'google';
			break;
			case '7' :
				$navStyling = 'corbis';
			break;
			case '8' :
				$navStyling = 'firefox';
			break;
			case '9' :
				$navStyling = 'puma';
			break;
		}		

		// the following is needed as different menu items types utilise a different param to control ordering
		// for Blogs the `orderby_sec` param is the order controlling param
		// for Table and List views it is the `orderby` param
		$params_list = $params->toArray();
		if (array_key_exists('orderby_sec', $params_list)) {
			$order_method = $params->get('orderby_sec', '');
		} else {
			$order_method = $params->get('orderby', '');
		}
		// additional check for invalid sort ordering
		if ( $order_method == 'front' ) {
			$order_method = '';
		}

		// Determine sort order
		switch ($order_method)
		{
			case 'date' :
				$orderby = 'a.created';
				break;

			case 'rdate' :
				$orderby = 'a.created DESC';
				break;

			case 'alpha' :
				$orderby = 'a.title';
				break;

			case 'ralpha' :
				$orderby = 'a.title DESC';
				break;

			case 'hits' :
				$orderby = 'a.hits';
				break;

			case 'rhits' :
				$orderby = 'a.hits DESC';
				break;

			case 'order' :
				$orderby = 'a.ordering';
				break;

			case 'author' :
				$orderby = 'a.created_by_alias, u.name';
				break;

			case 'rauthor' :
				$orderby = 'a.created_by_alias DESC, u.name DESC';
				break;

			case 'front' :
				$orderby = 'f.ordering';
				break;

			default :
				$orderby = 'a.ordering';
				break;
		}

		$xwhere = ' AND ( a.state = 1 OR a.state = -1 )' .
		' AND ( publish_up = '.$db->Quote($nullDate).' OR publish_up <= '.$db->Quote($now).' )' .
		' AND ( publish_down = '.$db->Quote($nullDate).' OR publish_down >= '.$db->Quote($now).' )';

		// array of articles in same category correctly ordered
		$query = 'SELECT a.id,'
		. ' CASE WHEN CHAR_LENGTH(a.alias) THEN CONCAT_WS(":", a.id, a.alias) ELSE a.id END as slug,'
		. ' CASE WHEN CHAR_LENGTH(cc.alias) THEN CONCAT_WS(":", cc.id, cc.alias) ELSE cc.id END as catslug'
		. ' FROM #__content AS a'
		. ' LEFT JOIN #__categories AS cc ON cc.id = a.catid'
		. ' WHERE a.catid = ' . (int) $row->catid
		. ' AND a.state = '. (int) $row->state
		. ($canPublish ? '' : ' AND a.access <= ' .(int) $user->get('aid', 0))
		. $xwhere
		. ' ORDER BY '. $orderby;
		$db->setQuery($query);
		$list = $db->loadObjectList('id');

		// this check needed if incorrect Itemid is given resulting in an incorrect result
		if ( !is_array($list) ) {
			$list = array();
		}

		reset($list);

		// location of current content item in array list
		$location = array_search($uid, array_keys($list));

		$rows = array_values($list);

		$row->prev = null;
		$row->next = null;

		if ($location -1 >= 0) 	{
			// the previous content item cannot be in the array position -1
			$row->prev = $rows[$location -1];
		}

		if (($location +1) < count($rows)) {
			// the next content item cannot be in an array position greater than the number of array postions
			$row->next = $rows[$location +1];
		}

		$pnSpace = "";
		if (JText::_('&lt') || JText::_('&gt')) {
			$pnSpace = " ";
		}

		if ($row->prev) {
			$row->prev = JRoute::_(ContentHelperRoute::getArticleRoute($row->prev->slug, $row->prev->catslug));
		} else {
			$row->prev = '';
		}

		if ($row->next) {
			$row->next = JRoute::_(ContentHelperRoute::getArticleRoute($row->next->slug, $row->next->catslug));
		} else {
			$row->next = '';
		}

 		// output
		if ($row->prev || $row->next) {

			$html = '';
			$html .= '<div style="clear:none;float:'.$alignmentText.';">';
		
			$html .= '
			<table align="'.$alignmentText.'" cellspacing="3" cellpadding="1">
			<tr>'
			;
			if ($row->prev) {
				$html .= '
				<td valign="top">
					<a title="'. JText::_('Prev') .'" href="'. $row->prev .'">
					    <img src="' . JURI::base() . '/plugins/content/jnavigation/img/blank.gif" class="'.$navStyling.'-prev" alt="" />
					</a>
				</td>'
				;
			} else {
				$html .= '
				<td valign="top">
					<img src="' . JURI::base() . '/plugins/content/jnavigation/img/blank.gif" class="'.$navStyling.'-prev_i" alt="" />
				</td>'
				;
			}			
			
			if ($row->prev && $row->next) {
				$html .= ''
				;
			}

			if ($row->next) {
				$html .= '
				<td valign="top">
					<a title="'. JText::_('Next') .'" href="'. $row->next .'">
					    <img src="' . JURI::base() . '/plugins/content/jnavigation/img/blank.gif" class="'.$navStyling.'-next" alt="" />
					</a>
				</td>'
				;
			} else {
				$html .= '
				<td valign="top">
					<img src="' . JURI::base() . '/plugins/content/jnavigation/img/blank.gif" class="'.$navStyling.'-next_i" alt="" />
				</td>'	
                ;				
			}
			$html .= '
			</tr>
			</table>'
			;
			$html .= '</div>';

			if ($position==1) {
			// display after content
				$row->text .= $html;
			}
			if ($position==0) {
			// display before content
				$row->text = $html . $row->text;
			}
		}
	}
	if ($position==2) {
		// Output NOT IN Content
		return $html;
	}else{
		// Output IN Content through $row->text
		return;
	}
}