<?php
/*======================================================================*\
|| #################################################################### ||
|| # Youjoomla LLC - YJ- Licence Number 2511TV810
|| # Licensed to - Vlad Serov
|| # ---------------------------------------------------------------- # ||
|| # Copyright (C) 2006-2009 Youjoomla LLC. All Rights Reserved.        ||
|| # This file may not be redistributed in whole or significant part. # ||
|| # ---------------- THIS IS NOT FREE SOFTWARE ---------------- #      ||
|| # http://www.youjoomla.com | http://www.youjoomla.com/license.html # ||
|| #################################################################### ||
\*======================================================================*/

// no direct access
defined('_JEXEC') or die('Restricted access');
$who = strtolower($_SERVER['HTTP_USER_AGENT']);
JHTML::_('behavior.mootools');
require_once (JPATH_SITE.DS.'components'.DS.'com_content'.DS.'helpers'.DS.'route.php');
require_once('modules/mod_yj_accslider/lib/slike.php');
              $get_items        = $params->get   ('get_items',1);
              $nitems           = $params->get   ('nitems',4);
              $chars            = $params->get   ('chars',40);
              $chars_nav        = $params->get   ('chars_nav',40);
              $ordering         = $params->get   ('ordering',3);// 1 = ordering | 2 = popular | 3 = random 
              $specificitems 	= $params->get   ('specificitems','');		
	 
			  if($ordering ==1){
              $order = 'ordering';
              }elseif($ordering == 2){
              $order = 'hits';
              }elseif ($ordering == 3){
              $order = 'RAND()';
              }
			  
			  /* script settings */
			  
			  
			  $closedWidth      = $params->get   ('closedWidth',65);
			  $openedWidth      = $params->get   ('openedWidth',640);
			  $sliderWidth      = $params->get   ('sliderWidth',"900px");
			  $sliderHeight      = $params->get   ('sliderHeight',"330px");
			  $infoPosition      = $params->get   ('infoPosition',"-50");
			  $autoSlide        = $params->get   ('autoSlide',"5000");
/* head tags */
$document = &JFactory::getDocument();
$document->addStyleSheet(JURI::base() . 'modules/mod_yj_accslider/stylesheet.css');
$document->addScript(JURI::base() . 'modules/mod_yj_accslider/lib/accslider.js');

$document->addScriptDeclaration("
	window.addEvent('domready', function(){
		new FancySlider({
			container:'accslider',
			elements:'.slide',
			closedWidth:".$closedWidth.",
			openedWidth:".$openedWidth.",
			autoSlide:".$autoSlide.",
			infoItems: '.info',
			hideTo: ".$infoPosition."
		});
	})
");


$document->addCustomTag('
  <style type="text/css">
#accslider li.opened{
width:'.$openedWidth.'px;
}
</style>

');

  echo "<!-- http://www.Youjoomla.com  Youjoomla Accordion Slider Module V 1.0 for Joomla 1.5 starts here -->	";
/* end head tags */
?>
<?php
		$db			=& JFactory::getDBO();
		$user		=& JFactory::getUser();
		$userId		= (int) $user->get('id');
		$aid		= $user->get('aid', 0);
		$contentConfig = &JComponentHelper::getParams( 'com_content' );
		$access		= !$contentConfig->get('shownoauth');
		$nullDate	= $db->getNullDate();
		$date =& JFactory::getDate();
		$now = $date->toMySQL(); //date('Y-m-d H:i:s');
		$where		= 'a.state = 1'
			. ' AND ( a.publish_up = '.$db->Quote($nullDate).' OR a.publish_up <= '.$db->Quote($now).' )'
			. ' AND ( a.publish_down = '.$db->Quote($nullDate).' OR a.publish_down >= '.$db->Quote($now).' )'
			;
	if(!empty($specificitems)){
		$where .= ' AND a.id IN ('.$specificitems.')';
	}else{
	    $where .= ' AND cc.id = '.$get_items.'';
	}
$sql = 'SELECT a.*, ' .
' CASE WHEN CHAR_LENGTH(a.alias) THEN CONCAT_WS(":", a.id, a.alias) ELSE a.id END as slug,'. 
' CASE WHEN CHAR_LENGTH(cc.alias) THEN CONCAT_WS(":", cc.id, cc.alias) ELSE cc.id END as catslug,'.
'cc.title as cattitle,'.
's.title as sectitle'.

			' FROM #__content AS a' .
			' INNER JOIN #__categories AS cc ON cc.id = a.catid' .
			' INNER JOIN #__sections AS s ON s.id = a.sectionid' .
			' WHERE '. $where .'' .
			($access ? ' AND a.access <= ' .(int) $aid. ' AND cc.access <= ' .(int) $aid. ' AND s.access <= ' .(int) $aid : '').
			' AND s.published = 1' .
			' AND cc.published = 1' .
			' ORDER BY '.$order .' LIMIT 0,'.$nitems.'';
			
$db->setQuery( $sql );
$load_items = $db->loadObjectList();
$acc_slides = array();
foreach ( $load_items as $row ) {
	$acc_slide = array(
			'intro' => substr(strip_tags($row->introtext),0,$chars),
			'link' => ContentHelperRoute::getArticleRoute($row->slug, $row->catslug, $row->sectionid),
			'img_url' => $img_url = articleaccs_image($row),
			'title' => $row->title,
			'img_url' => '',
			'img_out' =>"<img src=\"".JURI::base().$img_url."\" border=\"0\"  title=\"".$row->title." \"  alt=\"\"/>"
    	);
  		$acc_slides[] = $acc_slide;
  	} 
?>

<div id="accslide_holder" style="height:<?php echo $sliderHeight ?>;width:<?php echo $sliderWidth ?>;">
    <ul id="accslider">
        <?php $i=0; foreach ($acc_slides as $acc_slide):?>
        <li class="slide<?php if($i==0):?> opened<?php endif ?>" style="height:<?php echo $sliderHeight ?>;">
            <?php  if(isset($img_url) && $img_url != "") echo $acc_slide['img_out'] ?>
            <div class="info" style="width:<?php echo $openedWidth -40 ?>px;bottom:<?php echo $infoPosition ?>px;"> <a href="<?php  echo  $acc_slide['link'] ?>"><span class="title">
                <?php  echo  $acc_slide['title'] ?>
                </span></a>
                <?php  echo  $acc_slide['intro'] ?>
            </div>
        </li>
        <?php $i+=1; endforeach;?>
    </ul>
</div>
