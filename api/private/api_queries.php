<?php

function get_all_shows(){

    global $db;
    $sql = "
    select `shows`.*, `eps`.`mp3`, `eps`.`newestEpDate` from `shows`
    inner join (
            SELECT show_id, mp3, ep_date newestEpDate
            from `episodes` eps
            where id in (
                select max(id) id
                from episodes
                group by show_id
            )
    ) eps 
    on `shows`.`id` = `eps`.`show_id`;
    ";
    $result = mysqli_query($db, $sql);
    confirm_result_set($result);
    
    return $result;

}
