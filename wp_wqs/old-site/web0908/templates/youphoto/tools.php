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

if ( $showcolor== 1 ){

// COLOR SWITCHER LINKS

while(list($key, $val) = each($mystyles)){

echo "<a href='".$my_request."change_css=".$key."' >".$val["label"]."</a>";

}

}

?>

<?php

if ( $showfont== 1 ){

// FONT SWITCHER LINKS

while(list($key, $val) = each($myfont)){

echo "<a href='".$my_request."change_font=".$key."' >".$val["label"]."</a>";

}



}

?>



<?php

if ( $showwidth== 1 ){

// WIDTH SWITCHER LINKS

while(list($key, $val) = each($mywidth)){

echo "<a href='".$my_request."change_width=".$key."' >".$val["label"]."</a>";

}

}

?>
