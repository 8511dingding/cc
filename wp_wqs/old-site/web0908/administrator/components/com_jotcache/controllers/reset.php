<?php
/*
 * @version $Id: reset.php,v 1.4 2010/08/20 13:21:13 Vlado Exp $
 * @package JotCache
 * @copyright (C) 2010 Vladimir Kanich
 * @license http://www.gnu.org/copyleft/gpl.html GNU/GPL
 */
class ResetController extends JotcacheController {
function ResetController() {
parent::JotcacheController();
$this->registerTask('close', 'display');
$this->registerTask('apply', 'save');
$this->assignViewModel('reset');
}function display() {
parent::display();
}function refresh() {
$this->model->refresh();
parent::display();
}function cookie() {
$cookie_mark = JRequest::getVar('jotcachemark', '0', 'COOKIE', 'INT');
$pars = JRequest::get();
$line = "option=com_jotcache&view=reset";
$this->model->resetMark();
if ($cookie_mark) {
setcookie('jotcachemark', '0', '0', '/');
$this->setRedirect('index2.php?' . $line . "&filter_mark=", JText::_('JOTCACHE_RS_MSG_RESET'));
} else {
setcookie('jotcachemark', '1', '0', '/');
      $this->setRedirect('index2.php?' . $line, JText::_('JOTCACHE_RS_MSG_SET'));
}}function delete() {
$this->model->delete();
$this->setRedirect('index2.php?option=com_jotcache&view=reset', JText::_('JOTCACHE_RS_DEL'));
}function exclude() {
$this->view->exclude();
}function save() {
$post = JRequest::get('post');
$cid = JRequest::getVar('cid', array(0), 'post', 'array');
JArrayHelper::toInteger($cid, array(0));
if ($this->model->store($post,$cid)) {
$msg = JText::_('JOTCACHE_EXCLUDE_SAVE');
}    if ($this->getTask() == 'save') {
$this->setRedirect('index2.php?option=com_jotcache&view=reset&task=refresh', $msg);
} else {
$this->setRedirect('index2.php?option=com_jotcache&view=reset&task=exclude', $msg);
}}}?>