import {  ReactNode } from "react";
import styles from './ContentSection.module.scss'

interface contentSectionProps {
    heading: string | null,
    tag: keyof JSX.IntrinsicElements, // TODO could constrain to heading tag: https://stackoverflow.com/a/60837221
    centered?: boolean,
    readingWidth?: boolean,
    spacing?: 'padded' | 'tight',
    children: ReactNode
}

function ContentSection({heading=null, tag:Tag, centered=false, readingWidth=false, spacing='padded', children}:contentSectionProps ) {

    return (
        <>
            <div className={
                (spacing==='padded' ? styles.paddedContentSection : styles.tightContentSection )
                + (centered ? " " + styles.centeredSection : '')
                + (readingWidth ? " " + styles.readingWidth : '')
                }>
                <Tag>{heading}</Tag>
                    
                {children}
                    
            </div>
        </>
    )
} 

export default ContentSection;