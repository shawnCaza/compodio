<?php
header('Content-type: application/rss+xml; charset=utf-8');
// echo '<?xml-stylesheet type="text/css" href="/podcasting/includes/style/rss-style.css"

function mysql2date( $format, $date, $useGMT = false ) {
    // Adapted from WP - https://developer.wordpress.org/reference/functions/mysql2date/
	if ( empty( $date ) ) {
		return false;
	}

	$datetime = date_create( $date, new DateTimeZone('America/Toronto') );

	if ( false === $datetime ) {
		return false;
	}
    if($useGMT){
        $datetime->setTimezone(new DateTimeZone('GMT'));
    }
	return $datetime->format( $format );
}

function get_human_date($date) {
    // format date to "Sept 1, 2020 9AM"
    $human_date = mysql2date( 'M j, Y', $date, false );
    return $human_date;
}

if (isset($_GET['id'])){
    require_once(PRIVATE_PATH .'/feed_queries.php');
    $show_id = $_GET['id'];
   
    $show = get_show_by_id($show_id);
    $episodes = get_eps_by_show_id($show_id);
    $encoded_show_link = rawurlencode($show['internal_link']);
    $show_desc = htmlentities($show['desc'], ENT_XML1, 'UTF-8');
    $host = htmlentities($show['host'], ENT_XML1, 'UTF-8');
    $show_name = htmlentities($show['showName'], ENT_XML1, 'UTF-8');

    // use last episode for eTag headers
    $newest_ep = end($episodes);
    //use EST for modified even though we call it GMT, since there could be a slight delay between scraping and publishing
    $newest_ep_modified = mysql2date( 'D, d M Y H:i:s -0000', $newest_ep['modified'] );
    $newest_file_size = $newest_ep['file_size'];
    $etag = '"' . $newest_ep_modified . '-' . $newest_file_size . '"';
    header("Etag: {$etag}");
    header("Last-Modified: {$newest_ep_modified}"); 

    


    // channel details
    echo "<rss version='2.0' 
        xmlns:atom='http://www.w3.org/2005/Atom'
        xmlns:itunes='http://www.itunes.com/dtds/podcast-1.0.dtd'>
        <channel>
            <title>{$show_name}</title>
            <description>{$show_desc}</description>
            <link>{$encoded_show_link}</link>
            <docs>http://blogs.law.harvard.edu/tech/rss</docs>
            <itunes:author>{$host}</itunes:author>
            
            <itunes:owner>
                <itunes:name>{$show['source']}</itunes:name>
                <itunes:email>{$show['email']}</itunes:email>
            </itunes:owner>
            <itunes:image href='{$show['img']}'></itunes:image>";
    
    $current_ep_idx = 0;
    $current_ep_part = 0;
    $previous_ep_date = null;
    $num_eps = count($episodes);

    foreach($episodes as $ep) {
        $ep_date_est_string = $ep['ep_date'];
        $ep_date = mysql2date( 'D, d M Y H:i:s +0000', $ep_date_est_string, true); 
        // format date to "Sept 1, 2020 9AM"
        $ep_human_date = get_human_date($ep_date_est_string);
        $ep_human_date_with_hour = mysql2date( 'gA M j, Y', $ep_date_est_string );

        // CFRU is an example of a site where 1 episode may have multiple mp3 files since they post everything in 1 hour segments and some shows are longer than 1 hour. For cases like this let's check for eps where $ep_date has the same year, month, and day as $previous_ep_date and specify part numbers.
        if ( $current_ep_idx > 0 && $ep_human_date == get_human_date($episodes[$current_ep_idx - 1]['ep_date'])) {
            // Previous ep matches
            $current_ep_part++;
        
        } elseif ( $current_ep_idx < $num_eps - 1 && $ep_human_date == get_human_date($episodes[$current_ep_idx + 1]['ep_date']) ) {
            //the next episode is a duplicate 
            $current_ep_part = 1;
        } else {
            $current_ep_part = 0;
        }
        
        if($current_ep_part > 0) {
            $ep_title= $ep_human_date_with_hour;
        }
        else {
            $ep_title= $ep_human_date;
        }



        // Need to encode link to be valid XML. Also need to maintain the slashes and colon in the link for it the link to work
        // $encoded_mp3_link = str_replace("%3A",":", implode('/', array_map('rawurlencode', explode('/', $ep['mp3_link']))));
        $encoded_mp3_link = str_replace("%3A",":", implode('/', array_map('rawurlencode', explode('/', $ep['mp3']))));
        echo "<item>
                <title>{$ep_title}</title>
                <enclosure url='{$encoded_mp3_link}' length='{$ep['file_size']}' type='audio/mpeg'></enclosure>
                <description>{$show_name} for {$ep_title}</description>
                <guid isPermaLink='false'>{$show['slug']}-{$ep['id']}'</guid>
                <itunes:duration>{$show['duration']}</itunes:duration>
                <pubDate>{$ep_date}</pubDate>
             </item>
             ";

        $current_ep_idx++;
        $previous_ep_human_date = $ep_date;
    }

    echo "</channel>
    </rss>";

}

?>  