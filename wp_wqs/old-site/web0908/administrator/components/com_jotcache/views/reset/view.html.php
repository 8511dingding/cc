<?php
/*
 * @version $Id: view.html.php,v 1.4 2010/10/09 07:45:14 Vlado Exp $
 * @package JotCache
 * @copyright (C) 2010 Vladimir Kanich
 * @license http://www.gnu.org/copyleft/gpl.html GNU/GPL
 */
defined('_JEXEC') or die('Restricted access');
jimport('joomla.application.component.view');
class ResetViewReset extends JView {
var $help_site = "http://www.kanich.net/radio/site/";
function display($tpl = null) {
$data = $this->get('Data');
$lists = $this->get('Lists');
$this->assignRef('data', $data);
$this->assignRef('lists', $lists);
$url = $this->help_site . "?option=com_content&view=article&id=" . JText::_('JOTCACHE_RS_HELP') . "&tmpl=component";
$this->assignRef('url', $url);
parent::display($tpl);
}function exclude($tpl = null) {
$document =& JFactory::getDocument();
$document->addScript('components/com_jotcache/jotcache.js');
$exlist = $this->get('ExList');
$this->assignRef('data', $exlist);
$url = $this->help_site . "?option=com_content&view=article&id=" . JText::_('JOTCACHE_RS_HELP') . "&tmpl=component";
$this->assignRef('url', $url);
$this->setLayout("exclude");
parent::display();
}}