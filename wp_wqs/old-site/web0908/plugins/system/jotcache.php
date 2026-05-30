<?php
/*
 * @version $Id: jotcache.php,v 1.12 2010/10/07 04:31:26 Vlado Exp $
 * @package JotCache
 * @copyright (C) 2010 Vladimir Kanich
 * @license http://www.gnu.org/copyleft/gpl.html GNU/GPL
 */
defined('_JEXEC') or die('Restricted access');
jimport('joomla.plugin.plugin');
class plgSystemJotCache extends JPlugin {
var $_cache = null;
var $_fname = null;
function plgSystemJotCache(& $subject, $config) {
parent::__construct($subject, $config);
$config = & JFactory::getConfig();
$options = array(
'cachebase' => JPATH_BASE . DS . 'cache',
'defaultgroup' => 'page',
'lifetime' => $this->params->get('cachetime', 15) * 60,
'browsercache' => $this->params->get('browsercache', false),
'cachecompress' => $this->params->get('cachecompress', false),
'cachemark' => $this->params->get('cachemark', false),
'caching' => false,
'language' => $config->getValue('config.language', 'en-GB')
);jimport('joomla.cache.cache');
$this->_cache = & JCache::getInstance('page', $options);
}function onAfterInitialise() {
global $mainframe, $_PROFILER, $Itemid;
$user = &JFactory::getUser();
if ($mainframe->isAdmin() || JDEBUG || $_SERVER['REQUEST_METHOD'] == 'POST') {
return;
}if (!$user->get('aid') && $_SERVER['REQUEST_METHOD'] == 'GET') {
$this->_cache->setCaching(true);
}$this->setCacheMark();
$data = $this->_cache->get();
if ($data !== false) {
$app = & JFactory::getApplication();
$app->route();
$Itemid = JRequest::getInt('Itemid');
$data = $this->rewriteData($data);
$token = JUtility::getToken();
$search = '#<input type="hidden" name="[0-9a-f]{32}" value="1" />#';
$replacement = '<input type="hidden" name="' . $token . '" value="1" />';
$data = preg_replace($search, $replacement, $data);
if ($this->_cache->_options['cachemark']) {
$cookie_mark = JRequest::getVar('jotcachemark', '0', 'COOKIE', 'INT');
if ($cookie_mark) {
$data = preg_replace('#<title>(.*)<\/title>#', '<title>@@@ \\1</title>', $data);
}}JResponse::setBody($data);
echo JResponse::toString($mainframe->getCfg('gzip'));
if (JDEBUG) {
$_PROFILER->mark('afterCache');
echo implode('', $_PROFILER->getBuffer());
}$mainframe->close();
}}function rewriteData($data) {
$document = & JFactory::getDocument();
$result = null;
preg_match_all('#<!--\sjot\s(\w*)\s[es]\s((?:\w*="[-_a-zA-Z0-9]*"\s*)*)-->#', $data, $matches);
$marks = $matches[0];
$checks = array_unique($matches[1]);
$attrs = $matches[2];
$err = array();
for ($i = 0; $i < count($marks); $i = $i + 2) {
if ($marks[$i] != "<!-- jot " . $checks[$i] . " s " . $attrs[$i] . "-->" || $marks[$i + 1] != "<!-- jot " . $checks[$i] . " e -->")
$err[] = $checks[$i];
}if (array_key_exists(0, $err))
return "Not correct JotCache tag in active template index.php file - starting with " . $err[0] ;
$end = 0;
foreach ($checks as $key => $value) {
$start = strpos($data, "<!-- jot " . $value . " s " . $attrs[$key] . "-->", $end) + strlen($value) + strlen($attrs[$key]) + 15;
$end = strpos($data, "<!-- jot " . $value . " e -->", $start);
$chunk = substr($data, $start, $end - $start);
$attribs = JUtility::parseAttributes($attrs[$key]);
$attribs['name'] = $value;
$replacement = $document->getBuffer('modules', $value, $attribs);
if ($this->_cache->_options['cachemark']) {
$cookie_mark = JRequest::getVar('jotcachemark', '0', 'COOKIE', 'INT');
if ($cookie_mark) {
$replacement = '<div style="outline: Red dashed thin;">' . $replacement . '</div>';
}}if ($this->_cache->_options['cachecompress']) {
$replacement = preg_replace('#\n\s+#', '', $replacement);
$replacement = preg_replace('/(?:(?<=\>)|(?<=\/\>))(\s+)(?=\<\/?)/', '', $replacement);
}$part1 = substr($data, 0, $start);
$part2 = substr($data, $end);
$data = $part1 . $replacement . $part2;
$end = $end - strlen($chunk) + strlen($replacement);
}return $data;
}function onAfterRender() {
global $mainframe, $Itemid;
if ($mainframe->isAdmin() || JDEBUG || $_SERVER['REQUEST_METHOD'] == 'POST') {
return;
}$user = & JFactory::getUser();
$mark = $this->setCacheMark();
if (!$user->get('aid')) {
$database = &JFactory::getDBO();
$com = JRequest::getWord('option', '');
$view = JRequest::getCmd('view', '');
$query = "SELECT `value` FROM #__jotcache_exclude WHERE `name`='$com'";
$database->setQuery($query);
$value = $database->loadResult();
$isqparam = (@strpos($value, '=') !== false) ? true : false;
if ($isqparam) {
$divs = explode(',', $value);
$value = "";
$expart = false;
foreach ($divs as $div) {
$parts = explode('=', $div);
if (count($parts) == 1) {
$value.=$parts[0] . ',';
}if (count($parts) == 2) {
$val = JRequest::getCmd($parts[0], '');
if ($val == $parts[1])
$expart = true;
}}}$exclude = ($value == '1' or @strpos($value, $view) !== false or $expart) ? true : false;
if ($exclude) {
return;
}$id = JRequest::getInt('id', 0);
$fname = $this->getFName();
$database->setQuery("SELECT count(*) FROM #__jotcache WHERE fname='$fname'");
$found = $database->loadResult();
if (!$found) {
$query = "INSERT INTO #__jotcache (fname,com,view,id,ftime,mark) VALUES('$fname','$com','$view','$id',NOW(),'$mark')";
$database->setQuery($query);
$database->query();
}if ($this->_cache->_options['cachecompress']) {
$data = JResponse::getBody();
$data = preg_replace('#\n\s+#', '', $data);
$data = preg_replace('/(?:(?<=\>)|(?<=\/\>))(\s+)(?=\<\/?)/', '', $data);
JResponse::setBody($data);
}$this->_cache->store();
}}function getFName() {
if ($this->_fname === null) {
if (!isset($this->_cache->_id)) {
$id = md5(JRequest::getURI());
$config = & JFactory::getConfig();
$hash = $config->getValue('config.secret');
$language = $config->getValue('config.language');
} else {
$id = $this->_cache->_id;
$hash = $this->_cache->_handler->_hash;
$language = $this->_cache->_handler->_language;
}$application = (isset($this->_cache->_options['application'])) ? $this->_cache->_options['application'] : null;
$this->_fname = md5($application . '-' . $id . '-' . $hash . '-' . $language);
}return $this->_fname;
}function setCacheMark() {
if ($this->_cache->_options['cachemark']) {
$cookie_mark = JRequest::getVar('jotcachemark', '0', 'COOKIE', 'INT');
if ($cookie_mark) {
$database = &JFactory::getDBO();
$mark = true;
$fname = $this->getFName();
$query = "UPDATE #__jotcache SET mark='1' WHERE fname='$fname'";
$database->setQuery($query);
$database->query();
return true;
}return false;
}}}