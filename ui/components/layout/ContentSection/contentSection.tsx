import {  ReactNode } from "react";
import styles from './ContentSection.module.scss'

interface contentSectionProps {
    heading: string | null,
    tag: keyof JSX.IntrinsicElements, // TODO could constrain to heading tag: https://stackoverflow.com/a/60837221
    children: ReactNode
}

function ContentSection({heading=null, tag:Tag, children}:contentSectionProps ) {

    return (
        <>
            <div className={styles.paddedContentSection}>
                <Tag>{heading}</Tag>
                    
                {children}
                    

            </div>
        </>
    )
} 

export default ContentSection;