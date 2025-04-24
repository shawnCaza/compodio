interface showFeedUrl{
    showId: string,
    slug: string | null,
    showName: string
}

import { IoLogoRss } from "react-icons/io";
import CopyButton from "../../../../generic/commonElements/CopyButton/CopyButton";
import styles from './RssLink.module.scss'
import optionButtonStyles from '../subscribeOptionButton.module.scss'
import Modal from "react-modal";
import FeedUrl from "../../showFeed/ShowFeed";

import {useState } from "react";

function RssLink({showId, slug, showName}:showFeedUrl) {
    Modal.setAppElement('#everything');
    const feedLink = `${process.env.NEXT_PUBLIC_feed_URI}${showId}/${slug}`
    const [displayCopiedMessage, setDisplayCopiedMessage] = useState(false);
 

    return (
        <>  
                <span className={optionButtonStyles.subscribeOptionButtonContainer}>

                    <span className="screen-reader-text">Copy RSS Podcast Subscription link:</span>

                    <CopyButton toCopy={feedLink} setDisplayCopiedMessage={setDisplayCopiedMessage} linkTitle="Copy RSS Podcast Subscription link">
                        <IoLogoRss/>
                    </CopyButton>
                   
                </span>

                <Modal 
                    isOpen={displayCopiedMessage}
                    onRequestClose={()=>setDisplayCopiedMessage(false)}
                    parentSelector={() => document.getElementById('everything') as HTMLElement}
                    aria={{
                        labelledby: "main-menu-label"
                    }} 
                    overlayClassName={styles.rssCopiedMessageModalOverlay}
                    className={styles.modalCopiedMessage}
                >
                    <h1>To finish subscribing</h1>
                    
                    <ol>
                        <li>The RSS link for <strong>&apos;{showName}&apos;</strong> has already been added to your clipboard.</li>
                        <li>Open your podcast app</li>
                        <li>
                            <a href="https://medium.com/@joshmuccio/how-to-manually-add-a-rss-feed-to-your-podcast-app-on-desktop-ios-android-478d197a3770" target="_blank" rel="noopener noreferrer">Find the option to add a podcast by URL</a></li>
                        <li>Paste the link into your podcast app</li>
                    </ol>

                    <button className="highlight-button" onClick={()=>setDisplayCopiedMessage(false)}>Okay, I got it!</button>
                    <p>For your reference, below is the RSS link that has already been copied to your clipboard.</p>
                    <FeedUrl showId={showId} slug={slug}></FeedUrl>

                </Modal>
            
        </>
    )
} 

export default RssLink;