<?php
/*
 * @version $Id: exclude.php,v 1.4 2010/10/09 07:45:14 Vlado Exp $
 * @package JotCache
 * @copyright (C) 2010 Vladimir Kanich
 * @license http://www.gnu.org/copyleft/gpl.html GNU/GPL
 */
defined('_JEXEC') or die('Restricted access');
require_once(JPATH_COMPONENT_ADMINISTRATOR . DS . 'toolbar.php');
JHTML::_('behavior.tooltip');
JotcacheToolbar::title(JText::_('JOTCACHE_EXCLUDE_TITLE'));
$bar = & JToolBar::getInstance('toolbar');
$msg = JText::_('JOTCACHE_RS_REFRESH_DESC');
JToolBarHelper::customX('apply', 'apply.png', 'apply.png', 'Apply', false);
JToolBarHelper::spacer();
JToolBarHelper::custom('save', 'save.png', 'save.png', 'Save', false);
JToolBarHelper::spacer();
JToolBarHelper::cancel('display', JText::_('CLOSE'));
JToolBarHelper::spacer();
$bar->appendButton('Popup', 'help', 'Help', $this->url . "&start=2", 960, 720, 0, 0);
$rows = $this->data->rows;
?>
<script language="javascript" type="text/javascript">
  function submitbutton(pressbutton) {
    if (pressbutton == 'save'||pressbutton == 'apply') {
      var checked = jotcache.pressed();
      if(!checked){alert( "<?php echo JText::_('JOTCACHE_EXCLUDE_ERR'); ?>"); return;}
    }
    submitform( pressbutton );
  }
  window.addEvent('domready', function(){
    var lang =["<?php echo JText::_('JOTCACHE_EXCLUDE_ERR1'); ?>","<?php echo JText::_('JOTCACHE_EXCLUDE_ERR2'); ?>"];
    jotcache.init(lang);
  });
</script>
<br>
<form action="index2.php" method="post" name="adminForm">
  <table class="adminlist" style="width:60%;">
    <tr>
      <th nowrap="nowrap" width="120"><input type="checkbox" name="toggle" value=""  onclick="checkAll(<?php echo count($rows); ?>);" />&nbsp;<?php echo JText::_('JOTCACHE_EXCLUDE_EXCLUDED'); ?></th>
      <th nowrap="nowrap"><?php echo JText::_('JOTCACHE_EXCLUDE_CN'); ?></th>
      <th><?php echo JText::_('JOTCACHE_EXCLUDE_OPTION'); ?></th>
      <th title="<?php echo JText::_('JOTCACHE_EXCLUDE_VIEWS_DESC'); ?>"><?php echo JText::_('JOTCACHE_EXCLUDE_VIEWS'); ?></th>
    </tr>
    <?php
    $rows = $this->data->rows;
$k = 0;
for ($i = 0, $n = count($rows); $i < $n; $i++) {
$row = &$rows[$i];
$checking = array_key_exists($row->option, $this->data->exclude) ? "checked" : "";
$checked = '<input type="checkbox" id="cb' . $i . '" name="cid[]" value="' . $row->id . '" ' . $checking . ' onclick="isChecked(this.checked);" />';
?>
      <tr class="<?php echo "row$k"; ?>">
        <td align="center"><?php echo $checked; ?></td>
        <td><?php echo $row->name; ?></td>
        <td><?php echo $row->option; ?></td>
        <td><?php if ($checking and $this->data->exclude[$row->option] != 1) { ?>
            <input name="<?php echo "ex_$row->option"; ?>" size="100" value="<?php echo $this->data->exclude[$row->option]; ?>" onchange="jotcache.clicked(this,<?php echo $i; ?>);">
          <?php } else { ?>
            <input name="<?php echo "ex_$row->option"; ?>" size="100" value="" onchange="jotcache.clicked(this,<?php echo $i; ?>);">
          <?php } ?>
        </td>
      </tr>
      <?php $k = 1 - $k;
} ?>
  </table>
  <br/>
  <?php echo $this->data->pageNav->getListFooter(); ?>
  <input type="hidden" name="option" value="com_jotcache" />
  <input type="hidden" name="view" value="reset" />
  <input type="hidden" name="task" value="exclude" />
  <input type="hidden" name="boxchecked" value="0" />
  <input type="hidden" name="hidemainmenu" value="0" />
</form>