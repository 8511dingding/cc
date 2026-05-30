<?php
/*
** @version: joomslide.php  December 2008
* @package joomslide
* @author Juan Miguel Sanchez joomslide@nospam@gamedev.es
* @license http://www.gnu.org/copyleft/gpl.html GNU/GPL
* @version 1.4
* @description: Joomla plugin to display thumbnails inside content.
*/

defined( '_JEXEC' ) or  die('Restricted access');
jimport( 'joomla.event.plugin' );

//Language frontend files
$document	= & JFactory::getDocument();
$mosConfig_lang = strtolower($document->getLanguage());
$mosConfig_absolute_path = preg_replace("!(\\\)!i","/",JPATH_ROOT);
define('_JOOMSLIDE_PATH',$mosConfig_absolute_path.'/plugins/content/joomslide');
if (file_exists(_JOOMSLIDE_PATH . '/language/' . $mosConfig_lang . '.php')) {
  include_once(_JOOMSLIDE_PATH. '/language/' . $mosConfig_lang . '.php');
} else {
  include_once(_JOOMSLIDE_PATH . '/language/en-gb.php');
}

class plgContentJoomSlide extends JPlugin
{
	function plgContentJoomSlide (& $subject) {
		
		parent::__construct($subject);
		$this->plugin = &JPluginHelper::getPlugin('content', 'joomslide');
		$this->params = new JParameter($this->plugin->params);
		$this->pluginRegistry = $this->params->_registry['_default']['data'];
		$this->pluginRegistry->add_header=0;
	}

