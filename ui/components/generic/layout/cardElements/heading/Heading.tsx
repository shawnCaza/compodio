
import {  ReactNode } from "react";
import styles from './Heading.module.scss'

interface headingProps {

    children: ReactNode
}

function Heading ({children}:headingProps) {
    
    return (
        <div className={styles.heading} >
            {children}
        </div>
    )
}

export default Heading;