<?php

function get_all_shows(){

    global $db;
    $sql = "
        select `shows`.*, `eps`.`mp3`, `eps`.`newestEpDate`, `show_tags`.`tags` from `shows`
        
        left join (
                SELECT show_id, JSON_ARRAYAGG(tag_id) AS tags
                FROM show_tags GROUP BY show_id
        ) show_tags
        on `show_tags`.`show_id` = `shows`.`id`
            
        inner join (
            SELECT show_id, mp3, ep_date newestEpDate
            from `episodes` eps
            where id in (
                select max(id) id
                from episodes
                group by show_id
            )
        ) eps 
        on `shows`.`id` = `eps`.`show_id`
        ;
    ";
    $result = mysqli_query($db, $sql);
    confirm_result_set($result);
    
    return $result;

}
