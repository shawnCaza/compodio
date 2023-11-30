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
    `show_tags`.`tagIds`,
    `ext_feed_links`.`extFeeds`

    FROM `shows`

    LEFT JOIN show_images ON `show_images`.`show_id` = `shows`.`id`

    /* Collect all the show tags into an array */
    LEFT JOIN (
    SELECT show_id, JSON_ARRAYAGG(tag_id) AS tagIds
    FROM show_tags GROUP BY show_id
    ) show_tags
    ON `show_tags`.`show_id` = `shows`.`id`

    /* Add array of external podcast feed objects */
    LEFT JOIN (
        SELECT show_id, JSON_ARRAYAGG(JSON_OBJECT('link', link, 'feedType', feedType)) AS extFeeds
        FROM ext_feed_links GROUP BY show_id
    ) ext_feed_links
    ON `ext_feed_links`.`show_id` = `shows`.`id`


    /* Join most recent episode */
    INNER JOIN (
        SELECT `episodes`.`show_id`, mp3, ep_date newestEpDate
        FROM `episodes` 
        RIGHT JOIN (
            SELECT show_id, MAX(ep_date) max_ep_date
            FROM episodes
            GROUP BY show_id
        ) newest on `newest`.`show_id` = `episodes`.`show_id` and `newest`.`max_ep_date` = `episodes`.`ep_date`
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

function get_all_ext_feeds(){

    global $db;
    //table ext_feed_links has columns named: show_id, link, feedType
    //there can be multiple results for a show_id.
    // link, and feedType are unique for each show_id 
    // return a json object from ext_feed_links with the following shape:
    // {show_id:{feedType:link, feedType:link,...},...}
    $sql = "select json_objectagg(show_id, feeds) allExtFeeds
            FROM (
                SELECT show_id, JSON_OBJECTAGG(feedType, link) as feeds
                FROM ext_feed_links GROUP BY show_id
            ) t;";
    $result = mysqli_query($db, $sql);
    confirm_result_set($result);
    $all_tags = mysqli_fetch_assoc($result); 

    mysqli_free_result($result);
    return $all_tags['allExtFeeds'];
    

}
