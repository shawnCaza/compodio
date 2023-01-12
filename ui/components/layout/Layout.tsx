import {  ReactNode } from "react";
import Header from "./header/header";
import SiteBranding from "./header/siteBranding";
import MainMenu from "./header/MainMenu";
import SearchBar from "./header/search/SearchBar"

interface layoutProps {
    children: ReactNode
}

function Layout({ children}:layoutProps) {

    return (
        <>
            <Header>
                <SiteBranding/>
                {/* <SearchBar/>
                <MainMenu/> */}
            </Header>
            {children}
        </>
    )
} 

export default Layout;