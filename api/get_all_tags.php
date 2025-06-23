<?php
require_once('private/initialize.php');
require_once(PRIVATE_PATH .'/api_queries.php');
// header('Access-Control-Allow-Origin: http://localhost:3000', false); //TODO only for dev env
header('Access-Control-Allow-Origin: *', false); //TODO only for dev env
$allTags = get_all_tags();
echo $allTags;