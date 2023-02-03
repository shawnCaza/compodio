import {  ReactNode } from "react";
import Header from "./header/Container/Container";
import Branding from "./header/Branding/Branding";
import SearchContainer from "../search/SearchContainer";
import MainMenu from "./header/MainMenu";

interface layoutProps {
    children: ReactNode
}

function Layout({ children}:layoutProps) {

    return (
        <>
            <Header>
                <Branding/>
                <SearchContainer/>
                <MainMenu/>
            </Header>
            <div id='content'>
                {children}
            </div>
        </>
    )
} 

export default Layout;