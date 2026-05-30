<?php
/**
 * Plugin Helper File
 *
 * @package     Sourcerer
 * @version     2.4.3
 *
 * @author      Peter van Westen <peter@nonumber.nl>
 * @link        http://www.nonumber.nl
 * @copyright   Copyright (C) 2010 NoNumber! All Rights Reserved
 * @license     http://www.gnu.org/licenses/gpl-2.0.html GNU/GPL
 */

// No direct access
defined( '_JEXEC' ) or die( 'Restricted access' );

/**
* Plugin that replaces Sourcerer code with its HTML / CSS / JavaScript / PHP equivalent
*/
class plgSystemSourcererHelper
{
	function init( &$params ) {
		$this->params = plgSystemSourcererHelper::getParamValues( $params );
		plgSystemSourcererHelper::setExtraParams();
	}

	function setExtraParams()
	{
		// Set plugin parameters
		$this->src_params = '';

		$this->src_params->syntax_word =		$this->params->syntax_word;
		$this->src_params->syntax_start =		'{'.$this->src_params->syntax_word.'}';
		$this->src_params->syntax_start_0 =		'{'.$this->src_params->syntax_word.' 0}';
		$this->src_params->syntax_end =			'{/'.$this->src_params->syntax_word.'}';

		// Matches the start and end tags with everything in between
		// Also matches any surrounding breaks and paragraph tags, to prevent unwanted empty lines in output.
		$break_tags_start =			'(<p(?: [^>]*)?>\s*)?(?:<span [^>]*>\s*)*';
		$break_tags_end =			'(?:\s*</span>)*(\s*</p>)?';
		$this->src_params->regex =	'#('.$break_tags_start.'('.preg_quote( $this->src_params->syntax_start ).'|'.preg_quote( $this->src_params->syntax_start_0 ).')(.*?)'.preg_quote( $this->src_params->syntax_end ).$break_tags_end.')#s';

		// Escape any regex caracters!
		$this->src_params->tags_syntax =	array ( array( '<', '>' ), array( '\[\[', '\]\]' ) );
		$this->src_params->splitter =		'<!-- START: SRC_SPLIT -->';

		$this->src_params->debug_php =		$this->params->debug_php;
		$this->src_params->debug_php_article = $this->src_params->debug_php;
		$this->src_params->user_is_admin =	0;
		$user = JFactory::getUser();
		if ( $user->usertype == 'Super Administrator' || $user->usertype == 'Administrator' ) {
			$this->src_params->user_is_admin = 1;
		}

		$this->src_params->areas = array();
		$this->src_params->areas['default'] = array();
		$this->src_params->areas['default']['enable_css'] =				$this->params->enable_css;
		$this->src_params->areas['default']['enable_js'] =				$this->params->enable_js;
		$this->src_params->areas['default']['enable_php'] =				$this->params->enable_php;
		$this->src_params->areas['default']['forbidden_php'] =			$this->params->forbidden_php;
		$this->src_params->areas['default']['forbidden_tags'] =			$this->params->forbidden_tags;

		$this->src_params->areas['articles'] = $this->src_params->areas['default'];
		$this->src_params->areas['articles']['enable'] =				$this->params->articles_enable;
		$this->src_params->areas['articles']['enable_css'] =			$this->params->articles_enable_css;
		$this->src_params->areas['articles']['enable_js'] =				$this->params->articles_enable_js;
		$this->src_params->areas['articles']['enable_php'] =			$this->params->articles_enable_php;
		$this->src_params->areas['articles']['forbidden_php'] =			$this->src_params->areas['default']['forbidden_php'].','.$this->params->articles_forbidden_php;
		$this->src_params->areas['articles']['forbidden_tags'] =		$this->src_params->areas['default']['forbidden_tags'].','.$this->params->articles_forbidden_tags;

			$security_group =		$this->params->articles_security_level;
			$security_group_css =	$this->params->articles_security_level_css;
			$security_group_js =	$this->params->articles_security_level_js;
			$security_group_php =	$this->params->articles_security_level_php;

			$acl =& JFactory::getACL();
			$acls = array();
			if ( !isset( $acls[$security_group] ) ) {
				$acls[$security_group] = $acl->get_group_data( $security_group );
				$acls[$security_group] = $acls[$security_group]['4'];
			}
			if ( !isset( $acls[$security_group_css] ) ) {
				$acls[$security_group_css] = $acl->get_group_data( $security_group_css );
				$acls[$security_group_css] = $acls[$security_group_css]['4'];
			}
			if ( !isset( $acls[$security_group_js] ) ) {
				$acls[$security_group_js] = $acl->get_group_data( $security_group_js );
				$acls[$security_group_js] = $acls[$security_group_js]['4'];
			}
			if ( !isset( $acls[$security_group_php] ) ) {
				$acls[$security_group_php] = $acl->get_group_data( $security_group_php );
				$acls[$security_group_php] = $acls[$security_group_php]['4'];
			}
			$this->src_params->areas['articles']['security'] =		$acls[$security_group];
			$this->src_params->areas['articles']['security_css'] =	$acls[$security_group_css];
			$this->src_params->areas['articles']['security_js'] =	$acls[$security_group_js];
			$this->src_params->areas['articles']['security_php'] =	$acls[$security_group_php];
			$this->src_params->acls = $acls;

		$this->src_params->areas['components'] = $this->src_params->areas['default'];
		$this->src_params->areas['components']['enable'] =				$this->params->components_enable;
		$this->src_params->areas['components']['components'] =			$this->params->components;
		if ( !is_array( $this->src_params->areas['components']['components'] ) ) {
			$this->src_params->areas['components']['components'] = explode( ',', $this->src_params->areas['components']['components'] );
		}
		$this->src_params->areas['components']['enable_css'] =			$this->params->components_enable_css;
		$this->src_params->areas['components']['enable_js'] =			$this->params->components_enable_js;
		$this->src_params->areas['components']['enable_php'] =			$this->params->components_enable_php;
		$this->src_params->areas['components']['forbidden_php'] =		$this->src_params->areas['default']['forbidden_php'].','.$this->params->components_forbidden_php;
		$this->src_params->areas['components']['forbidden_tags'] =		$this->src_params->areas['default']['forbidden_tags'].','.$this->params->components_forbidden_tags;

		$this->src_params->areas['other'] = $this->src_params->areas['default'];
		$this->src_params->areas['other']['enable'] =					$this->params->other_enable;
		$this->src_params->areas['other']['enable_css'] =				$this->params->other_enable_css;
		$this->src_params->areas['other']['enable_js'] =				$this->params->other_enable_js;
		$this->src_params->areas['other']['enable_php'] =				$this->params->other_enable_php;
		$this->src_params->areas['other']['forbidden_php'] =			$this->src_params->areas['default']['forbidden_php'].','.$this->params->other_forbidden_php;
		$this->src_params->areas['other']['forbidden_tags'] =			$this->src_params->areas['default']['forbidden_tags'].','.$this->params->other_forbidden_tags;

		foreach ( $this->src_params->areas as $areaname => $area ) {
			if ( $area['enable_css'] == -1 )	$this->src_params->areas[$areaname]['enable_css'] =		$this->src_params->areas['default']['enable_css'];
			if ( $area['enable_js'] == -1 )		$this->src_params->areas[$areaname]['enable_js'] =		$this->src_params->areas['default']['enable_js'];
			if ( $area['enable_php'] == -1 )	$this->src_params->areas[$areaname]['enable_php'] =		$this->src_params->areas['default']['enable_php'];
		}

		$this->src_params->currentarea = 'default';
	}

////////////////////////////////////////////////////////////////////
// ARTICLES
////////////////////////////////////////////////////////////////////

