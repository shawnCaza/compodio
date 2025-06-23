import Link from 'next/link';
import { ReactNode } from 'react';

interface showLinkProps{
    slug: string | null,
    children: ReactNode
}

function ShowLink({ slug, children}:showLinkProps) {

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