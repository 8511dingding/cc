<?php
/*
 * @version $Id: reset.php,v 1.12 2010/10/09 11:26:26 Vlado Exp $
 * @package JotCache
 * @copyright (C) 2010 Vladimir Kanich
 * @license http://www.gnu.org/copyleft/gpl.html GNU/GPL
 */
defined('_JEXEC') or die('Restricted access');
jimport('joomla.application.component.model');
class ResetModelReset extends JModel {
var $_data = null;
var $_total = null;
var $_pagination = null;
var $_item = null;
var $filter_actid = null;
var $filter_com = null;
var $filter_view = null;
var $filter_mark = null;
var $exclude = array();
function ResetModelReset() {
parent::__construct();
}function getExclude() {
$this->_db->setQuery("SELECT id,name,value FROM #__jotcache_exclude");
$rows = $this->_db->loadObjectList();
if (!empty($rows)) {
foreach ($rows as $row) {
$this->exclude[$row->name] = $row->value;
}}return $this->exclude;
}function getExcludePost($post) {
$name_list = "";
$cnt = 0;
foreach ($post as $key => $value) {
if (substr($key, 0, 3) == "ex_") {
if ($cnt > 0)
$name_list.=",";
$name_list.="'" . substr($key, 3) . "'";
$cnt++;
}}$this->_db->setQuery("SELECT id,name,value FROM #__jotcache_exclude WHERE name IN (" . $name_list . ")");
$rows = $this->_db->loadObjectList();
if (!empty($rows)) {
foreach ($rows as $row) {
$this->exclude[$row->name] = $row->value;
}}return $this->exclude;
}function getData() {
global $mainframe;
$data = new stdclass;
$option = "com_jotcache";
$task = JRequest::getCmd('task');
$where = array();
$limit = $mainframe->getUserStateFromRequest('global.list.limit', 'limit', $mainframe->getCfg('list_limit'), 'int');
$limitstart = $mainframe->getUserStateFromRequest($option . 'limitstart', 'limitstart', 0, 'int');
    $this->filter_com = $mainframe->getUserStateFromRequest($option . '.filter_com', 'filter_com', '', 'cmd');
$this->filter_view = $mainframe->getUserStateFromRequest($option . '.filter_view', 'filter_view', '', 'cmd');
$this->filter_mark = $mainframe->getUserStateFromRequest($option . '.filter_mark', 'filter_mark', '', 'cmd');
                        if ($this->filter_com) {
$where[] = "m.com='$this->filter_com'";
}if ($this->filter_view) {
$where[] = "m.view='$this->filter_view'";
}if ($this->filter_mark) {
$where[] = "m.mark='$this->filter_mark'";
}$this->removeExpired();
$query = "SELECT COUNT(*) FROM #__jotcache AS m "
. (count($where) ? "\n WHERE " . implode(' AND ', $where) : '');
$this->_db->setQuery($query);
$total = $this->_db->loadResult();
jimport('joomla.html.pagination');
$data->pageNav = new JPagination($total, $limitstart, $limit);
$query = "SELECT m.* "
. "\n FROM #__jotcache AS m"
. (count($where) ? "\n WHERE " . implode(' AND ', $where) : '')
. "\n ORDER BY m.com ASC, m.view ASC, m.id ASC";
$this->_db->setQuery($query, $data->pageNav->limitstart, $data->pageNav->limit);
$data->rows = $this->_db->loadObjectList();
if ($data->rows === null)
JError::raiseNotice(100, $this->_db->getErrorMsg());
    return $data;
}function getLists() {
global $mainframe, $option;
$where = array();
$query = 'SELECT com as value, com as text FROM #__jotcache AS c'
. ' GROUP BY com ORDER BY com';
$com[] = JHTML::_('select.option', '', '- ' . JText::_('JOTCACHE_RS_SEL_COMP') . ' -', 'value', 'text');
$this->_db->setQuery($query);
$com = array_merge($com, $this->_db->loadObjectList());
$lists['com'] = JHTML::_('select.genericlist', $com, 'filter_com', 'class="inputbox" size="1" onchange="resetSelect();"', 'value', 'text', $this->filter_com);
if ($this->filter_com) {
$where[] = "c.com='$this->filter_com'";
}$where[] = "c.view<>''";
$query = "SELECT view as value, view as text FROM #__jotcache AS c"
. (count($where) ? "\n WHERE " . implode(' AND ', $where) : '')
. " GROUP BY view ORDER BY view";
$view[] = JHTML::_('select.option', '', '- ' . JText::_('JOTCACHE_RS_SEL_VIEW') . ' -', 'value', 'text');
$this->_db->setQuery($query);
$view = array_merge($view, $this->_db->loadObjectList());
$lists['view'] = JHTML::_('select.genericlist', $view, 'filter_view', 'class="inputbox" size="1" onchange="document.adminForm.submit( );"', 'value', 'text', $this->filter_view);
$mark[] = JHTML::_('select.option', '', '- ' . JText::_('JOTCACHE_RS_SEL_MARK') . ' -', 'value', 'text');
$mark[] = JHTML::_('select.option', '1', JText::_('JOTCACHE_RS_SEL_MARK_YES'), 'value', 'text');
$lists['mark'] = JHTML::_('select.genericlist', $mark, 'filter_mark', 'class="inputbox" size="1" onchange="document.adminForm.submit( );"', 'value', 'text', $this->filter_mark);
return $lists;
}function removeExpired() {
$root = JPATH_SITE . DS . 'cache' . DS . 'page';
$query = "SELECT *  FROM #__jotcache";
$this->_db->setQuery($query);
$rows = $this->_db->loadObjectList();
$expired = array();
foreach ($rows as $row) {
$filename = $root . DS . $row->fname . '.php_expire';
if (file_exists($filename)) {
$exp = file_get_contents($filename);
if (time() - $exp > 0)
$expired[] = $row->fname;
}if (count($expired) > 0) {
$explist = implode("','", $expired);
$query = "DELETE FROM #__jotcache WHERE fname IN ('" . $explist . "')";
$this->_db->setQuery($query);
if (!$this->_db->query()) {
JError::raiseNotice(100, $this->_db->getErrorMsg());
}}}}function refresh() {
JRequest::setVar('filter_com', '');
JRequest::setVar('filter_view', '');
JRequest::setVar('filter_mark', '');
$root = JPATH_SITE . DS . 'cache' . DS . 'page';
if (!file_exists($root)) {
$query = "DELETE FROM #__jotcache";
$this->_db->setQuery($query);
if (!$this->_db->query())
JError::raiseNotice(100, $this->_db->getErrorMsg());
return;
}$sql = 'SELECT fname FROM #__jotcache';
$this->_db->setQuery($sql);
$rows = $this->_db->loadObjectList();
$deleted = array();
$existed = array();
foreach ($rows as $row) {
if (file_exists($root . DS . $row->fname . '.php')) {          $existed[$row->fname] = 1;
} else {          $deleted[] = $row->fname;
}}if (count($deleted) > 0) {
$list = implode("','", $deleted);
$query = "DELETE FROM #__jotcache WHERE `fname` IN ('$list');";
$this->_db->setQuery($query);
if (!$this->_db->query())
JError::raiseNotice(100, $this->_db->getErrorMsg());
}    if ($handle = opendir($root)) {
while (false !== ($file = readdir($handle))) {
if ($file != "." && $file != "..") {
$ext = strrchr($file, ".");
$fname = substr($file, 0, -strlen($ext));
if (!array_key_exists($fname, $existed) && ($ext == ".php" || $ext == ".php_expire")) {
unlink($root . DS . $file);
}}}closedir($handle);
}}function resetMark() {
$query = "UPDATE #__jotcache SET mark=NULL;";
$this->_db->setQuery($query);
if (!$this->_db->query())
JError::raiseNotice(100, $this->_db->getErrorMsg());
}function delete() {
global $mainframe;
$root = JPATH_SITE . DS . 'cache' . DS . 'page';
$cid = JRequest::getVar('cid', array(0), '', 'array');
$list = implode("','", $cid);
$query = "DELETE FROM #__jotcache where `fname` IN ('$list');";
$this->_db->setQuery($query);
if (!$this->_db->query())
JError::raiseNotice(100, $this->_db->getErrorMsg());
foreach ($cid as $fname) {
if (file_exists($root . DS . $fname . '.php')) {          unlink($root . DS . $fname . '.php');
unlink($root . DS . $fname . '.php_expire');
}}}function getExList() {
global $mainframe;
$data = new stdclass;
$option = "com_jotcache";
$task = JRequest::getCmd('task');
$where = array();
$limit = $mainframe->getUserStateFromRequest($option . '.list.limit', 'limit', $mainframe->getCfg('list_limit'), 'int');
$limitstart = $mainframe->getUserStateFromRequest($option . 'limitstart', 'limitstart', 0, 'int');
$data->exclude = $this->getExclude();
$where[] = "`parent`=0 AND `option`<>''";
$query = "SELECT COUNT(*) FROM #__components "
. (count($where) ? "\n WHERE " . implode(' AND ', $where) : '');
$this->_db->setQuery($query);
$total = $this->_db->loadResult();
jimport('joomla.html.pagination');
$data->pageNav = new JPagination($total, $limitstart, $limit);
$query = "SELECT `id`,`name`,`option` "
. "\n FROM #__components"
. (count($where) ? "\n WHERE " . implode(' AND ', $where) : '')
. "\n ORDER BY name ASC";
$this->_db->setQuery($query, $data->pageNav->limitstart, $data->pageNav->limit);
$data->rows = $this->_db->loadObjectList();
if ($data->rows === null)
JError::raiseNotice(100, $this->_db->getErrorMsg());
    return $data;
}function store($post, $cid) {
if (count($cid) > 0) {
$idlist = implode(',', $cid);
$query = "SELECT `option` FROM #__components WHERE id IN (" . $idlist . ")";
$this->_db->setQuery($query);
$rows = $this->_db->loadObjectList();
$exclude_jc = array();
foreach ($rows as $row) {
$views = 'ex_' . $row->option;
$value = array_key_exists($views, $post) ? $post[$views] : '';
if ($value == '')
$value = '1';
$exclude_jc[$row->option] = $value;
}$exclude_db = $this->getExcludePost($post);        $upd = $exclude_jc;
$del = array_diff_key($exclude_db, $exclude_jc);
$ins = array_diff_key($exclude_jc, $exclude_db);
if (count($del) > 0) {
$del_list = implode("','", array_keys($del));
$query = "DELETE FROM #__jotcache_exclude WHERE name IN ('" . $del_list . "')";
$this->_db->setQuery($query);
if (!$this->_db->query()) {
JError::raiseNotice(100, $this->_db->getErrorMsg());
return false;
}}foreach ($ins as $option => $views) {
$query = "INSERT INTO #__jotcache_exclude(`name`,`value`) VALUES('$option','$views')";
$this->_db->setQuery($query);
if (!$this->_db->query()) {
JError::raiseNotice(100, $this->_db->getErrorMsg());
return false;
}}foreach ($upd as $option => $views) {
$upd_list = implode("','", array_keys($upd));
$root = JPATH_SITE . DS . 'cache' . DS . 'page';
$query = "SELECT `fname` FROM #__jotcache WHERE `com` IN ('" . $upd_list . "')";
$this->_db->setQuery($query);
$names = $this->_db->loadObjectList();
foreach ($names as $name) {
if (file_exists($root . DS . $name->fname . '.php')) {              unlink($root . DS . $name->fname . '.php');
unlink($root . DS . $name->fname . '.php_expire');
}}$query = "UPDATE #__jotcache_exclude SET `value`='$views' WHERE `name`='$option'";
$this->_db->setQuery($query);
if (!$this->_db->query()) {
JError::raiseNotice(100, $this->_db->getErrorMsg());
return false;
}}}return true;
}}