	function replaceInArticles ( &$article, $params = '' ) {
		if ( is_string( $params ) && $params == 'search' ) {
			$this->src_params->debug_php_article = 0;
		}
		if ( isset( $article->created_by ) ) {
			if ( !isset( $this->src_params->acls[$article->created_by] ) ) {
				$acl =& JFactory::getACL();
				$this->src_params->acls[$article->created_by] = $acl->getAroGroup( $article->created_by );
			}
			$article_group = $this->src_params->acls[$article->created_by];

			if ( !isset( $article_group->lft ) ) {
				$article_group->lft = 0;
			}

			// Set if security is passed
			// passed = creator is equal or higher than security group level
			$this->src_params->areas['articles']['security_pass'] =			( $this->src_params->areas['articles']['security']		<= $article_group->lft ) ? 1 : 0;
			$this->src_params->areas['articles']['security_pass_css'] =		( $this->src_params->areas['articles']['security_css']	<= $article_group->lft ) ? 1 : 0;
			$this->src_params->areas['articles']['security_pass_js'] =		( $this->src_params->areas['articles']['security_js']	<= $article_group->lft ) ? 1 : 0;
			$this->src_params->areas['articles']['security_pass_php'] =		( $this->src_params->areas['articles']['security_php']	<= $article_group->lft ) ? 1 : 0;

		}

		if ( isset( $article->text ) ) {
			$this->replace( $article->text, 'articles', $article );
		}
		if ( isset( $article->description ) ) {
			$this->replace( $article->description, 'articles', $article );
		}
		if ( isset( $article->title ) ) {
			$this->replace( $article->title, 'articles', $article );
		}
		if ( isset( $article->author ) ) {
			if ( isset( $article->author->name ) ) {
				$this->replace( $article->author->name, 'articles', $article );
			} else if ( is_string( $article->author ) ) {
				$this->replace( $article->author, 'articles', $article );
			}
		}
	}

////////////////////////////////////////////////////////////////////
// COMPONENTS
////////////////////////////////////////////////////////////////////

