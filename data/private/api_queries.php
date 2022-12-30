<?php

function get_all_shows(){

    global $db;
    $sql = "
        SELECT `shows`.*, `eps`.`mp3`, `eps`.`newestEpDate`, `show_tags`.`tags` 
        FROM `shows`

        /* Collect all the show tags into an array */
        LEFT JOIN (
                SELECT show_id, JSON_ARRAYAGG(tag_id) AS tags
                FROM show_tags GROUP BY show_id
        ) show_tags
        ON `show_tags`.`show_id` = `shows`.`id`
        
        /* Join most recent episode */
        INNER JOIN (
            SELECT show_id, mp3, ep_date newestEpDate
            FROM `episodes` eps
            WHERE id IN (
                SELECT MAX(id) id
                FROM episodes
                GROUP BY show_id
            )
        ) eps 
        ON `shows`.`id` = `eps`.`show_id`

        ORDER BY newestEpDate DESC
        ;
    ";
    $result = mysqli_query($db, $sql);
    confirm_result_set($result);
    
    return $result;

}
