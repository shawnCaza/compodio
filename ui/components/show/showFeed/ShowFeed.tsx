interface showFeedUrl{
    showId: number,
    slug: string | null
}

import { IoLogoRss } from "react-icons/io";
import CopyButton from "../../commonElements/CopyButton/CopyButton";
import HelpButton from "../../commonElements/helpButton";
import styles from './ShowFeed.module.scss'


import {  useEffect, useState } from "react";

function FeedUrl({showId, slug}:showFeedUrl) {
    const feedLink = `${process.env.NEXT_PUBLIC_feed_URI}${showId}/${slug}`
    const [displayCopiedMessage, setDisplayCopiedMessage] = useState(false);
    const [helpActive, setHelpActive] = useState(false);

    useEffect(() => {
        if(displayCopiedMessage){

            setTimeout(() => {
                setDisplayCopiedMessage(false);
                // setDisplayCopiedMessage(true);
            }, 3000);
        }
      }, [displayCopiedMessage]);


    return (
        <>  
            <div className={styles.showFeedContainer} >
                
                <div className={styles.subLabel}>
                    Subscribe
                </div>

                <div className={styles.feedAndCopyButtonContainer}>

                    <span className={styles.rssIcon}><IoLogoRss/></span>

                    <input className={styles.url} value={feedLink} readOnly />
                    
                    <CopyButton toCopy={feedLink} setDisplayCopiedMessage={setDisplayCopiedMessage} />
                    {displayCopiedMessage &&
                        <>
                            <div className={styles.copiedMessage}>Copied to clipboard</div>
                        </>
                    }    
                </div>
                {/* <HelpButton setHelpActive={setHelpActive} /> */}
                
            </div>
        </>
    )
} 

export default FeedUrl;