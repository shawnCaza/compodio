import { Show } from '../../../../hooks/queries/shows';
import styles from './FeedLinks.module.scss';
import ExtLink from '../extLink/ExtLink';
import RssLink from '../rssLink/RssLink';
interface FlexRowProps{
    showId: string,
    slug: string | null,
    showName: string,
    extFeeds: string | null
}


function FeedLinks({showId, slug, showName, extFeeds}:FlexRowProps) {
    return ( 
        <>
           <div className={styles.flexRow}>
                {/* map over show.extFeeds */ 
                  extFeeds && JSON.parse(extFeeds).map((extFeed:{link: string, feedType: string}) =>
                  <ExtLink key={extFeed.link} extFeed={extFeed} />
                )}

                <RssLink showId={showId} slug={slug} showName={showName} />
           </div>
        </>
    )
} 

export default FeedLinks;