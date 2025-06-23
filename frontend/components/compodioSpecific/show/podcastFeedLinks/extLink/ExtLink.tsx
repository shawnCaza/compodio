interface extFeed{
    extFeed: {link: string, feedType: string}
}

import styles from '../subscribeOptionButton.module.scss'
import { PiSpotifyLogoFill } from "react-icons/pi";
import { PiApplePodcastsLogoFill } from "react-icons/pi";
import { PiGooglePodcastsLogo } from "react-icons/pi";

function ExtLink({extFeed}:extFeed) {
 

    return (
        <>  
            <span className={styles.subscribeOptionButtonContainer}>

                <span className="screen-reader-text">Subscribe on {extFeed.feedType}</span>
                    <a className='button' href={extFeed.link} target='_blank' rel='noreferrer' title={'Subscribe on ' + extFeed.feedType.charAt(0).toUpperCase() + extFeed.feedType.slice(1)}>
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