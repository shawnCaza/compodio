import {  ReactNode } from "react";

interface headingProps {
    children: ReactNode
}

function Header({children}:headingProps) {
    return(
        <>
            <header className="site-header">
                {children}
            </header>

        </>
    )
}

export default Header;