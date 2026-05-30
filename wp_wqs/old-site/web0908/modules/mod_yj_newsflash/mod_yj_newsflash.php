<?php
/*----------------------------------------------------------------------
#Youjoomla Newsflash Module for Joomla 1.5 Version 3.0
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
require_once (JPATH_SITE.DS.'components'.DS.'com_content'.DS.'helpers'.DS.'route.php');

$database					=& JFactory::getDBO();
$mosConfig_absolute_path	= JPATH_ROOT;
$mosConfig_live_site 		= JURI :: base();    

global $mosConfig_absolute_path, $mosConfig_live_site, $mainframe, $database, $_MAMBOTS;

$document = JFactory::getDocument();
$document->addStyleSheet(JURI::base() . 'modules/mod_yj_newsflash/stylesheet.css');



  echo "<!-- http://www.Youjoomla.com  Youjoomla Newslash Module V3 for Joomla 1.5 starts here -->	";

?>

		
        
<?php

        
  $now 		    = date('Y-m-d H:i:s');
  $database 	=& JFactory::getDBO();
  $nullDate 	= $database->getNullDate();


$get_items = $params->get('get_items',1);
$nitems = $params->get ('nitems',4);
$chars = $params->get ('chars',40);
$imgwidth=$params->get('imgwidth',"40px");
$imgheight=$params->get('imgheight',"40px");
$imgalign = $params->get('imgalign',"left");
$ordering = $params->get('ordering',3);// 1 = ordering | 2 = popular | 3 = random 
$showimage = $params->get('showimage',1);
$showrm = $params->get('showrm',1);
$showtitle = $params->get('showtitle',1);
$specificitems 	= $params->get('specificitems','');		
if($ordering ==1){
$order = 'ordering';
}elseif($ordering == 2){
$order = 'hits';
}elseif ($ordering == 3){
$order = 'RAND()';
}

			
			

		$db			=& JFactory::getDBO();
		$user		=& JFactory::getUser();
		$userId		= (int) $user->get('id');
		$aid		= $user->get('aid', 0);

		$contentConfig = &JComponentHelper::getParams( 'com_content' );
		$access		= !$contentConfig->get('shownoauth');

		$nullDate	= $db->getNullDate();

		$date =& JFactory::getDate();
		$now = $date->toMySQL();

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
			
			
$database->setQuery( $sql );
$load_items = $database->loadObjectList();

?>
<?php
     // error_reporting(E_ALL);
	 
require_once('modules/mod_yj_newsflash/lib/slike.php');
foreach ( $load_items as $row ) {
    $date = JHTML::_('date', $row->created, '%d-%m-%Y');
    $intro 	= substr(strip_tags($row->introtext),0,$chars)."...";
    $link = ContentHelperRoute::getArticleRoute($row->slug, $row->catslug, $row->sectionid);
			$img_url = article_image($row);
    
            $img_out = '';
			if(isset($img_url) && $img_url != "") $img_out="<a href=\"".JRoute::_($link)."\"><img src=\"".$img_url."\" border=\"0\" height=\"".$imgheight."\" align=\"".$imgalign."\" title=\"".$row->title." \" width=\"".$imgwidth."\" alt=\"\"/></a>";


echo "<div class=\"yjnewsflash\">";
if($showimage == 1){

if($imgalign == 'left' || $imgalign == 'right' || $imgalign == 'top'){


if($imgalign == 'top'){
echo '<div class="nfimgpos">';
}
if(isset($img_url) && $img_url != "") echo $img_out;

if($imgalign == 'top'){
echo '</div>';
}
}
}

echo '<div class="yjnf_descr">';
if($showtitle == 1){
echo "<a class=\"yjnewsflash_title\" href=\"".JRoute::_($link)."\">".$row->title."</a>";
}
echo "<p>".$intro."</p>";
echo '</div>';

if($showimage == 1){
if($imgalign == 'bottom'){


echo '<div class="nfimgpos">';
if(isset($img_url) && $img_url != "") echo $img_out;
echo '</div>';

}
}
$show_cat_title = $params->get('show_cat_title',1);
$showdate = $params->get('showdate',1);
if ($show_cat_title ==1){
$showcat_title="In&nbsp;".$row->cattitle."<br />";
}else{
$showcat_title="";
}
if ($showdate ==1){
$show_date=$date;
}else{
$show_date="";
}

if($showdate == 1 || $show_cat_title ==1){
echo "<span class=\"yjnewsflash_date\">".$showcat_title."".$show_date."</span>";
}
if($showrm == 1){
echo "<span class=\"yjnsreadon\"><a class=\"yjns_rm\" href=\"".JRoute::_($link)."\">more</a></span>";
}
echo "</div>\n";
}

?>