	function replaceInComponents()
	{
		$document	=& JFactory::getDocument();
		$docType = $document->getType();

		// FEED
		if ( $docType == 'feed' && isset( $document->items ) ) {
			for ( $i = 0; $i < count( $document->items ); $i++ ) {
				$this->replaceInArticles( $document->items[$i] );
			}
		}

		if ( isset( $document->_buffer ) ) {
			$this->tagArea( $document->_buffer, 'component' );
		}

		// PDF
		if ( $docType == 'pdf' ) {
			if ( isset( $document->_header ) ) {
				$this->replaceInTheRest( $document->_header );
				$this->cleanLeftoverJunk( $document->_header );
			}
			if ( isset( $document->title ) ) {
				$this->replaceInTheRest( $document->title );
				$this->cleanLeftoverJunk( $document->title );
			}
			if ( isset( $document->_buffer ) ) {
				$this->replaceInTheRest( $document->_buffer );
				$this->cleanLeftoverJunk( $document->_buffer );
			}
		}
	}

////////////////////////////////////////////////////////////////////
// OTHER AREAS
////////////////////////////////////////////////////////////////////
	function replaceInOtherAreas()
	{
		$document =& JFactory::getDocument();
		$docType = $document->getType();

		// not in pdf's
		if ( $docType == 'pdf' ) { return; }

		$html = JResponse::getBody();

		$this->protect( $html );
		$this->replaceInTheRest( $html );
		$this->unprotect( $html );

		$this->cleanLeftoverJunk( $html );

		unset( $this->src_params );

		JResponse::setBody( $html );
	}

	function replaceInTheRest( &$str, $docType = 'html' )
	{
		global $option;

		if ( $str == '' ) { return; }

		$document	=& JFactory::getDocument();
		$docType = $document->getType();

		// COMPONENT
		if ( $docType == 'feed' ) {
			$search_regex = '#(<item[^>]*>.*</item>)#si';
			$str = preg_replace( $search_regex, '<!-- START: SRC_COMPONENT -->\1<!-- END: SRC_COMPONENT -->', $str );
		}
		if ( strpos( $str, '<!-- START: SRC_COMPONENT -->' ) === false ) {
			$this->tagArea( $str, 'component' );
		}

		if ( in_array( $option, $this->src_params->areas['components']['components'] ) ) {
			// For all components that are selected, set the 'enable' to false
			$this->src_params->areas['components']['enable'] = $this->src_params->areas['components']['enable_css'] = $this->src_params->areas['components']['enable_js'] = $this->src_params->areas['components']['enable_php'] = 0;
		}

		$components = $this->getTagArea( $str, 'component' );
		foreach ( $components as $component ) {
			$this->replace( $component['1'], 'components', '' );
			$str = str_replace( $component['0'], $component['1'], $str );
		}

		// EVERYWHERE
		$this->replace( $str, 'other' );
	}

	function tagArea( &$str, $area = '' )
	{
		if ( $area ) {
			if ( is_array( $str ) ) {
				foreach ( $str as $key => $val ) {
					$this->tagArea( $val, $area );
					$str[ $key ] = $val;
				}
			} else if ( $str ) {
				$str = '<!-- START: SRC_'.strtoupper( $area ).' -->'.$str.'<!-- END: SRC_'.strtoupper( $area ).' -->';
			}
		}
	}

	function getTagArea( $str, $area = '' )
	{
		$matches = array( '', '' );

		if ( $str && $area ) {
			preg_match_all( '#<\!-- START: SRC_'.strtoupper( $area ).' -->(.*?)<\!-- END: SRC_'.strtoupper( $area ).' -->#s', $str, $matches, PREG_SET_ORDER );
		}

		return $matches;
	}


	function replace( &$string, $area = 'articles', $article = '' ) {
		$string_array = $this->stringToSplitArray( $string, $this->src_params->regex );
		$string_array_count = count( $string_array );
		if ( $string_array_count > 1 ) {
			for ( $i = 1; $i < $string_array_count-1; $i++ ) {
				if ( fmod( $i, 2 ) ) {
					$sub_string_array = preg_replace( $this->src_params->regex, implode( $this->src_params->splitter, array( '\2', '\3', '\4', '\5' ) ), $string_array[$i] );
					$sub_string_array = explode( $this->src_params->splitter, $sub_string_array );
					$string_array[$i] = $sub_string_array['2'];

					if ( $sub_string_array['1'] == $this->src_params->syntax_start ) {
						$this->cleanText( $string_array[$i] );
					}

					$this->replaceTags( $string_array[$i], $area, $article );

					// Restore leading/trailing paragraph tags if not both present
					if ( !( $sub_string_array['0'] && $sub_string_array['3'] ) ) {
						$string_array[$i] = $sub_string_array['0'].$string_array[$i].$sub_string_array['3'];
					}
				}
			}
		}
		$string = implode( '', $string_array );
	}

