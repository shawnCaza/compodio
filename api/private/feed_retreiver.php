<?php
header('Content-type: application/rss+xml; charset=utf-8');
// echo '<?xml-stylesheet type="text/css" href="/podcasting/includes/style/rss-style.css"

function mysql2date( $format, $date, $translate = true ) {
    // Adapted from WP - https://developer.wordpress.org/reference/functions/mysql2date/
	if ( empty( $date ) ) {
		return false;
	}

	$datetime = date_create( $date, new DateTimeZone('America/Toronto') );

	if ( false === $datetime ) {
		return false;
	}

	return $datetime->format( $format );
}

if (isset($_GET['id'])){
    require_once(PRIVATE_PATH .'/feed_queries.php');
    $show_id = $_GET['id'];
   
    $show = get_show_by_id($show_id);
    $episodes = get_eps_by_show_id($show_id);

    // channel details
    echo "<rss version='2.0' 
        xmlns:atom='http://www.w3.org/2005/Atom'
        xmlns:itunes='http://www.itunes.com/dtds/podcast-1.0.dtd'>
        <channel>
            <title>{$show['showName']}</title>
            <description>{$show['desc']}</description>
            <link>{$show['internal_link']}</link>
            <docs>http://blogs.law.harvard.edu/tech/rss</docs>
            <itunes:author>{$show['host']}</itunes:author>
            
            <itunes:owner>
                <itunes:name>{$show['source']}</itunes:name>
                <itunes:email>{$show['email']}</itunes:email>
            </itunes:owner>
            <itunes:image href='{$show['img']}'></itunes:image>";

    foreach($episodes as $ep) {
        $ep_date = $ep['ep_date'];
        $ep_date = mysql2date( 'D, d M Y H:i:s +0000', $ep_date, false );

        echo "<item>
                <title>{$ep['ep_date']}</title>
                <enclosure url='{$ep['mp3']}' length='{$ep['file_size']}' type='audio/mpeg'></enclosure>
                <guid isPermaLink='false'>{$show['slug']}-{$ep['id']}'</guid>
                <itunes:duration>{$show['duration']}</itunes:duration>
                <pubDate>{$ep_date}</pubDate>
             </item>";
    }

    echo "</channel></rss>";

}

?>  