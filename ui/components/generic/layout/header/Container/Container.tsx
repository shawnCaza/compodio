import {  ReactNode } from "react";
import styles from './Container.module.scss'

interface headingProps {
    children: ReactNode
}

function Container({children}:headingProps) {
    return(
        <>
            <header className={styles.header} >
                {children}
            </header>

        </>
    )
}

export default Container;