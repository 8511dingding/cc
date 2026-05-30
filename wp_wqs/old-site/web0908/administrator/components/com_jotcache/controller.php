<?php
/*
* @version $Id: controller.php,v 1.1 2010/05/26 06:39:43 Vlado Exp $
* @package JotCache
* @copyright (C) 2010 Vladimir Kanich
* @license http://www.gnu.org/copyleft/gpl.html GNU/GPL
*/
defined('_JEXEC') or die('Restricted access');
jimport('joomla.application.component.controller');
class JotcacheController extends JController {
var $config = null;
var $view = null;
var $model = null;
function JotcacheController($config = array()) {
$this->config = $config;
parent::__construct();
}function getConfig() {
return $this->config;
}function assignViewModel($viewName,$modelName='',$modelPrefix='') {
$this->view = $this->getView($viewName, 'html');
if ($modelName=='') {
$modelName= ucfirst($viewName);
}if ($modelPrefix=='') {
$modelPrefix= ucfirst($modelName).'Model';
}if ($this->model = $this->getModel($modelName,$modelPrefix)) {
$this->view->setModel($this->model, true);
}$this->view->assignRef('config', $this->config);
if (is_object($this->model)) {
$this->model->setState('config', $this->config);
}}function display() {
$this->view->display();
}function show($tpl = null) {
$this->view->show($tpl);
}}?>