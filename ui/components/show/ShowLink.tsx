import Link from 'next/link';
import { ReactNode } from 'react';

interface showLinkProps{
    slug: string | null,
    children: ReactNode
}

function ShowLink({ slug, children}:showLinkProps) {
    // Adds show despription. If approxLength is greater than 0, will shorten description rounding up to the nearest space after approxLength.

    const showURL = `/shows/${slug}`

    return (
        <>
            <Link href={showURL} >
                {children}
            </Link>
        </>
    )
} 

export default ShowLink;