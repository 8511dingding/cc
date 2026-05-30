<?php
/*
* @version $Id: toolbar.php,v 1.1 2010/05/26 06:39:43 Vlado Exp $
* @package JotCache
* @copyright (C) 2010 Vladimir Kanich
* @license http://www.gnu.org/copyleft/gpl.html GNU/GPL
*/
defined('_JEXEC') or die('Restricted access');
class JotcacheToolbar extends JToolBarHelper {
function title($title) {
global $mainframe;
$site = $mainframe->getSiteURL();
$html  = '<img border="0" width="100" height="54" src="'.$site
.'administrator/components/com_jotcache/images/jotcache-logo-2.gif" alt="JotCache Logo" align="left">';
$html .= '<div class="header">&nbsp;'.$title;
$html .= "</div>\n";
$mainframe->set('JComponentTitle', $html);
}}?>