	function replaceTags( &$string, $area = 'articles', $article = '' ) {
		$this->replaceTagsByType( $string, $area, 'php', $article );
		if ( strpos( $string, '<!-- SORCERER DEBUGGING -->' ) === false ) {
			$this->replaceTagsByType( $string, $area, 'all', '' );
			$this->replaceTagsByType( $string, $area, 'js', '' );
			$this->replaceTagsByType( $string, $area, 'css', '' );
		}
	}

	function replaceTagsByType( &$string, $area = 'articles', $type = 'all', $article = '' ) {
		$type_ext = '_'.$type;
		if ( $type == 'all' ) {
			$type_ext = '';
		}
		$enable = isset( $this->src_params->areas[$area]['enable'.$type_ext] ) ? $this->src_params->areas[$area]['enable'.$type_ext] : 1;
		$security_pass = isset( $this->src_params->areas[$area]['security_pass'.$type_ext] ) ? $this->src_params->areas[$area]['security_pass'.$type_ext] : 1;

		switch ( $type ) {
			case 'php':
				$this->replaceTagsPHP( $string, $enable, $security_pass, $article );
				break;
			case 'js':
				$this->replaceTagsJS( $string, $enable, $security_pass );
				break;
			case 'css':
				$this->replaceTagsCSS( $string, $enable, $security_pass );
				break;
			default:
				$this->replaceTagsAll( $string, $enable, $security_pass );
				break;
		}
	}

