<?php
/*----------------------------------------------------------------------
#Youjoomla Twitter - 
# ----------------------------------------------------------------------
# Copyright (C) 2008 - 2009 You Joomla. All Rights Reserved.
# License: Commercial
# Website: http://www.youjoomla.com
------------------------------------------------------------------------*/
// no direct access
defined('_JEXEC') or die('Restricted access');

//remove notice msg from lay_out
ini_set('error_reporting',E_ALL ^ E_NOTICE);

echo "<!-- http://www.Youjoomla.com  Yj Twitter for Joomla 1.5 starts here -->	";
	if(is_array($twitter_return)){
		foreach($twitter_return as $twitter_row){
			//generate tweet title
			$tweet_title = $tweet_limit > 0 ? substr($twitter_row['text'],0,$tweet_limit)."..." : $twitter_row['text'];
			//generate tweet link
			$tweet_title = $tweet_link == 1 ? "<a href='http://twitter.com/".$twitter_user."/statuses/".$twitter_row['id']."' target='_blank'>".$tweet_title."</a>" : $tweet_title ;

			echo "<div class='yj_twitter_cont'>";
				echo "<div class='yj_twitter_title'>".$tweet_title."</div>";
				echo $tweet_date == 1 ? "<div class='yj_twitter_updated'>".$twitter_row['created_at']."</div>" : '';
			echo "</div>";	
		}
		echo "<div class='yj_twitter_footer'>";
			echo $tweet_image == 1 ? "<div class='yj_twitter_image'><img src='".$twitter_row['profile_image_url']."' alt='' title='' /></div>" : "";		
			echo $tweet_follow == 1 ? "<div class='yj_twitter_follow'><a href='http://twitter.com/".$twitter_user."' target='_blank'>".JText::_( 'TWITTER FOLLOW ME' )."</a></div>" : '';
		echo "</div>";
	}else{
		echo $twitter_return;
	}
echo "<!-- http://www.Youjoomla.com  Yj Twitter for Joomla 1.5 ends here -->";
?>