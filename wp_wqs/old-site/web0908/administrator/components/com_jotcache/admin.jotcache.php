<?php
/*
* @version $Id: admin.jotcache.php,v 1.1 2010/05/26 06:39:43 Vlado Exp $
* @package JotCache
* @copyright (C) 2010 Vladimir Kanich
* @license http://www.gnu.org/copyleft/gpl.html GNU/GPL
*/
defined('_JEXEC') or die('Restricted access');
require_once(JPATH_COMPONENT_ADMINISTRATOR.DS.'controller.php');
$task = JRequest::getCmd('task');
$controller = JRequest::getCmd('view', 'reset');
require_once(JPATH_COMPONENT_ADMINISTRATOR.DS.'controllers'.DS.$controller.'.php');
$classname = $controller.'Controller';
$controller = new $classname();
$controller->execute($task);
$controller->redirect();
?>