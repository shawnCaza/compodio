interface showFeedUrl{
    showId: Number,
    source: string,
    slug: string | null
}

import CopyButton from "../commonElements/CopyButton"


function FeedUrl({showId, source, slug}:showFeedUrl) {
    const feedUrl = `${process.env.NEXT_PUBLIC_feed_URI}${showId}/${source}-${slug}`
    
    return (
        <>
            <input type="url" value={feedUrl} readOnly />
            <CopyButton toCopy={feedUrl} />

        </>
    )
} 

export default FeedUrl;