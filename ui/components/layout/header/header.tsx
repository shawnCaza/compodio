import {  ReactNode } from "react";

interface headingProps {
    children: ReactNode
}

function Header({children}:headingProps) {
    return(
        <>
            <header className="site-header" 
                style={{
                    display:"flex",
                    justifyContent:"space-between"
                }}>
                {children}
            </header>

        </>
    )
}

export default Header;