import {  ReactNode } from "react";
import Header from "./header/Container/Container";
import Branding from "./header/Branding/Branding";
import SearchContainer from "../search/Search";
import MainMenu from "./header/MainMenu/MainMenu";

interface layoutProps {
    children: ReactNode
}

function Layout({ children}:layoutProps) {

    return (
        <>
            <div id='everything'>
                <Header>
                    <Branding />
                    <div className="middleItems"> {/* Used to ensure all middle items are centered to page width in grid. */}       
                        <SearchContainer />
                    </div>
                    <MainMenu/>
                </Header>
                <div id='content'>
                    {children}
                </div>
            </div>
        </>
    )
} 
 
export default Layout;