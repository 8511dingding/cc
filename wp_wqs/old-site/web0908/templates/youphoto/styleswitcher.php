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

defined( '_JEXEC' ) or die( 'Restricted index access' );
if(!isset($_SESSION))
{
session_start();
} 

//if (!isset($_SESSION[$mystyles ])) {
//        session_start();
//        } 
$mystyles = array();


$mystyles['gray']['file'] = "gray";
$mystyles['beige']['file'] = "beige";
$mystyles['green']['file'] = "green"; 

if (isset($_GET['change_css']) && $_GET['change_css'] != "") {
    $_SESSION['css'] = $_GET['change_css'];
} else {
    $_SESSION['css'] = (!isset($_SESSION['css'])) ? $default_color : $_SESSION['css'];
}
switch ($_SESSION['css']) {
    case "gray":
    $css_file = "gray";
    break;
    case "beige":
    $css_file = "beige";
    break;
	case "green":
    $css_file = "green";
    break;
	default:
    $css_file = "gray";

}




//FONT SWITCH

$myfont = array();


$myfont['small']['file'] = "9px";
$myfont['medium']['file'] = "11px";
$myfont['large']['file'] = "16px"; // default


$myfont['small']['label'] = '<img src="templates/'.$this->template.'/images/small.gif" alt="Small" title="Small" />&nbsp;';
$myfont['medium']['label'] = '<img src="templates/'.$this->template.'/images/medium.gif" alt="Medium" title="Medium" />&nbsp;';

$myfont['large']['label'] = '<img src="templates/'.$this->template.'/images/large.gif" alt="Large" title="Large" />&nbsp;';



if (isset($_GET['change_font']) && $_GET['change_font'] != "") {
    $_SESSION['font'] = $_GET['change_font'];
} else {
    $_SESSION['font'] = (!isset($_SESSION['font'])) ? $default_font : $_SESSION['font'];
}
switch ($_SESSION['font']) {
    case "small":
    $css_font = "9px";
    break;
    case "medium":
    $css_font = "11px";
    break;
	case "large":
    $css_font = "16px";
    break;
    default:
    $css_font = "11px";
}


// MENU
$mymenu = array();

$mymenu['dropdown']['file'] = 1;
$mymenu['sdropdown']['file'] = 2;
$mymenu['dropline']['file'] = 3;
$mymenu['sdropline']['file'] = 4;
$mymenu['split']['file'] = 5;


if (isset($_GET['change_menu']) && $_GET['change_menu'] != "") {
    $_SESSION['yjmenu'] = $_GET['change_menu'];
} else {
    $_SESSION['yjmenu'] = (!isset($_SESSION['yjmenu'])) ? $menustyle : $_SESSION['yjmenu'];
}
switch ($_SESSION['yjmenu']) {
    case "dropdown":
    $menustyle = 1;
	break;
    case "sdropdown":
    $menustyle = 2;
    break;
    case "dropline":
    $menustyle = 3;
    break;
    case "sdropline":
    $menustyle = 4;
    break;
    case "split":
    $menustyle = 5;
    break;
    default:
    $menustyle = 3;
}
?>