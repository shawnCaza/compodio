import {  ReactNode } from "react";
import Header from "./header/header";
import SiteBranding from "./header/siteBranding";
import SearchContainer from "../search/SearchContainer";
import MainMenu from "./header/MainMenu";

interface layoutProps {
    children: ReactNode
}

function Layout({ children}:layoutProps) {

    return (
        <>
            <Header>
                <SiteBranding/>
                 <SearchContainer/>
                {/*<MainMenu/> */}
            </Header>
            <div id='content'>
                {children}
            </div>
        </>
    )
} 

export default Layout;