	// Replace any html style tags by a comment tag if not permitted
	// Match:
	// <...>
	function replaceTagsAll( &$string, $enabled = 1, $security_pass = 1 ) {
		if ( !$enabled ) {
			// replace source block content with HTML comment
			$string = '<!-- '.JText::_( 'Comment - Sourcerer' ).': '.JText::_( 'REMOVED ALL, NOT ENABLED' ).' -->';
		} else if ( !$security_pass ) {
			// replace source block content with HTML comment
			$string = '<!-- '.JText::_( 'Comment - Sourcerer' ).': '.JText::_( 'REMOVED ALL, SECURITY' ).' -->';
		} else {
			$this->cleanTags( $string );

			$forbidden_tags_array = explode( ',', $this->src_params->areas[$this->src_params->currentarea]['forbidden_tags'] );
			$this->cleanArray( $forbidden_tags_array );
			// remove the comment tag syntax from the array - they cannot be disabled
			$forbidden_tags_array = array_diff( $forbidden_tags_array, array( '!--' ) );
			// reindex the array
			$forbidden_tags_array = array_merge( $forbidden_tags_array );

			$has_forbidden_tags = 0;
			foreach ( $forbidden_tags_array as $forbidden_tag ) {
				if ( !( strpos( $string, '<'.$forbidden_tag ) == false ) ) {
					$has_forbidden_tags = 1;
					break;
				}
			}

			if ( $has_forbidden_tags ) {
				// double tags
				$tag_regex = '#<\s*([a-z\!][^>\s]*?)(?:\s+.*?)?>.*?</\1>#si';
				if ( preg_match_all( $tag_regex, $string, $matches, PREG_SET_ORDER ) > 0 ) {
					foreach ( $matches as $match ) {
						if ( in_array( $match['1'], $forbidden_tags_array ) ) {
							$tag = '<!-- '.JText::_( 'Comment - Sourcerer' ).': '.JText::sprintf( 'REMOVED TAG, FORBIDDEN', $match['1'] ).' -->';
							$string = str_replace( $match['0'], $tag, $string );
						}
					}
				}
				// single tags
				$tag_regex = '#<\s*([a-z\!][^>\s]*?)(?:\s+.*?)?>#si';
				if ( preg_match_all( $tag_regex, $string, $matches, PREG_SET_ORDER ) > 0 ) {
					foreach ( $matches as $match ) {
						if ( in_array( $match['1'], $forbidden_tags_array ) ) {
							$tag = '<!-- '.JText::_( 'Comment - Sourcerer' ).': '.JText::sprintf( 'REMOVED TAG, FORBIDDEN', $match['1'] ).' -->';
							$string = str_replace( $match['0'], $tag, $string );
						}
					}
				}
			}
		}
	}
	// Replace the PHP tags with the evaluated PHP scripts
	// Or replace by a comment tag the PHP tags if not permitted
	function replaceTagsPHP( &$src_string, $src_enabled = 1, $src_security_pass = 1, $article = '' ) {
		if ( ( strpos( $src_string, '<?' ) === false ) && ( strpos( $src_string, '[[?' ) === false ) ) { return; }

		global $src_vars;

		$document	=& JFactory::getDocument();
		$docType = $document->getType();

		// Match ( read {} as <> ):
		// {?php ... ?}
		// {? ... ?}
		$src_string_array = $this->stringToSplitArray( $src_string, '-start-'.'\?(?:php)?[\s<](.*?)\?'.'-end-', 1 );
		$src_string_array_count = count( $src_string_array );

		if ( $src_string_array_count > 1 ) {
			if ( !$src_enabled ) {
				// replace source block content with HTML comment
				$src_string_array = array();
				$src_string_array['0'] = '<!-- '.JText::_( 'Comment - Sourcerer' ).': '.JText::sprintf( 'REMOVED, NOT ALLOWED', JText::_( 'PHP' ), JText::_( 'PHP' ) ).' -->';
			} else if ( !$src_security_pass ) {
				// replace source block content with HTML comment
				$src_string_array = array();
				$src_string_array['0'] = '<!-- '.JText::_( 'Comment - Sourcerer' ).': '.JText::sprintf( 'REMOVED, SECURUITY', JText::_( 'PHP' ), JText::_( 'PHP' ) ).' -->';
			} else {
				// if source block content has more than 1 php block, combine them
				if ( $src_string_array_count > 3 ) {
					for ( $i = 2; $i < $src_string_array_count-1; $i++ ) {
						if ( fmod( $i, 2 ) == 0 ) {
							$src_string_array['1'] .= " ?>\n".trim( $src_string_array[$i] )."\n<?php ";
						} else {
							$src_string_array['1'] .= $src_string_array[$i];
						}
						unset( $src_string_array[$i] );
					}
				}

				// fixes problem with _REQUEST being stripped if there is an error in the code
				$src_backup_REQUEST = $_REQUEST;
				$src_backup_vars = array_keys( get_defined_vars() );

				$src_script = trim( $src_string_array['1'] );

				$src_comment = '';
				$src_errorline = 0;
				$src_php_succes = 0;

				$src_forbidden_php_array = explode( ',', $this->src_params->areas[$this->src_params->currentarea]['forbidden_php'] );
				$this->cleanArray( $src_forbidden_php_array );
				$src_forbidden_php_regex = '#('.implode( '|', $src_forbidden_php_array ).')\s*\(#si';

				if ( preg_match_all( $src_forbidden_php_regex, $src_script, $src_functions, PREG_SET_ORDER ) > 0 ) {
					$src_functionsArray = array();
					foreach ( $src_functions as $src_function ) $src_functionsArray[] = $src_function['1'].')';
					$src_string_array['1'] = JText::_( 'PHP FORBIDDEN' ).':<br /><span style="font-family: monospace;"><ul style="margin:0px;"><li>'.implode( '</li><li>', $src_functionsArray ).'</li></ul></span>';
					$src_comment = JText::_( 'REMOVED PHP, FORBIDDEN' ).': ( '.implode( ', ', $src_functionsArray ).' )';
				} else {
					// evaluate the script
					ob_start();
						if ( is_array( $src_vars ) ) {
							foreach ( $src_vars as $src_key=>$src_value ) {
								${$src_key} = $src_value;
							}
						}
						if ( !isset( $mainframe ) && !( strpos( $src_script, '$mainframe' ) === false ) ) {
							global $mainframe;
						}
						if ( !isset( $Itemid ) && !( strpos( $src_script, '$Itemid' ) === false ) ) {
							global $Itemid;
						}
						if ( !isset( $user ) && !( strpos( $src_script, '$user' ) === false ) ) {
							$user =& JFactory::getUser();
						}
						if ( !isset( $database ) && !( strpos( $src_script, '$database' ) === false ) ) {
							$database =& JFactory::getDBO();
						}
						$src_script .= "\n".'$src_php_succes = 1;';
						eval( $src_script );
						$src_string_array['1'] = ob_get_contents();
					ob_end_clean();
					if ( !( strpos( $src_string_array['1'], "eval()'d code" ) === false ) ) {
						foreach ( $src_backup_REQUEST as $src_key=>$src_value ) {
							$_REQUEST[$src_key] = $src_value;
						}
						$src_php_succes = 0;
						preg_match( '#on line <b>([0-9]+)#si', $src_string_array['1'], $src_errormatch );
						if ( count( $src_errormatch ) ) $src_errorline = $src_errormatch['1'];
					}

					$src_comment = JText::_( 'REMOVED PHP, ERRORS' );
				}

				if ( !$src_php_succes ) {
					if ( $docType == 'html' ) {
						if ( ( $this->src_params->debug_php && !$article ) || ( $this->src_params->debug_php_article && $article ) ) {
							if ( $this->src_params->user_is_admin ) {
								$this->createDebuggingOutput( $src_string_array['1'], $src_script, $src_errorline );
							} else {
								$src_string_array['1'] = '<!-- '.JText::_( 'Comment - Sourcerer' ).': '.$src_comment.' '.JText::_( 'Login to show PHP Debugging' ).' -->';
							}
						} else {
							$src_string_array['1'] = '<!-- '.JText::_( 'Comment - Sourcerer' ).': '.$src_comment.' -->';
						}
					} else {
						$src_string_array['1'] = '';
					}
				} else {
					$src_new_vars = get_defined_vars();
					$src_diff_vars = array_diff( array_keys( $src_new_vars ), $src_backup_vars );
					foreach ( $src_diff_vars as $src_diff_key ) {
						if ( substr( $src_diff_key, 0, 5 ) != '_src_' && substr( $src_diff_key, 0, 4 ) != 'src_' ) {
							$src_vars[$src_diff_key] = $src_new_vars[$src_diff_key];
						}
					}
				}
			}
		}
		$src_string = implode( '', $src_string_array );
	}

