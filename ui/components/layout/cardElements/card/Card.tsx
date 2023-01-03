import {  ReactNode } from "react";
import styles from './Card.module.scss'

interface cardProps {

    children: ReactNode
}

function Card({children}:cardProps) {
    

    return (
        <>
            <div className={styles.card}>
                {children}
            </div>
        </>
    )
} 

export default Card;