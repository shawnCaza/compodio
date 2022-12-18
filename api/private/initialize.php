<?php
ob_start();// output buffering is turned on
session_start();// turn on sessions
  define("PRIVATE_PATH", dirname(__FILE__));
  define("PROJECT_PATH", dirname(PRIVATE_PATH));
  define("PUBLIC_PATH", PROJECT_PATH . '/public');
  define("SHARED_PATH", PRIVATE_PATH . '/shared');
  define("FRONT_SHARED_PATH", PRIVATE_PATH . '/front_shared');
  define("CONTENT_PATH", PRIVATE_PATH . '/content');
  $public_end = strpos($_SERVER['SCRIPT_NAME'], '/public') + 7;

  $doc_root = substr($_SERVER['SCRIPT_NAME'], 0, $public_end);

//echo substr($_SERVER['SCRIPT_NAME'], 0, $public_end-7);
define("DOMAIN_ROOT", substr($_SERVER['SCRIPT_NAME'], 0, $public_end-7));

if(!($public_end > 7)){
    
     $public_end = strpos($_SERVER['SCRIPT_NAME'], '/private');

  $doc_root = substr($_SERVER['SCRIPT_NAME'], 0, $public_end) . '/public';
    
    
}

 define("WWW_ROOT", $doc_root );

  require_once('database.php');


  $db = db_connect();
  $errors = [];




?>