	// Replace the JavaScript tags by a comment tag if not permitted
	function replaceTagsJS( &$string, $enabled = 1, $security_pass = 1 ) {
		// quick check to see if i is necessary to do anything
		if ( ( strpos( $string, 'script' ) === false ) ) { return; }

		// Match:
		// <script ...>...</script>
		$tag_regex =
			'(-start-'.'\s*script\s[^'.'-end-'.']*?[^/]\s*'.'-end-'
			.'(.*?)'
			.'-start-'.'\s*\/\s*script\s*'.'-end-)'
			;
		$string_array = $this->stringToSplitArray( $string, $tag_regex, 1 );
		$string_array_count = count( $string_array );

		// Match:
		// <script ...>
		// single script tags are not xhtml compliant and should not occur, but just incase they do...
		if ( $string_array_count == 1 ) {
			$tag_regex = '(-start-'.'\s*script\s.*?'.'-end-)';
			$string_array = $this->stringToSplitArray( $string, $tag_regex, 1 );
			$string_array_count = count( $string_array );
		}

		if ( $string_array_count > 1 ) {
			if ( !$enabled ) {
				// replace source block content with HTML comment
				$string = '<!-- '.JText::_( 'Comment - Sourcerer' ).': '.JText::sprintf( 'REMOVED, NOT ALLOWED', array( JText::_( 'JavaScript' ) ), array( JText::_( 'JavaScript' ) ) ).' -->';
			} else if ( !$security_pass ) {
				// replace source block content with HTML comment
				$string = '<!-- '.JText::_( 'Comment - Sourcerer' ).': '.JText::sprintf( 'REMOVED, SECURUITY', array( JText::_( 'JavaScript' ) ), array( JText::_( 'JavaScript' ) ) ).' -->';
			}
		}
	}

	// Replace the CSS tags by a comment tag if not permitted
	function replaceTagsCSS( &$string, $enabled = 1, $security_pass = 1 ) {
		// quick check to see if i is necessary to do anything
		if ( ( strpos( $string, 'style' ) === false ) && ( strpos( $string, 'link' ) === false ) ) { return; }

		// Match:
		// <script ...>...</script>
		$tag_regex =
			'(-start-'.'\s*style\s[^'.'-end-'.']*?[^/]\s*'.'-end-'
			.'(.*?)'
			.'-start-'.'\s*\/\s*style\s*'.'-end-)'
			;
		$string_array = $this->stringToSplitArray( $string, $tag_regex, 1 );
		$string_array_count = count( $string_array );

		// Match:
		// <script ...>
		// single script tags are not xhtml compliant and should not occur, but just incase they do...
		if ( $string_array_count == 1 ) {
			$tag_regex = '(-start-'.'\s*link\s[^'.'-end-'.']*?(rel="stylesheet"|type="text/css").*?'.'-end-)';
			$string_array = $this->stringToSplitArray( $string, $tag_regex, 1 );
			$string_array_count = count( $string_array );
		}

		if ( $string_array_count > 1 ) {
			if ( !$enabled ) {
				// replace source block content with HTML comment
				$string = '<!-- '.JText::_( 'Comment - Sourcerer' ).': '.JText::sprintf( 'REMOVED, NOT ALLOWED', array( JText::_( 'CSS' ) ), array( JText::_( 'CSS' ) ) ).' -->';
			} else if ( !$security_pass ) {
				// replace source block content with HTML comment
				$string = '<!-- '.JText::_( 'Comment - Sourcerer' ).': '.JText::sprintf( 'REMOVED, SECURUITY', array( JText::_( 'CSS' ) ), array( JText::_( 'CSS' ) ) ).' -->';
			}
		}
	}

	function stringToSplitArray( $string, $search, $tags = 0 ) {
		if ( $tags) {
			foreach ( $this->src_params->tags_syntax as $src_tag_syntax ) {
				$tag_search = str_replace( '-start-', $src_tag_syntax['0'], $search );
				$tag_search = str_replace( '-end-', $src_tag_syntax['1'], $tag_search );
				$tag_search = '#'.$tag_search.'#si';
				$string = preg_replace( $tag_search, $this->src_params->splitter.'\1'.$this->src_params->splitter, $string );
			}
		} else {
			$string = preg_replace( $search, $this->src_params->splitter.'\1'.$this->src_params->splitter, $string );
		}
		return explode( $this->src_params->splitter, $string );
	}

	function cleanTags( &$string ) {
		foreach ( $this->src_params->tags_syntax as $src_tag_syntax ) {
			$tag_regex = '#'.$src_tag_syntax['0'].'\s*(\/?\s*[a-z\!][^'.$src_tag_syntax['1'].']*?(?:\s+.*?)?)'.$src_tag_syntax['1'].'#si';
			$string = preg_replace( $tag_regex, '<\1\2>', $string );
		}
	}

