<?php
require_once('private/initialize.php');
require_once(PRIVATE_PATH .'/api_queries.php');
$result = get_all_shows();
echo json_encode($result->fetch_all(MYSQLI_ASSOC));