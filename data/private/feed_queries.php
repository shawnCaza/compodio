<?php

function get_show_by_id($show_id){

    global $db;
    $sql = "select * from `shows`
            where id = {$show_id}";
    $result = mysqli_query($db, $sql);
    confirm_result_set($result);
    $show = mysqli_fetch_assoc($result); // find first


    mysqli_free_result($result);
    return $show;

}

function get_eps_by_show_id($show_id){

    global $db;
    $sql = "select * from `episodes`
    where show_id = {$show_id}
    limit 100";
    $result = mysqli_query($db, $sql);
    confirm_result_set($result);
    
    return $result->fetch_all(MYSQLI_ASSOC);

}
///// alert subs stats admin page

function get_subscription_status_counts(){

    global $db;
    $sql = "SELECT status, count(*) as count FROM alert_subs GROUP BY status";
    $result = mysqli_query($db, $sql);
    confirm_result_set($result);

    return $result;

}
