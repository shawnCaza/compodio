import {  ReactNode } from "react";

interface contentSectionProps {
    heading: string | null,
    tag: keyof JSX.IntrinsicElements, // TODO could constrain to heading tag: https://stackoverflow.com/a/60837221
    children: ReactNode
}

function ContentSection({heading=null, tag:Tag, children}:contentSectionProps ) {

    return (
        <>
            <div className="content-section">
                <Tag>{heading}</Tag>
                    
                {children}
                    

            </div>
        </>
    )
} 

export default ContentSection;