<?php
/*
* @version $Id: uninstall.jotcache.php,v 1.2 2010/07/05 12:40:13 Vlado Exp $
* @package JotCache
* @copyright (C) 2010 Vladimir Kanich
* @license http://www.gnu.org/copyleft/gpl.html GNU/GPL
*/
function com_uninstall() {
$database = &JFactory::getDBO();
$query = "DELETE FROM #__components where `option`='com_jotcache'";
$database->setQuery($query);
if (!$database->query()) JError::raiseNotice(100, $database->getErrorMsg());
$query = "DROP TABLE #__jotcache";
$database->setQuery($query);
if (!$database->query()) JError::raiseNotice(100, $database->getErrorMsg());
if(count(JError::getErrors())>0) {
echo "Error condition - Uninstallation not successfull! You have to manually remove com_jotcache from '.._components' table as well as to drop '.._jotcache' tabel";
} else {
echo "Uninstallation successfull!";
}}?>