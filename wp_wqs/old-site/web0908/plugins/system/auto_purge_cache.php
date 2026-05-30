<?php
// ******************************************************************************
// Title          Auto_Purge_Cache - Plugin for Joomla 1.5x 
// Author         Mike Leeper
// Version        1.2
// Copyright      © by MLWebTechnologies
// License        This is free software and you may redistribute it under the GPL.
//                Auto_Purge_Cache comes with absolutely no warranty. For details,
//                see the license at http://www.gnu.org/licenses/gpl.txt
//                YOU ARE NOT REQUIRED TO KEEP COPYRIGHT NOTICES IN
//                THE HTML OUTPUT OF THIS SCRIPT. YOU ARE NOT ALLOWED
//                TO REMOVE COPYRIGHT NOTICES FROM THE SOURCE CODE.
//
// *******************************************************************************
defined( '_JEXEC' ) or die( 'Restricted access' );
jimport( 'joomla.plugin.plugin' );
jimport( 'joomla.plugin.helper' );
$enabled = JPluginHelper::isEnabled('system','auto_purge_cache');
if(!$enabled){
  return true;
}

class plgSystemAuto_purge_cache extends JPlugin
{
	/*
	 * Constructor
	 */
	function plgSystemauto_purge_cache(& $subject, $config)
	{
		parent::__construct($subject, $config);
  }

	function onAfterInitialise()
	{ 
    global $mainframe;
    jimport('joomla.filesystem.folder');
  	jimport('joomla.filesystem.file');
  
   	$plugin =& JPluginHelper::getPlugin('system', 'auto_purge_cache');
   	$params 	= new JParameter( $plugin->params );
  
  	$enablePurge		= $params->get('config_enable_purge', '0');
  	$enableEmail		= $params->get('config_enable_email', '0');
    $config_prev		= $params->get('config_previous', '86400');
    $config_freq_int		= $params->get('config_freq_int', '1');
    $config_freq = ($config_prev * $config_freq_int);
    $config_email_list		= $params->get('config_email_list');
  	$config_email_sender_name		= $params->get('config_email_sender_name');
  	$config_email_subject		= $params->get('config_email_subject');
  	$config_email_message		= $params->get('config_email_message');
    $count = 0;
  
  	$conf =& JFactory::getConfig();
  	$config_cache_path = $conf->getValue('config.cache_path');
		if(isset($config_cache_path)) {
			$cachepath = $conf->getValue('config.cache_path');
		} else {
			$cachepath = JPATH_ROOT.DS.'cache';
		}
  
  	$mediaPath = JPATH_ROOT.DS.'media';
  	$checkfileName = 'auto_purge_cache_checkfile';
  	$okToContinue = true;
  
    $filearray = JFolder::files($mediaPath, $checkfileName);
    foreach($filearray as $matchfile){
      if((time() - filemtime($mediaPath.DS.$matchfile)) > $config_freq) {
        @unlink($mediaPath.DS.$matchfile);
        } 
      }
    if (is_writable($mediaPath) )
  		{
  		if (is_file($mediaPath.DS.$checkfileName) ) 
  			{
        $okToContinue = false;
        }
  		elseif (!touch($mediaPath.DS.$checkfileName)) 
  			{
        $okToContinue = false;
  			}
  		}
  	else
  	  {
      $okToContinue = false;
      }
    
  	if ($okToContinue && $enablePurge) 
  		{
  		$result = true;
  		$files = JFolder::files($cachepath, '_expire', true, true);
  		foreach($files As $file) {
  			$time = @file_get_contents($file);
  			if ($time < time()) {
  				$result |= JFile::delete($file);
  				$result |= JFile::delete(str_replace('_expire', '', $file));
          $count++;
  			}
  		}
  
     if($okToContinue && $enableEmail && $count > 0){
       $this->apc_email_notification($config_email_list,$config_email_sender_name,$config_email_subject,$config_email_message,$count);
      }
   }
  }

  function apc_email_notification($config_email_list,$sendername,$config_email_subject,$config_email_message,$count)
  {
    global $mainframe;
    jimport( 'joomla.mail.helper' );
    $livesite = JURI::base();
    $sitename = $mainframe->getCfg( 'sitename' );
    $mailfrom = $mainframe->getCfg('mailfrom');
    $filter_match_msg = str_replace("%site%", '<a href="' . $livesite . 'administrator" target="_blank">' . $livesite .'administrator</a>', $filter_match_msg);
  
  			$body = $config_email_message;
  			$body = str_replace("%header%", '<h2>', $body);
  			$body = str_replace("%/header%", '</h2>', $body);
  			$body = str_replace("%br%", "<br />", $body);
  			$body = str_replace("%b%", "<b>", $body);
  			$body = str_replace("%/b%", "</b>", $body);
  			$body = str_replace("%site%", '<a href="' . $livesite . 'administrator" target="_blank">' . $livesite .'administrator</a>', $body);
  			$body = str_replace("%title%", $sitename, $body);
  			$body = str_replace("%count%", $count, $body);
  	
  	$subject = $config_email_subject;
    $email_array = preg_split('/[,]/',$config_email_list, -1, PREG_SPLIT_NO_EMPTY);
    foreach($email_array as $email){
      JUtility::sendMail($mailfrom, $sendername, $email, $subject, $body, 1);
    }
  }

}

?>