	function cleanArray( &$array ) {
		// trim all values
		$array = array_map( 'trim', $array );
		// remove dublicates
		$array = array_unique( $array );
		// remove empty (or false) values
		$array = array_filter( $array );
	}

	function cleanText( &$string ) {
		// replace chr style enters with normal enters
		$string = str_replace( chr(194).chr(160), ' ', $string );
		$string = str_replace( chr(160), ' ', $string );
		$string = str_replace( '&#160;', ' ', $string );

		// replace linbreak tags with normal linebreaks (paragraphs, enters, etc).
		$enter_tags = array( 'p', 'br' );
		$regex = '#</?(('.implode( ')|(', $enter_tags ).'))+[^>]*?>\n?#si';
		$string = preg_replace( $regex, " \n", $string );

		// replace indent characters with spaces
		$string = preg_replace( '#<img [^>]*/sourcerer/images/tab\.png[^>]*>#si', '    ', $string );

		// strip all other tags
		$regex = '#<(/?\w+((\s+\w+(\s*=\s*(?:".*?"|\'.*?\'|[^\'">\s]+))?)+\s*|\s*)/?)>#si';
		$string = preg_replace( $regex, "", $string );

		// reset htmlentities
		$string = html_entity_decoder( $string );

		// convert protected html entities &_...; -> &...;
		$string = preg_replace( '#&_([a-z0-9\#]+?);#i', '&\1;', $string );
	}

	function createDebuggingOutput( &$string, $script, $errorlinenr ) {
		$script = str_replace( "\n".'$src_php_succes = 1;', '', $script );
		$script = htmlentities( $script );
		$scriptLines = explode( "\n", $script );
		$count = count( $scriptLines );
		if ( $errorlinenr > $count ) {
			$string = str_replace( 'on line <b>'.$errorlinenr.'</b>' , 'on line <b>'.$count.'</b>', $string );
			$errorlinenr = $count;
		}
		$script = $this->createNumberedTable( $scriptLines, $errorlinenr );
		$this->trimBr( $string );
		$id = rand( 1000, 9999 );
		$string =
			"\n".'<!-- SORCERER DEBUGGING -->'
			."\n".'<div style="clear: both;border: 3px solid #CC3333;background-color: #FFFFFF;">'
				."\n\t".'<div id="sourcerer_debugging_'.$id.'_collapsed">'
					."\n\t\t".'<div style="float:right;padding: 2px 5px;color:#999999;cursor:pointer;cursor:hand;" onclick="document.getElementById(\'sourcerer_debugging_'.$id.'_expanded\').style.display=\'block\';document.getElementById(\'sourcerer_debugging_'.$id.'_collapsed\').style.display=\'none\';">'.JText::_( 'show' ).'</div>'
					."\n\t\t".'<div style="font-size:1.2em;padding: 2px 5px;"><strong>'.JText::_( 'PHP Debugging' ).'</strong></div>'
				."\n\t".'</div>'
				."\n\t".'<div id="sourcerer_debugging_'.$id.'_expanded" style="display:none;">'
					."\n\t\t".'<div style="float:right;padding: 2px 5px;color:#999999;cursor:pointer;cursor:hand;" onclick="document.getElementById(\'sourcerer_debugging_'.$id.'_expanded\').style.display=\'none\';document.getElementById(\'sourcerer_debugging_'.$id.'_collapsed\').style.display=\'block\';">'.JText::_( 'hide' ).'</div>'
					."\n\t\t".'<div style="font-size:1.2em;padding: 2px 5px;"><strong>'.JText::_( 'PHP Debugging' ).'</strong></div>'
					."\n\t\t".'<div style="background-color: #339933;color: #FFFFFF;padding: 2px 5px;"><strong>'.JText::_( 'PHP Code' ).'</strong></div>'
					."\n\t\t".'<div style="max-height:200px;overflow:auto;position:relative;">'.$script.'</div>'
					."\n\t\t".'<div style="background-color: #CC3333;color: #FFFFFF;padding: 2px 5px;"><strong>'.JText::_( 'PHP Error' ).'</strong></div>'
					."\n\t\t".'<div style="background-color: #FFDDDD;padding: 2px 5px;">'.$string.'</div>'
					."\n\t\t".'<div style="font-size:0.8em;font-style:italic;padding: 2px 5px;">'
						."\n\t\t\t".'<div style="float:right;"><a href="http://www.nonumber.nl/sourcerer" target="_blank">'.JText::_( 'More about Sourcerer' ).'</a></div>'
						."\n\t\t\t".'<div>'.JText::_( 'To hide this error, turn off PHP Debugging' ).'</div>'
					."\n\t\t".'</div>'
				."\n\t".'</div>'
				."\n\t".'<div style="clear: both;"></div>'
			."\n".'</div>';
	}

