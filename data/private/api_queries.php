<?php

function get_all_shows(){

    global $db;
    $sql = "
            SELECT 
            `shows`.`desc`,
            `shows`.`duration`,
            `shows`.`email`,
            `shows`.`ext_link`,
            `shows`.`host`,
            `shows`.`id`,
            `shows`.`internal_link`,
            `shows`.`showName`,
            `shows`.`slug`,
            `shows`.`source`,
            `show_images`.`dom_colours`,
            `show_images`.`sizes`,
            `eps`.`mp3`, 
            `eps`.`newestEpDate`, 
            `show_tags`.`tagIds` 

            FROM `shows`

            LEFT JOIN show_images ON `show_images`.`show_id` = `shows`.`id`

            /* Collect all the show tags into an array */
            LEFT JOIN (
            SELECT show_id, JSON_ARRAYAGG(tag_id) AS tagIds
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
            ;";
    $result = mysqli_query($db, $sql);
    confirm_result_set($result);
    
    return $result;

}


function get_all_tags(){

    global $db;
    $sql = "SELECT JSON_OBJECTAGG(
                id, 
                JSON_OBJECT(
                    'id', id,
                    'tag', tag,
                    'freq', freq)
                ) as allTags
            from all_tags
            ORDER BY freq
            ;";
    $result = mysqli_query($db, $sql);
    confirm_result_set($result);
    $all_tags = mysqli_fetch_assoc($result); // find first

    mysqli_free_result($result);
    return $all_tags['allTags'];

}
