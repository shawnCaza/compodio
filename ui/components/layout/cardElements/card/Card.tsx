import {  ReactNode } from "react";

interface cardProps {
    cardStyles: {readonly [key: string]: string };
    children: ReactNode
}

function Card({cardStyles, children}:cardProps) {
    

    return (
        <>
            <div className={cardStyles.card}>
                {children}
            </div>
        </>
    )
}

export default Card;