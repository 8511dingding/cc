<?php
/*----------------------------------------------------------------------
#Youjoomla Bumpit - 
# ----------------------------------------------------------------------
# Copyright (C) 2008 - 2009 You Joomla. All Rights Reserved.
# License: Commercial
# Website: http://www.youjoomla.com
------------------------------------------------------------------------*/
// no direct access
defined('_JEXEC') or die('Restricted access');

//remove notice msg from lay_out
ini_set('error_reporting',E_ALL ^ E_NOTICE);

function ago($timestamp){

	$format_time_array = explode(" ",$timestamp);
	$year = preg_grep("/^([0-9]{4})/", $format_time_array);
	$day = preg_grep("/^([0-9]{2})/", $format_time_array);
	$time = preg_grep("/^([0-9]{2}:[0-9]{2}:[0-9]{2})/", $format_time_array);
	$time = array_values($time);
	$time_array = explode(":",$time[0]);
	$month = preg_grep("/^([a-zA-Z]{3})/", $format_time_array);
	switch($month[1]){
		case 'Jan':
			$month_nr = 1;
		break;
		case 'Feb':
			$month_nr = 2;
		break;
		case 'Mar':
			$month_nr = 3;
		break;
		case 'Apr':
			$month_nr = 4;
		break;
		case 'May':
			$month_nr = 5;
		break;
		case 'Jun':
			$month_nr = 6;
		break;
		case 'Jul':
			$month_nr = 7;
		break;
		case 'Aug':
			$month_nr = 8;
		break;
		case 'Sep':
			$month_nr = 9;
		break;
		case 'Oct':
			$month_nr = 10;
		break;
		case 'Nov':
			$month_nr = 11;
		break;																					
		case 'Dec':
			$month_nr = 12;
		break;
		default :
			$month_nr = 1;
		break;
	}
	
	// Evaluate how much difference there is between local and GTM/UTC
	// Don't forget to correct for daylight saving time...
	$aNow = localtime();
	$iDelta = gmmktime(1, 1, 1, 1, 1, 1970, $aNow[8]) - mktime(1, 1, 1, 1, 1, 1970, $aNow[8]);
	
	$timestamp = mktime($time_array[0], $time_array[1], $time_array[2], $month_nr, $day[2], $year[5]);
	$difference = time() - ($timestamp + $iDelta);
	//if difference in smaller than 0 sec put the difference to 1 second
	if($difference <= 0){
		$difference = 1;
	}
	$periods = array("second", "minute", "hour", "day", "week", "month", "years");
	$lengths = array("60","60","24","7","4.35","12","10");
	for($j = 0; $difference >= $lengths[$j]; $j++){
		$difference /= $lengths[$j];
	}
	
	//$difference = floor($difference);
	$difference = round($difference);   
	if($difference != 1) $periods[$j].= "s";
	$text = "$difference $periods[$j] ".JText::_( 'TWITTER AGO' );
	
	return $text;
}

	$twitter_user		= $params->get( 'twitter_user', '' );
	$nr_article			= $params->get( 'nr_article', '20' );
	$tweet_limit		= $params->get( 'tweet_limit', '0' );
	$tweet_link			= $params->get( 'tweet_link', '1' );	
	$tweet_date			= $params->get( 'tweet_date', '1' );
	$tweet_follow		= $params->get( 'tweet_follow', '1' );
	$tweet_image		= $params->get( 'tweet_image', '1' );

	JHTML::stylesheet('stylesheet.css', JURI :: base().'/modules/mod_yj_twitter/mod_yj_twitter/', false);		
	require_once( JPATH_ROOT.DS.'libraries'.DS.'domit'.DS.'xml_domit_lite_parser.php' );    

	//$xml_file = "http://search.twitter.com/search.atom?q=from:" . $twitter_user . "&rpp=".$nr_article;
	//$xml_file = "http://twitter.com/statuses/user_timeline/".$twitter_user.".rss";
	if($twitter_user != ''){
		$xml_file = "http://twitter.com/statuses/user_timeline/".$twitter_user.".xml?count=".$nr_article;
		$xmlDoc = new DOMIT_Lite_Document();
		$xmlDoc->resolveErrors( true );
		//$xmlDoc->errorString = JText::_( 'SERVICE UNAVAILABLE' );
		if (!@$xmlDoc->loadXML_utf8($xml_file, false, true, false)) {
			$twitter_return =  JText::_( 'SERVICE UNAVAILABLE' );
			//continue;
		}else{
			$root 			= &$xmlDoc->documentElement;
			$records		=& $root->getElementsByTagName('status');
			$records		= $records->toNormalizedString();
			$records_array 	= explode("<status>",$records);
			$twitter_return = array();

			if(!isset($records_array[1])){
				$twitter_return =  JText::_( 'TWITTER NOT FOUND' );		
			}else{
				foreach($records_array as $record_row => $record){
					if($record != ''){
						//get title
						$pattern = '/\<text\>([^<]+)\<\/text\>/s';
						preg_match($pattern, $record, $text);
						if(!empty($text)){
							$twitter_return[$record_row]['text'] = $text[1];
						}
						//get image
						$pattern = '/\<profile_image_url\>([^<]+)\<\/profile_image_url\>/s';
						preg_match($pattern, $record, $profile_image_url);
						if(!empty($profile_image_url)){
							$twitter_return[$record_row]['profile_image_url'] = $profile_image_url[1];
						}					
						//get updated
						$pattern = '/\<created_at\>([^<]+)\<\/created_at\>/s';
						preg_match($pattern, $record, $created_at);
						if(!empty($created_at)){
							//$date = explode("+",$updated[1]);
							$twitter_return[$record_row]['created_at'] = ago($created_at[1]);
						}
						//twitter link
						$pattern = '/\<id\>([^<]+)\<\/id\>/s';
						preg_match($pattern, $record, $id);
						if(!empty($id)){
							$twitter_return[$record_row]['id'] = $id[1];
						}
					}
				}
				array_values($twitter_return);
			}
		}
	}else{
		$twitter_return =  JText::_( 'TWITTER USERNAME NOT FOUND' );
	}
?>