<?php

require_once('db_credentials.php');

function db_connect()
{
  // Fallback to db_credentials.php values if env vars aren't set
  $server = getenv('DB_HOST') ?: DB_SERVER;
  $user = getenv('DB_USER') ?: DB_USER;
  $pass = getenv('DB_PASSWORD') ?: DB_PASS;
  $name = getenv('DB_NAME') ?: DB_NAME;
  $port = getenv('DB_PORT') ?: 3306;
  $connection = mysqli_connect($server, $user, $pass, $name, $port);
  confirm_db_connect();
  return $connection;
}

function db_disconnect($connection)
{
  if (isset($connection)) {
    mysqli_close($connection);
  }
}

function db_escape($connection, $string)
{
  return mysqli_real_escape_string($connection, $string);
}

function confirm_db_connect()
{
  if (mysqli_connect_errno()) {
    $msg = "Database connection failed: ";
    $msg .= mysqli_connect_error();
    $msg .= " (" . mysqli_connect_errno() . ")";
    exit($msg);
  }
}

function confirm_result_set($result_set)
{
  if (!$result_set) {

    exit("Database query failed.");
  }
}