	// Function for include headers
	function JoomSlide_Add_Header()
	{
		//Document
		$doc =&JFactory::getDocument();
		//files needed
		$doc->addScript($this->pluginRegistry->highslidePath.$this->pluginRegistry->highslideScript);
		if ($this->pluginRegistry->allowFlash=="1")
			$doc->addScript($this->pluginRegistry->highslidePath.'swfobject.js');
		//Advanced efects
		if ($this->pluginRegistry->advancedEfects=="1")
			$doc->addScript($this->pluginRegistry->highslidePath.'easing_equations.js');
		//Highslide Styleshet
		$doc->addStyleSheet($this->pluginRegistry->highslidePath.'highslide.css');
		$CssStyle = array ();
		$CssStyle[] = '<style type="text/css">';
		if ($this->pluginRegistry->customColors=="1") {
			$CssStyle[]= '	.highslide img { border-color: '.       $this->pluginRegistry->TumbBorderColor .'; }';
			$CssStyle[]= '	.highslide:hover img { border-color: '. $this->pluginRegistry->TumbBorderColorHover .'; }';
			$CssStyle[]= '	.highslide-image { border-color: '.     $this->pluginRegistry->ImageBorderColor .'; }';
			$CssStyle[]= '	.highslide-heading { background: '. $this->pluginRegistry->HeaderBackground .'; }';
			$CssStyle[]='	.highslide-heading { color: '.    $this->pluginRegistry->HeaderTextColor .'; }';
			$CssStyle[]= '	.highslide-caption { background: '.     $this->pluginRegistry->CaptionBackbroundColor.'; }';
			$CssStyle[]= '	.highslide-caption { color: '.          $this->pluginRegistry->CaptionTextColor .'; }';
			$CssStyle[]= '	.highslide-wrapper { background:'.        $this->pluginRegistry->WrapperColor .';}';
			$CssStyle[]= '	.highslide-outline { background:'.        $this->pluginRegistry->OutlineColor .';}';
			$CssStyle[]= '	.highslide-loading { background:'.        $this->pluginRegistry->LoadingColor .';}';
			$CssStyle[]= '	.highslide-loading{ background:'.        $this->pluginRegistry->LoadingBackground .';}';
		}
		$CssStyle[]= '	.highslide-dimming { background: '.     $this->pluginRegistry->dimmingColor.'; }';
		//Show/Hide Thumb when expand image
		if ($this->pluginRegistry->showThumbWhenExpand=="1") {
			$CssStyle[]= '	.highslide-active-anchor img { visibility:visible;}';
		}
		$CssStyle[] = '</style>';
		$doc->addCustomTag(implode("\n", $CssStyle),"text/css");
		$this->JoomSlide_Add_Header_HS();
	}
	function JoomSlide_Add_Header_HS()
	{
		//$Plugin_path = JURI::root(true).'plugins/content/joomslide/';
		//Highslide config
		$HSconfig    = array ();
		//Languajes
		$HSconfig[]= "	hs.lang = {
			loadingText :     '".JS_LOADING_TEXT."',
			loadingTitle :    '".JS_LOADING_TITLE."',
			focusTitle :      '".JS_FOCUS_TITLE."',
			fullExpandTitle : '".JS_FULL_EXPAND_TITLE."',
			fullExpandText :  '".JS_FULL_EXPAND_TEXT."',
			creditsText :     '".JS_CREDITS_TEXT."',
			creditsTitle :    '".JS_CREDITS_TITLE."',
			previousText :    '".JS_PREVIOUS_TEXT."',
			previousTitle :   '".JS_PREVIOUS_TITLE."',
			nextText :        '".JS_NEXT_TEXT."',
			nextTitle :       '".JS_NEXT_TITLE."',
			moveTitle :       '".JS_MOVE_TITLE."',
			moveText :        '".JS_MOVE_TEXT."',
			closeText :       '".JS_CLOSE_TEXT."',
			closeTitle :      '".JS_CLOSE_TITLE."',
			resizeTitle :     '".JS_RESIZE_TITLE."',
			playText :        '".JS_PLAY_TEXT."',
			playTitle :       '".JS_PLAY_TITLE."',
			pauseText :       '".JS_PAUSE_TEXT."',
			pauseTitle :      '".JS_PAUSE_TITLE."',
			number	:         '".JS_NUMBER."',
			restoreTitle :    '".JS_RESTORE_TITLE."'
		};";
		//Highslide Options
		$HSconfig[]= "	hs.graphicsDir = '".JURI::root(true).'/'. $this->pluginRegistry->highslidePath . "graphics/';";
		$HSconfig[]= "	hs.align = '". $this->pluginRegistry->alignImage ."';";
		$HSconfig[]= "	hs.anchor = '". $this->pluginRegistry->anchor ."';";
		$HSconfig[]= "	hs.transitions = ['expand', 'crossfade'];";
		$HSconfig[]= "	hs.transitionDuration = ". $this->pluginRegistry->transitionDuration .";";
		$HSconfig[]= "	hs.expandDuration = ". $this->pluginRegistry->expandDuration .";";
		$HSconfig[]= "	hs.expandSteps = ". $this->pluginRegistry->expandSteps .";";
		$HSconfig[]= "	hs.restoreSteps = ". $this->pluginRegistry->restoreSteps .";";
		$HSconfig[]= "	hs.dragSensitivity = ". $this->pluginRegistry->dragSensitivity .";";
		$HSconfig[]= "	hs.numberOfImagesToPreload = ". $this->pluginRegistry->numberOfImagesToPreload .";";
		// Credits display
		if($this->pluginRegistry->showCredits != "0") {
			if ($this->pluginRegistry->showCredits =="2") {
				$HSconfig[]= "hs.lang.creditsText= 'Powered by JoomSlide';";
				$HSconfig[]= "hs.creditsHref= 'http://joomlacode.org/gf/project/joomslide/';";
			}
			if ($this->pluginRegistry->showCredits =="3") {
				$HSconfig[]= "hs.lang.creditsText= '".$this->pluginRegistry->customCredits."';";
				$HSconfig[]= "hs.creditsHref= '".$this->pluginRegistry->customUrl."';";
			}
			//$HSconfig[]= "	hs.showCredits = false;";
			if($this->pluginRegistry->urlCredits=="0") {
				$HSconfig[]= "hs.creditsHref = 'javascript:;'";
			}
		} else {
			$HSconfig[]="	hs.showCredits = false;";
		}
		//Outline Type
		if($this->pluginRegistry->outlineType != "No_Border") {
			$HSconfig[]= "	hs.outlineType = '". $this->pluginRegistry->outlineType ."';";
		}
		//Key Listener
		if($this->pluginRegistry->KeyListener == "0") {
			$HSconfig[]= "	hs.enableKeyListener = false;";
		}
		//Dimming
		if($this->pluginRegistry->dimming != "0") {
			$HSconfig[]= "	hs.dimmingOpacity = ". $this->pluginRegistry->dimmingOpacity .";";
			$HSconfig[]= "	hs.dimmingDuration = ". $this->pluginRegistry->dimmingDuration .";";
		}
		//Right Click
		if($this->pluginRegistry->rightClick == "0") {
			$HSconfig[]= "	hs.blockRightClick = true;";
		}
		//Multiple Instances
		if($this->pluginRegistry->multipleInstances == "1") {
			$HSconfig[]= "	hs.allowMultipleInstances = true;";
		}
		//Size Reduction
		if($this->pluginRegistry->sizeReduction == "0") {
			$HSconfig[]= "	hs.allowSizeReduction = false;";
		}
		//Drag by Heading
		if($this->pluginRegistry->dragByHeading == "0") {
			$HSconfig[]= "	hs.dragByHeading = false;";
		}
		//Number Position
		if ($this->pluginRegistry->numberPosition != "Disabled") {
			$HSconfig[]= "	hs.numberPosition = \"". $this->pluginRegistry->numberPosition ."\";";
		}
		//Fade In Out
		if($this->pluginRegistry->fadeInOut == "1") {
			$HSconfig[]= "	hs.fadeInOut = true;";
		}
		//Advanced Effects
		if ($this->pluginRegistry->advancedEfects =="1") {
			$HSconfig[]= "	hs.easing = '". $this->pluginRegistry->easing ."';";
			$HSconfig[]= "	hs.easingClose = '". $this->pluginRegistry->easingClose ."';";
		}
		//Caption Text
		if($this->pluginRegistry->captionText != "Disabled") {
			$HSconfig[]= "	hs.captionEval = '". $this->pluginRegistry->captionText ."';";
			if ($this->pluginRegistry->captionOverlay=="1") {
				if (($this->pluginRegistry->captionOverlayFirstPosition!="disabled")&&($this->pluginRegistry->captionFirstPosition!="disabled"))
					$HSconfig[]= "	hs.captionOverlay.position = '". $this->pluginRegistry->captionOverlayFirstPosition ." ". $this->pluginRegistry->captionOverlaySecondPosition ."';";
				elseif ($this->pluginRegistry->captionOverlayFirstPosition!="disabled")
					$HSconfig[]= "	hs.captionOverlay.position = '". $this->pluginRegistry->captionOverlayFirstPosition ."';";
				elseif ($this->pluginRegistry->captionOverlaySecondPosition!="disabled")
					$HSconfig[]= "	hs.captionOverlay.position = '". $this->pluginRegistry->captionOverlaySecondPosition ."';";
				$HSconfig[]= "	hs.captionOverlay.width = '". $this->pluginRegistry->captionOverlayWidth ."';";
				$HSconfig[]= "	hs.captionOverlay.opacity = ". $this->pluginRegistry->captionOverlayOpacity .";";
				$HSconfig[]= "	hs.captionOverlay.hideOnMouseOut = ".$this->pluginRegistry->captionOverlayHideOnMouse.";";
			}
		}
		//Wapper Class
		if ($this->pluginRegistry->wrapperColor!="white")
			$HSconfig[]= "	hs.wrapperClassName = '".$this->pluginRegistry->wrapperColor."';";