	function createNumberedTable( &$scriptLines, $errorlinenr ) {
		$output = '';
		foreach ( $scriptLines as $linenr => $scriptLine ) {
			$linenr++;
			$scriptLine = str_replace( '    ', '&nbsp;&nbsp;&nbsp;&nbsp;', $scriptLine );
			$bgcolor = '#FFFFFF';
			if ( fmod ( $linenr, 2 ) == 1 ) {
				$bgcolor = '#F7F7F7';
			}
			if ( $errorlinenr == $linenr ) {
				$bgcolor = '#FFDDDD';
			}
			$output .=
				"\n\t\t".'<div style="background-color: '.$bgcolor.';position:relative;">'
					."\n\t\t\t".'<div style="font-family:monospace;color:#999999;text-align:right;padding: 1px 5px;width: 24px;position: absolute;left:0;">'.$linenr.'</div>'
					."\n\t\t\t".'<div style="margin-left: 34px;border-left: 1px solid #DDDDDD;font-family:monospace;padding: 1px 5px;">'.$scriptLine.'</div>'
				."\n\t\t".'</div>'
				;
		}
		return $output;
	}

	function trimBr( &$string ) {
		while ( substr( $string, 0, 6 ) == '<br />' ) {
			$string = trim( substr( $string, 6, strlen( $string ) ) );
		}
		while ( substr( $string, strlen( $string )-6, 6 ) == '<br />' ) {
			$string = trim( substr( $string, 0, strlen( $string )-6 ) );
		}
		$string = trim( $string );
	}

	/*
	 * Protect input and text area's
	 */
	function protect( &$string )
	{
		global $mainframe, $option;
		$task = JRequest::getCmd( 'task' );

		if (
			$option == 'com_rereplacer' ||
			( $option == 'com_content' && $task == 'edit' ) ||
			$option == 'com_contentsubmit'
		) {
			// Protect complete adminForm (to prevent Sourcerer messing stuff up when editing articles and such)
			$regex = '#<form [^>]*name="adminForm".*?>.*?</form>#si';
			if ( preg_match_all( $regex, $string, $matches, PREG_SET_ORDER ) > 0 ) {
				$protected_start = $this->protectStr( $this->src_params->syntax_start );
				$protected_start_0 = $this->protectStr( $this->src_params->syntax_start_0 );
				$protected_end = $this->protectStr( $this->src_params->syntax_end );
				foreach ( $matches as $match ) {
					if ( !( strpos( $match['0'], $this->src_params->syntax_start ) === false ) ) {
						$form_string = str_replace( $this->src_params->syntax_start, $protected_start, $match['0'] );
						$form_string = str_replace( $this->src_params->syntax_start_0, $protected_start_0, $match['0'] );
						$form_string = str_replace( $this->src_params->syntax_end, $protected_end, $form_string );
						$string = str_replace( $match['0'], $form_string, $string );
					}
				}
			}
		}
	}

	function unprotect( &$string )
	{
		$protected_start = $this->protectStr( $this->src_params->syntax_start );
		$protected_start_0 = $this->protectStr( $this->src_params->syntax_start_0 );
		$protected_end = $this->protectStr( $this->src_params->syntax_end );
		$string = str_replace( $protected_start, $this->src_params->syntax_start, $string );
		$string = str_replace( $protected_start_0, $this->src_params->syntax_start_0, $string );
		$string = str_replace( $protected_end, $this->src_params->syntax_end, $string );
	}

	function protectStr( $string )
	{
		$string = base64_encode( $string );
		return $string;
	}

	function cleanLeftoverJunk( &$str )
	{
		$str = preg_replace( '#<\!-- (START|END): SRC_[^>]* -->#', '', $str );
	}

	function getParamValues( &$params ) {
		$values = '';
		if ( isset( $params->_xml ) ) {
			foreach ( $params->_xml as $xml_group ) {
				foreach ( $xml_group->children() as $xml_child ) {
					$key = $xml_child->attributes('name');
					if ( !empty( $key ) && $key['0'] != '@' ) {
						$val = $params->get( $key );
						if ( !is_array( $val ) && !strlen( $val ) ) {
							$val = $xml_child->attributes('default');
							if ( $xml_child->attributes('type') == 'textarea' ) {
								$val = str_replace( '<br />', "\n", $val );
							}
						}
						$values->$key = $val;
					}
				}
			}
		}

		return $values;
	}
}

if ( !function_exists( 'html_entity_decoder' ) ) {
	function html_entity_decoder( $given_html, $quote_style = ENT_QUOTES, $charset = 'UTF-8' )
	{
		if ( phpversion() < '5.0.0' ) {
			$trans_table = array_flip( get_html_translation_table( HTML_SPECIALCHARS, $quote_style ) );
			$trans_table['&#39;'] = "'";
			return ( strtr( $given_html, $trans_table ) );
		}else {
			return html_entity_decode( $given_html, $quote_style, $charset );
		}
	}
}