<?php
/*
* @version $Id: install.jotcache.php,v 1.2 2010/08/18 05:39:32 Vlado Exp $
* @package JotCache
* @copyright (C) 2010 Vladimir Kanich
* @license http://www.gnu.org/copyleft/gpl.html GNU/GPL
*/
define('_JotCacheVersion', '1.2.0');
function migrate($table, $column, $type) {
$database = &JFactory::getDBO();
$sql = "DESCRIBE `#__jotcache" . $table . "` `" . $column . "`";
$database->setQuery($sql);
if (!$database->loadResult()) {
$sql = "ALTER TABLE `#__jotcache" . $table . "` ADD `" . $column . "` " . $type . ";";
$database->setQuery($sql);
if (!$database->query()) JError::raiseNotice(100, $database->getErrorMsg());
}}function com_install() {
$items = array(",mark,TINYINT(1)"
);foreach ($items as $item) {
$table = "";
$column = "";
$type = "";
list($table, $column, $type) = split(",", $item, 3);
migrate($table, $column, $type);
}if(count(JError::getErrors())>0) {
echo "<p>Installation of the component was not successful!</p>";
return false;
} else {
echo "<p>Installation of JotCache ver." ._JotCacheVersion. " successful!</p><p> More information you can find in JotCache Help (Components-&gt;JotCache).</p><p>Home site : <a href=\"http://www.kanich.net/radio/site\" target=\"_blank\">http://www.kanich.net/radio/site</a>.<br><br>When necessary contact me using <a href=\"http://www.kanich.net/radio/site/contact\" target=\"_blank\">http://www.kanich.net/radio/site/contact</a> with any questions.</p>";
return true;
}}?>