		//SlideShow
		if ($this->pluginRegistry->enableSlideShow=="1")
		{
			$HSconfig[]= "	if (hs.addSlideshow) hs.addSlideshow({";
			$HSconfig[]= "		interval: ".$this->pluginRegistry->slideshowInterval.",";
			$HSconfig[]= "		repeat: ".$this->pluginRegistry->slideshowRepeat.",";
			//ControlBar
			$HSconfig[]= "		useControls: ".$this->pluginRegistry->controlBar.",";
			if ($this->pluginRegistry->fixedControls=="fit")
				$HSconfig[]= "		fixedControls: 'fit',";
			elseif ($this->pluginRegistry->fixedControls=="enabled")
				$HSconfig[]= "		fixedControls: true,";
			else
				$HSconfig[]= "		fixedControls: false,";
			$HSconfig[]= "		overlayOptions: {";
			//IE bug when controls-in-heading and opacity isn't 1
			if ($this->pluginRegistry->wrapperColor!='controls-in-heading')
				$HSconfig[]= "			opacity: ". $this->pluginRegistry->barOpacity .",";
			else
				$HSconfig[]= "			opacity: 1,";
			$HSconfig[]= "			position: '". $this->pluginRegistry->barFirstPosition ." ". $this->pluginRegistry->barSecondPosition ."',";
			$HSconfig[]= "			width: '". $this->pluginRegistry->barWidth ."',";
			$HSconfig[]= "			hideOnMouseOut: ".$this->pluginRegistry->barHideOnMouse;
			$HSconfig[]= "		}";
			$HSconfig[]= "	});";
		}
		//Clode Button MAC style
		if ($this->pluginRegistry->showCloseButton=="1") {
			$HSconfig[]= "hs.registerOverlay({";
			$HSconfig[]= "overlayId: 'closebutton',";
			$HSconfig[]= "position: '".$this->pluginRegistry->CloseButtonFirstPosition." ".$this->pluginRegistry->CloseButtonSecondPosition."',";
			$HSconfig[]= "fade: 2";
			$HSconfig[]= "});";
		}
		// Events on Mouse Out
		if ($this->pluginRegistry->closeImageEvent=="0") {
			// close on mouse out
			$HSconfig[]= "	hs.Expander.prototype.onMouseOut = function (sender) { sender.close();};";
			// close if mouse is not over on expand (using the internal mouseIsOver property)
			$HSconfig[]= "	hs.Expander.prototype.onAfterExpand = function (sender) { if (!sender.mouseIsOver) sender.close();};";
		}
		$doc =&JFactory::getDocument();
		$doc->addScriptDeclaration(implode("\n", $HSconfig));
	}

	function onPrepareContent(&$article,&$params )
	{	
		$regex = "#<img\s*(.*?)/>#s";
		//force include header
		if (($this->pluginRegistry->forceIncludeHeader=="1")&&($this->pluginRegistry->add_header==0))
		{
			$this->JoomSlide_Add_Header();
			$this->pluginRegistry->add_header=1;
		}
		$article->text = preg_replace_callback( $regex,array($this,'plgContentJoomSlideReplacer'), $article->text );
	}
	
	function plgContentJoomSlideReplacer (&$matches)
	{
		$lower_classname="";
		if (preg_match('#\s*class="(.*?)(-.)?"#s',$matches[1],$classname)){
			$lower_classname=strtolower($classname[1]);
		}
				
		$ApplyToImage=((($this->pluginRegistry->applyAllImages=="0")&&($lower_classname=="joomslide"))||(($this->pluginRegistry->applyAllImages=="1")&&($lower_classname!="joomslide"))||($this->pluginRegistry->applyAllImages=="2"));
		if ((!$ApplyToImage)||($lower_classname=="nojoomslide")) return $matches[0];

		//Default size
		$this->pluginRegistry->thumbSize=$this->pluginRegistry->size;
		//Notice message
		$aux = count ($classname);
		//Thumb small, medium, large, or default size
		if (($aux>2)&&($classname[2])){
			switch ($classname[2]) {
				case "-s":$this->pluginRegistry->thumbSize=$this->pluginRegistry->smallSize;
					break;
				case "-m":$this->pluginRegistry->thumbSize=$this->pluginRegistry->mediumSize;
					break;
				case "-l":$this->pluginRegistry->thumbSize=$this->pluginRegistry->largeSize;
					break;
			}
		}

		//Get atributes
		$this->getImageTags($matches[1]);

		if ((!$this->Can_open_image($matches[0]))||(is_dir($this->pluginRegistry->full_image_path)))
			return $matches[0];
	
		//Header
		if ($this->pluginRegistry->add_header==0) {
			$this->JoomSlide_Add_Header();
			$this->pluginRegistry->add_header=1;
		}

		//check directory
		$thumb_dir = JPATH_BASE  .'/'. $this->pluginRegistry->thumbsDir;
		if (!is_dir($thumb_dir)) mkdir ($thumb_dir ,0755);

		//encode thumbnail name
		$thumb_name = base64_encode($this->pluginRegistry->full_image_path);
		//Get format
		$IMG_TYPE = strtolower(substr($this->pluginRegistry->full_image_path,-3));
		//If jpeg image format
		if ($IMG_TYPE == 'peg') $IMG_TYPE='jpg';
		//Thumbnail image path
		if ($this->pluginRegistry->tumbFormat!='auto')
			$tumb_local_path = '/'.$this->pluginRegistry->thumbsDir . $thumb_name . '.' . $this->pluginRegistry->tumbFormat;
		else
			$tumb_local_path = '/'.$this->pluginRegistry->thumbsDir . $thumb_name . '.' . $IMG_TYPE;
		//Cache and image exist control
		if ($this->Check_cache($tumb_local_path)==1){
			$this->create_tumb ($this->pluginRegistry->source,$tumb_local_path,$IMG_TYPE, $this->pluginRegistry->quality);
		}
		//Return new source
		return $this->contentReplacement($tumb_local_path);
	}

	function Check_cache ($tumb_local_path) {
		if (!file_exists(JPATH_BASE.$tumb_local_path)){
			return 1;
		}else{
			$timecache=(int)$this->pluginRegistry->cacheTime;
			if ($timecache>0) {
				$mivar=filemtime(JPATH_BASE.$tumb_local_path)+ $timecache * 60;
				if (($this->pluginRegistry->cache=='0')||($mivar < time())){
					return 1;
				}
			}
		}
		return 0;
	}
	
	//Create thumbnails file
	function create_tumb ($image_path,$thumb_name,$IMG_TYPE,$_quality)
	{
		//Width & Height
		$this->calculateWidthHeight();
		//Create thumbnail
		switch ($IMG_TYPE) {
			case "jpg":
				$src_img=ImageCreateFromJpeg($this->pluginRegistry->full_image_path);
				$dst_img = imagecreatetruecolor($this->pluginRegistry->thumbWidth, $this->pluginRegistry->thumbHeight);
				break;
			case "gif":
				$src_img=ImageCreateFromGif($this->pluginRegistry->full_image_path);  
				$dst_img=imagecreatetruecolor($this->pluginRegistry->thumbWidth,$this->pluginRegistry->thumbHeight);
				ImagePaletteCopy($dst_img,$src_img);
				break;
			case "png":
				$src_img=ImageCreateFromPng($this->pluginRegistry->full_image_path);
				$dst_img = imagecreatetruecolor($this->pluginRegistry->thumbWidth, $this->pluginRegistry->thumbHeight); 
				ImagePaletteCopy($dst_img,$src_img);
				break;
		}
		
		if ($this->pluginRegistry->doCrop) $this->CalculateCropArea();
		
		ImageCopyResampled($dst_img,$src_img,0,0,$this->pluginRegistry->cropX,$this->pluginRegistry->cropY,$this->pluginRegistry->thumbWidth,$this->pluginRegistry->thumbHeight,$this->pluginRegistry->cropWidth,$this->pluginRegistry->cropHeight);
		//Save thumbnail
		switch ($this->pluginRegistry->tumbFormat) {
			case "jpg":
				$img = Imagejpeg($dst_img,JPATH_BASE .$thumb_name, $_quality);
				break;
			case "gif":
				$img = Imagegif($dst_img,JPATH_BASE .$thumb_name);
				break;
			case "png":
				$img = imagepng($dst_img,JPATH_BASE .$thumb_name,10-intval($_quality/10),NULL);
				break;
			case "auto":
				//Thumbnail image format auto
				switch ($IMG_TYPE) {
					case "jpg":
						$img = Imagejpeg($dst_img,JPATH_BASE .$thumb_name, $_quality);
						break;
					case "gif":
						$img = Imagegif($dst_img,JPATH_BASE .$thumb_name);
						break;
					case "png":
						$img = imagepng($dst_img,JPATH_BASE .$thumb_name,10-intval($_quality/10),NULL);
						break;
				}
				break;
		}
		//free memory
		imagedestroy($dst_img);
	}

	function contentReplacement ($tumb_local_path) {
		//content replacement
		$newsource = '<a href="'.$this->pluginRegistry->source.'" ';
		$newsource .= 'class="highslide" ';
		if ($this->pluginRegistry->openImageEvent=="0")
			$newsource .=' onmouseover="return this.onclick()"';
		$newsource .=' onclick="return hs.expand(this)">' . "\n";
		$newsource .= '	<img ';
		//Apply atributes to thumbnail
		if ($this->pluginRegistry->align!="")
			$newsource .= '	align="'.$this->pluginRegistry->align.'"';
		if ($this->pluginRegistry->border!="")
			$newsource .= '	border="'.$this->pluginRegistry->border.'"';
		if ($this->pluginRegistry->hspace!="")
			$newsource .= '	hspace="'.$this->pluginRegistry->hspace.'"';
		if ($this->pluginRegistry->longdesc!="")
			$newsource .= '	longdesc="'.$this->pluginRegistry->longdesc.'"';
		if ($this->pluginRegistry->usemap!="")
			$newsource .= '	usemap="'.$this->pluginRegistry->usemap.'"';
		if ($this->pluginRegistry->vspace!="")
			$newsource .= '	vspace="'.$this->pluginRegistry->vspace.'"';
		if ($this->pluginRegistry->id!="")
			$newsource .= '	id="'.$this->pluginRegistry->id.'"';
		if ($this->pluginRegistry->style!="")
			$newsource .= '	style="'.$this->pluginRegistry->style.'"';
		if ($this->pluginRegistry->desc!="")
			$newsource .= '	alt="'.$this->pluginRegistry->desc.'"';
		if ($this->pluginRegistry->title!="")
			$newsource .= '	title="'.$this->pluginRegistry->title.'"';
		
		$newsource .= '	src="'.JURI::root(true).$tumb_local_path.'"';
		//end atributes
		$newsource .= '/></a>'."\n";
		//Check Caption text
		$CaptionText="";
		if($this->pluginRegistry->TextPosition != "Disabled") {
			//Text
			if (($this->pluginRegistry->captionText=="alt")&&($this->pluginRegistry->desc!="")){
					$CaptionText .= $this->pluginRegistry->desc;
			}
			elseif (($this->pluginRegistry->captionText=="longDescription")&&($this->pluginRegistry->longdesc!="")){
					$CaptionText .= $this->pluginRegistry->longdesc;
			}
			elseif (($this->pluginRegistry->captionText=="title")&&($this->pluginRegistry->title!="")){
					$CaptionText .= $this->pluginRegistry->title;
			}
			//Text Position (Header or Caption)
			if ($CaptionText!=""){
				$newsource .= '<span class="highslide-'.$this->pluginRegistry->TextPosition.'">' . "\n";
				$newsource .= $CaptionText. "\n";
				$newsource .= '</span>' . "\n";
			}
		}
		if ($this->pluginRegistry->showCloseButton=="1")
			$newsource .= '<div id="closebutton" class="highslide-overlay closebutton" onclick="return hs.close(this)" title="Close"></div>';

		//end replacement and return new code
		return $newsource;
	}
	function calculateWidthHeight() {
		//Get Image size
		$this->pluginRegistry->imagedata = getimagesize($this->pluginRegistry->full_image_path);
		//Full Image
		$this->pluginRegistry->cropX=0;
		$this->pluginRegistry->cropY=0;
		$this->pluginRegistry->cropWidth=$this->pluginRegistry->imagedata[0];
		$this->pluginRegistry->cropHeight=$this->pluginRegistry->imagedata[1];

		$this->pluginRegistry->doCrop=(($this->pluginRegistry->forceAspectRatio=="2")||(($this->pluginRegistry->thumbWidth!="")&&($this->pluginRegistry->forceAspectRatio=="1"))||(($this->pluginRegistry->thumbWidth=="")&&($this->pluginRegistry->forceAspectRatio=="0")));
		//No Resized image or Force Crop
		if (($this->pluginRegistry->thumbWidth=='')||( $this->pluginRegistry->thumbHeight=='')||($this->pluginRegistry->doCrop==True)){
			//Aspect Ratio
			$this->calculateAspectRatio();
			//Size of thumbnail
			//Preserve apect ratio by width
			if ($this->pluginRegistry->maxThumbSize=="width") {
				$this->pluginRegistry->thumbWidth  = $this->pluginRegistry->thumbSize;
				$this->pluginRegistry->thumbHeight = (int)($this->pluginRegistry->thumbSize/$this->pluginRegistry->aspectRatio);
			//Preserve apect ratio by Height
			} else {
				$this->pluginRegistry->thumbHeight = $this->pluginRegistry->thumbSize;
				$this->pluginRegistry->thumbWidth  = (int)($this->pluginRegistry->thumbSize/$this->pluginRegistry->aspectRatio);
			}
		}
		//Don't enlarge small images. Check button
		$this->pluginRegistry->thumbIsBiggerImage=(($this->pluginRegistry->thumbHeight>$this->pluginRegistry->imagedata[1])||($this->pluginRegistry->thumbWidth>$this->pluginRegistry->imagedata[0]));
		if (($this->pluginRegistry->thumbBiggerImage=="0")&&($this->pluginRegistry->thumbIsBiggerImage)) {
			$this->pluginRegistry->thumbWidth =$this->pluginRegistry->imagedata[0];
			$this->pluginRegistry->thumbHeight=$this->pluginRegistry->imagedata[1];
			$this->pluginRegistry->doCrop=false;
			$this->pluginRegistry->cropX=0;
			$this->pluginRegistry->cropY=0;
			$this->pluginRegistry->cropWidth=$this->pluginRegistry->imagedata[0];
			$this->pluginRegistry->cropHeight=$this->pluginRegistry->imagedata[1];
		}
	}
	//Force Aspect Ratio
	function calculateAspectRatio() {
		if ($this->pluginRegistry->doCrop){
			switch ($this->pluginRegistry->changeAspectRatio) {
				case "0":$this->pluginRegistry->aspectRatio=(16/9);
						break;
				case "1":$this->pluginRegistry->aspectRatio=(4/3);
						break;
				case "2":$this->pluginRegistry->aspectRatio=1;
						break;
				case "3":$this->pluginRegistry->aspectRatio= $this->pluginRegistry->imagedata[0]/$this->pluginRegistry->imagedata[1];
						break;
			}
		}else{
			if ($this->pluginRegistry->maxThumbSize=="width")
				$this->pluginRegistry->aspectRatio= $this->pluginRegistry->imagedata[0]/$this->pluginRegistry->imagedata[1];
			else
				$this->pluginRegistry->aspectRatio= $this->pluginRegistry->imagedata[1]/$this->pluginRegistry->imagedata[0];
		}
	}
	//Crop Area
	function CalculateCropArea() {
		$this->pluginRegistry->cropX = 0;
		$this->pluginRegistry->cropY = 0;
		$this->pluginRegistry->cropWidth = 0;
		$this->pluginRegistry->cropHeight= 0;
		//Max crop Area by width
		if ($this->pluginRegistry->maxThumbSize=="width") {
			while (($this->pluginRegistry->cropWidth<$this->pluginRegistry->imagedata[0])&&($this->pluginRegistry->cropHeight<$this->pluginRegistry->imagedata[1])) {
				$this->pluginRegistry->cropWidth = $this->pluginRegistry->cropWidth+1;
				$this->pluginRegistry->cropHeight = (int)($this->pluginRegistry->cropWidth/$this->pluginRegistry->aspectRatio);
			}
		//Max crop Area by height
		}else{
			while (($this->pluginRegistry->cropWidth<$this->pluginRegistry->imagedata[0])&&($this->pluginRegistry->cropHeight<$this->pluginRegistry->imagedata[1])) {
				$this->pluginRegistry->cropHeight = $this->pluginRegistry->cropHeight+1;
				$this->pluginRegistry->cropWidth = (int)($this->pluginRegistry->cropHeight/$this->pluginRegistry->aspectRatio);
			}
		}
		//Crop Area
		switch ($this->pluginRegistry->cropArea){
			//Center
			case "6":	$this->pluginRegistry->cropX=(int)(($this->pluginRegistry->imagedata[0]-$this->pluginRegistry->cropWidth)/2);
						$this->pluginRegistry->cropY=(int)(($this->pluginRegistry->imagedata[1]-$this->pluginRegistry->cropHeight)/2);
						break;
			//Top Center
			case "5":	$this->pluginRegistry->cropX=(int)(($this->pluginRegistry->imagedata[0]-$this->pluginRegistry->cropWidth)/2);
						$this->pluginRegistry->cropY=0;
						break;
			//Top Left
			case "4":	$this->pluginRegistry->cropX=0;
						$this->pluginRegistry->cropY=0;
						break;
			//Top Right
			case "3":	$this->pluginRegistry->cropX=($this->pluginRegistry->imagedata[0]-$this->pluginRegistry->cropWidth);
						$this->pluginRegistry->cropY=0;
						break;
			//Bottom Center
			case "2":	$this->pluginRegistry->cropX=0;
						$this->pluginRegistry->cropY=(int)(($this->pluginRegistry->imagedata[1]-$this->pluginRegistry->cropHeight)/2);
						break;
			//Bottom Left
			case "1":	$this->pluginRegistry->cropX=0;
						$this->pluginRegistry->cropY=($this->pluginRegistry->imagedata[1]-$this->pluginRegistry->cropHeight);
						break;
			//Bottom Right
			case "0":	$this->pluginRegistry->cropX=($this->pluginRegistry->imagedata[0]-$this->pluginRegistry->cropWidth);
						$this->pluginRegistry->cropY=($this->pluginRegistry->imagedata[1]-$this->pluginRegistry->cropHeight);
						break;
		}
	}
	// Get atributes from img tag
	function getImageTags($text) {

		//local or external paths
		if (preg_match('#\s*src="(.*?)"#s',$text,$this->pluginRegistry->getinfo))
			$this->pluginRegistry->source=$this->pluginRegistry->getinfo[1];
		else
			$this->pluginRegistry->source="";
		
		if ((preg_match('#http://#s',$text,$protocol))&&($protocol[0]=='http://')){
			$this->pluginRegistry->is_external_image=true;
			$this->pluginRegistry->full_image_path = $this->pluginRegistry->source;
		}else{
			$this->pluginRegistry->is_external_image=false;
			$this->pluginRegistry->full_image_path = JPATH_SITE.'/'.$this->pluginRegistry->source;
			$this->pluginRegistry->full_image_path = str_replace('%20', ' ',$this->pluginRegistry->full_image_path );
		}
		//description
		$this->pluginRegistry->desc="";
		if (preg_match('#\s*alt=\"(.*?)\"#s',$text,$this->pluginRegistry->getinfo))
			$this->pluginRegistry->desc=$this->pluginRegistry->getinfo[1];
		//title
		$this->pluginRegistry->title="";
		if (preg_match('#\s*title=\"(.*?)\"#s',$text,$this->pluginRegistry->getinfo))
			$this->pluginRegistry->title=$this->pluginRegistry->getinfo[1];
		//Resize image
		$this->pluginRegistry->thumbHeight="";
		$this->pluginRegistry->thumbWidth="";
		if ($this->pluginRegistry->resizeImage=="0") {
			//width
			if (preg_match('#\s*width=\"(.*?)\"#s',$text,$this->pluginRegistry->getinfo))
				$this->pluginRegistry->thumbWidth=$this->pluginRegistry->getinfo[1];
			//height
			if (preg_match('#\s*height=\"(.*?)\"#s',$text,$this->pluginRegistry->getinfo))
				$this->pluginRegistry->thumbHeight=$this->pluginRegistry->getinfo[1];
		}
		//align
		$this->pluginRegistry->align="";
		if (preg_match('#\s*align=\"(.*?)\"#s',$text,$this->pluginRegistry->getinfo))
			$this->pluginRegistry->align=$this->pluginRegistry->getinfo[1];
		//border
		$this->pluginRegistry->border="";
		if (preg_match('#\s*border=\"(.*?)\"#s',$text,$this->pluginRegistry->getinfo))
			$this->pluginRegistry->border=$this->pluginRegistry->getinfo[1];
		//hspace
		$this->pluginRegistry->hspace="";
		if (preg_match('#\s*hspace=\"(.*?)\"#s',$text,$this->pluginRegistry->getinfo))
			$this->pluginRegistry->hspace=$this->pluginRegistry->getinfo[1];
		//longdesc
		$this->pluginRegistry->longdesc="";
		if (preg_match('#\s*longdesc=\"(.*?)\"#s',$text,$this->pluginRegistry->getinfo))
			$this->pluginRegistry->longdesc=$this->pluginRegistry->getinfo[1];
		//usemap
		$this->pluginRegistry->usemap="";
		if (preg_match('#\s*usemap=\"(.*?)\"#s',$text,$this->pluginRegistry->getinfo))
			$this->pluginRegistry->usemap=$this->pluginRegistry->getinfo[1];
		//vspace
		$this->pluginRegistry->vspace="";
		if (preg_match('#\s*vspace=\"(.*?)\"#s',$text,$this->pluginRegistry->getinfo))
			$this->pluginRegistry->vspace=$this->pluginRegistry->getinfo[1];
		//id
		$this->pluginRegistry->id="";
		if (preg_match('#\s*id=\"(.*?)\"#s',$text,$this->pluginRegistry->getinfo)){
			$this->pluginRegistry->id=$this->pluginRegistry->getinfo[1];
		}
		//style
		$this->pluginRegistry->style="";
		if ((preg_match('#\s*style=\"(.*?)\"#s',$text,$this->pluginRegistry->style))&&($this->pluginRegistry->style[1])) {
			if (preg_match('#\s*(width:\s*\d*\s*px;\s*height:\s*\d*\s*px;)#s',$this->pluginRegistry->style[1],$this->pluginRegistry->styleWHFull)) {
				if (($this->pluginRegistry->styleWHFull[1])&&($this->pluginRegistry->thumbHeight=="")&&($this->pluginRegistry->thumbWidth=="")){
					preg_match('#width:\s*(\d*)\s*px;\s*height:\s*(\d*)\s*px;#s',$this->pluginRegistry->styleWHFull[1],$this->pluginRegistry->styleWH);
					$this->pluginRegistry->thumbWidth=(int)$this->pluginRegistry->styleWH[1];
					$this->pluginRegistry->thumbHeight=(int)$this->pluginRegistry->styleWH[2];
					$finalStyle=str_replace($this->pluginRegistry->styleWHFull[1],"",$this->pluginRegistry->style[1]);
				}else{
					$finalStyle=$this->pluginRegistry->style[1];
				}
			}
			$this->pluginRegistry->style=$finalStyle;
		}
	}

	//Return 1 when image can be opened
	function Can_open_image($match)
	{
		//is external server image
		if ($this->pluginRegistry->is_external_image){
			$AgetHeaders = @get_headers($this->pluginRegistry->full_image_path);
			if (!preg_match("|200|", $AgetHeaders[0])) {
				if ($this->pluginRegistry->showErrors=="1"){
					$html_entities_match = array( "|\<br \/\>|", "#<#", "#>#", "|&#39;|", '#&quot;#', '#&nbsp;#' );
					$html_entities_replace = array( "\n", '&lt;', '&gt;', "'", '"', ' ' );
					$text = preg_replace( $html_entities_match, $html_entities_replace, $match );
					echo '<br>'."JoomSlide error: Invalid image src: ".$text.". Server error: ".$AgetHeaders[0]."</br>";
				}
				if ($this->pluginRegistry->useErrorImage=="1"){
					$this->pluginRegistry->source=$this->pluginRegistry->pathErrorImage;
					$this->pluginRegistry->full_image_path=JPATH_SITE.'/'.$this->pluginRegistry->source;
				}else{
					return 0;
				}
			}
		//is local server image
		}elseif (!file_exists ($this->pluginRegistry->full_image_path)){
			if ($this->pluginRegistry->showErrors=="1"){
				$html_entities_match = array( "|\<br \/\>|", "#<#", "#>#", "|&#39;|", '#&quot;#', '#&nbsp;#' );
				$html_entities_replace = array( "\n", '&lt;', '&gt;', "'", '"', ' ' );
				$text = preg_replace( $html_entities_match, $html_entities_replace, $match );
				echo '<br>'."JoomSlide error: Invalid image src: ".$text."</br>";
			}
			if ($this->pluginRegistry->useErrorImage=="0"){
				$this->pluginRegistry->source=$this->pluginRegistry->pathErrorImage;
				$this->pluginRegistry->full_image_path=JPATH_SITE.'/'.$this->pluginRegistry->source;
			}else{
				return 0;
			}
		}
		return 1;
	}
}

?>