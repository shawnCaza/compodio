<?php
require_once('private/initialize.php');
require_once(PRIVATE_PATH .'/api_queries.php');
// header('Access-Control-Allow-Origin: http://localhost:3000', false); //TODO only for dev env
header('Access-Control-Allow-Origin: *', false); //TODO only for dev env
// Set cache control to 10 minutes
header('Cache-Control: max-age=600');

$result = get_all_shows();
// echo all results as json
echo json_encode(mysqli_fetch_all($result, MYSQLI_ASSOC));