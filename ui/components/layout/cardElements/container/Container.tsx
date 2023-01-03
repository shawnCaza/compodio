
import {  ReactNode } from "react";
import styles from './Container.module.scss'

interface containerProps {

    children: ReactNode
}

function Container ({children}:containerProps) {
    
    return (
        <div className={styles.cardContainer} >
            {children}
        </div>
    )
}

export default Container;