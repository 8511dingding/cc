<?php
/*======================================================================*\
|| #################################################################### ||
|| # Youjoomla LLC - YJ- Licence Number 2511TV810
|| # Licensed to - Vlad Serov
|| # ---------------------------------------------------------------- # ||
|| # Copyright ©2006-2009 Youjoomla LLC. All Rights Reserved.           ||
|| # This file may not be redistributed in whole or significant part. # ||
|| # ---------------- THIS IS NOT FREE SOFTWARE ---------------- #      ||
|| # http://www.youjoomla.com | http://www.youjoomla.com/license.html # ||
|| #################################################################### ||
\*======================================================================*/
  defined( '_JEXEC' ) or die( 'Direct Access to this location is not allowed.');

//////////////////////// PARAMS /////////////////////////////////////////////
$moduleclass_sfx= $params->get('moduleclass_sfx',"_yjmutlitab");

$module_pozi = $params->get('module_pozi','user1|user2');
$module_title = $params->get('module_title','Title1|Title2');
$ulis_width2 = $params->get('ulis_width2','100px');
$auto_width  = $params->get('auto_width',1);
$is_copy = $params->get('is_copy');
$transtype = $params->get('transtype',1);


//if ($transtype == 1){
//$transition = '';
//}else{
//$transition = '_fade';
//}

////////////////////////////   END PARAMS   /////////////////////////////////////
 JHTML::_('behavior.mootools'); 

$document = JFactory::getDocument();
$document->addStyleSheet(JURI::base() . 'modules/mod_yj_multitab/mod_yj_multitab.css');   
//$linktag_tabs2="<link rel='stylesheet' type='text/css' href='".JURI::base()."/modules/mod_yj_multitab/mod_yj_multitab.css'/>\n";


//$mainframe->addCustomHeadTag($linktag_tabs2);
  echo "<!-- http://www.Youjoomla.com  Youjoomla Multitab Modules for Joomla 1.5 starts here -->	";
echo "<script type='text/javascript' src='".JURI::base()."/modules/mod_yj_multitab/src/mod_yj_multitab.js'></script>\n";


?>

<script language="javascript" type="text/javascript">
	window.addEvent('domready', function(){
			new Tabs({container:'tabs_container<?php echo $is_copy ?>', tabsContainer:'tabs<?php echo $is_copy ?>', classContent:'tab_content<?php echo $is_copy ?>'});			
	});
</script>

<div id="tabs_holder<?php echo $is_copy ?>"><!-- Youjoomla Multitab Holder -->
 <div id="tabs_container<?php echo $is_copy ?>">
<!--Start Multitab -->

<?php

$tab2mods = explode(",", $module_pozi);
$titles = explode(",", $module_title);

 echo '<ul id="tabs'.$is_copy.'">';   
 

$ulis_width = 100/count ($titles);





for($i = 0;$i<count($titles);$i++){

if ($auto_width == 1){
 echo '<li style="width:'.$ulis_width.'%"> '.$titles[$i].' </li>'; 
 }else{
 echo '<li style="width:'.$ulis_width2.'"> '.$titles[$i].' </li>'; 
 }
   
}
echo '</ul>'; 

  for($i = 0;$i<count($tab2mods);$i++){
	$tabs2_out = JModuleHelper::getModules($tab2mods[$i]);
foreach (array_keys($tabs2_out) as $o) {
	
  
  
  

  echo '<div class="tab_content'.$is_copy.'">';         
        echo '<div class="tab_content_in'.$is_copy.'">'; 

	  echo JModuleHelper::renderModule($tabs2_out[$o],array('style'=> 'raw'));
      echo '</div>';  
      echo '</div>';  
		
      
   
  }
  } ?>
  
  
<!--End --> 
</div>
</div><!--Youjoomla Multitab Holder end-->
        
        
      