<?php
/*
 * @version $Id: default.php,v 1.7 2010/09/02 04:21:36 Vlado Exp $
 * @package JotCache
 * @copyright (C) 2010 Vladimir Kanich
 * @license http://www.gnu.org/copyleft/gpl.html GNU/GPL
 */
defined('_JEXEC') or die('Restricted access');
jimport('joomla.database.table');
require_once(JPATH_COMPONENT_ADMINISTRATOR . DS . 'toolbar.php');
$site_path = JPATH_SITE;
$site_url = JURI::root();
$document = & JFactory::getDocument();
$cacheplg = & JPluginHelper::getPlugin('system', 'jotcache');
$plg_disabled = true;
if (is_object($cacheplg)) {
$plg_disabled = false;
$pars = new JParameter($cacheplg->params);
$cachemark = $pars->get('cachemark');
$cookie_mark = JRequest::getVar('jotcachemark', '0', 'COOKIE', 'INT');
if ($cookie_mark) {
$icon_cookie = $site_url . "administrator/components/com_jotcache/images/icon-32-cookiereset.png";
$text_cookie = JText::_('JOTCACHE_RS_MARK_RESET');
} else {
$icon_cookie = $site_url . "administrator/components/com_jotcache/images/icon-32-cookieset.png";
$text_cookie = JText::_('JOTCACHE_RS_MARK_SET');
}}JHTML::_('behavior.tooltip');
JotcacheToolbar::title(JText::_('JOTCACHE_RS_TITLE'));
$bar = & JToolBar::getInstance('toolbar');
$msg = JText::_('JOTCACHE_RS_REFRESH_DESC');
JToolBarHelper::custom('refresh', 'refresh.png', 'refresh.png', JText::_('JOTCACHE_RS_REFRESH'), false);
if (!$plg_disabled and $cachemark)
JToolBarHelper::customX('cookie', 'cookie.png', 'cookie.png', $text_cookie, false);
JToolBarHelper::deleteList(JText::_('JOTCACHE_RS_DEL_CONFIRM'), 'delete');
JToolBarHelper::spacer();
JToolBarHelper::customX('exclude', 'unpublish.png', 'unpublish.png',JText::_('JOTCACHE_RS_EXCL'), false);
JToolBarHelper::spacer();
$bar->appendButton('Popup', 'help','Help', $this->url."&start=2", 960,720,0,0);
$icon_refresh = $site_url . "administrator/components/com_jotcache/images/icon-32-refresh.png";
JLoader::register('JPaneTabs', JPATH_LIBRARIES . DS . 'joomla' . DS . 'html' . DS . 'pane.php');
$tabs = new JPaneTabs(1);
$callbase = JRequest::getInt('callbase', 1);
$task = JRequest::getVar('task');
?>
<script language="javascript" type="text/javascript">
  function resetSelect() {
    document.getElementById("filter_view").value="";
    document.adminForm.submit();
  }
</script>
<style type="text/css">
  .icon-32-refresh {
    background-image:url(<?php echo $icon_refresh; ?>);
  }
  .icon-32-cookie {
    background-image:url(<?php echo $icon_cookie; ?>);
  }
  .icon-32-back {
    background-image:url(<?php echo $site_url . "administrator/components/com_jotcache/images/icon-32-help.png"; ?>);
  }
  table.adminlist thead tr td.no-border-select {
    outline-style:solid;
    outline-width:1px;
    outline-color:white;
    background-color:white;
  }
</style>
<form action="index2.php" method="post" name="adminForm">
  <table class="adminlist">
    <thead>
      <tr>
        <td class="no-border-select" colspan="3" ><?php if ($plg_disabled) {
echo JText::_('JOTCACHE_RS_DISABLED');
} else {
echo "&nbsp;";
} ?></td>
        <td class="no-border-select"><?php echo $this->lists['com']; ?></td>
        <td class="no-border-select"><?php echo $this->lists['view']; ?></td>
        <td class="no-border-select" colspan="2" >&nbsp;</td>
        <td class="no-border-select"><?php echo $this->lists['mark']; ?></td>
      </tr>
      <tr><th width="50">#</th>
        <th width="5"><input type="checkbox" name="toggle" value="" onclick="checkAll(<?php echo count($this->data->rows); ?>);" /></th>
        <th class="title"><?php echo JText::_('JOTCACHE_RS_FNAME'); ?></th>
        <th nowrap="nowrap"><?php echo JText::_('JOTCACHE_RS_COMP'); ?></th>
        <th nowrap="true"><?php echo JText::_('JOTCACHE_RS_VIEW'); ?></th>
        <th><?php echo JText::_('JOTCACHE_RS_ID'); ?></th>
        <th nowrap="nowrap"><?php echo JText::_('JOTCACHE_RS_CREATED'); ?></th>
        <th nowrap="nowrap"><?php echo JText::_('JOTCACHE_RS_MARK'); ?></th>
      </tr>
    </thead>
    <?php
    $rows = $this->data->rows;
$k = 0;
for ($i = 0, $n = count($rows); $i < $n; $i++) {
$row = &$rows[$i];
      $checked = '<input type="checkbox" onclick="isChecked(this.checked);" value="'.$row->fname.'" name="cid[]" id="cb'.$i.'">';
?>
      <tr class="<?php echo "row$k"; ?>">
        <td align="right"><?php echo $this->data->pageNav->getRowOffset($i); ?></td>
        <td align="center"><?php echo $checked; ?></td>
        <td><?php echo $row->fname; ?></td>
        <td><?php echo $row->com; ?></td>
        <td><?php echo $row->view; ?></td>
        <td align="right" style="padding-right:30px;"><?php echo $row->id; ?></td>
        <td align="center"><?php echo $row->ftime; ?></td>
        <td align="center"><?php echo $row->mark==1?'Yes':''; ?></td>
      </tr>
  <?php $k = 1 - $k;
} ?>
    </table>
    <br/>
<?php echo $this->data->pageNav->getListFooter(); ?>
  <input type="hidden" name="option" value="com_jotcache" />
  <input type="hidden" name="view" value="reset" />
  <input type="hidden" name="task" value="" />
  <input type="hidden" name="boxchecked" value="0" />
  <input type="hidden" name="hidemainmenu" value="0" />
</form>