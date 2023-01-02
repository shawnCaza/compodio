interface showFeedUrl{
    showId: number,
    source: string,
    slug: string | null
}

import CopyButton from "../commonElements/CopyButton"
import { use, useEffect, useState } from "react";

function FeedUrl({showId, source, slug}:showFeedUrl) {
    const feedUrl = `${process.env.NEXT_PUBLIC_feed_URI}${showId}/${source}-${slug}`
    const [displayCopiedMessage, setDisplayCopiedMessage] = useState(false);

    useEffect(() => {
        if(displayCopiedMessage){

            setTimeout(() => {
                setDisplayCopiedMessage(false);
            }, 3000);
        }
      }, [displayCopiedMessage]);


    return (
        <>  
            <div className="showFeedContainer">
                <input type="url" value={feedUrl} readOnly />
                <CopyButton toCopy={feedUrl} setDisplayCopiedMessage={setDisplayCopiedMessage} />
                {displayCopiedMessage &&
                    <>
                    <div className="copiedMessage">Copied</div>
                    </>
                }
            </div>
        </>
    )
} 

export default FeedUrl;