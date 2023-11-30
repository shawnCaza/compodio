interface extFeed{
    extFeed: {link: string, feedType: string}
}

import styles from './RssLink.module.scss'
import { PiSpotifyLogoFill } from "react-icons/pi";
import { PiApplePodcastsLogoFill } from "react-icons/pi";
import { PiGooglePodcastsLogo } from "react-icons/pi";

function ExtLink({extFeed}:extFeed) {
 

    return (
        <>  
            <span className={styles.subscribeOptionButtonContainer}>

                <span className="screen-reader-text">Subscribe on {extFeed.feedType}</span>
                    <a className={'button ' + styles.subscribeOptionButton} href={extFeed.link} target='_blank' rel='noreferrer' title={'Subscript on ' + extFeed.feedType}>
                        {extFeed.feedType === 'spotify' &&
                            <PiSpotifyLogoFill/>
                        }
                        {extFeed.feedType === 'apple' &&
                            <PiApplePodcastsLogoFill/>
                        }
                        {extFeed.feedType === 'google' &&
                            <PiGooglePodcastsLogo/>
                        }
                    </a>

            </span>
        </>
    )
} 

export default ExtLink;