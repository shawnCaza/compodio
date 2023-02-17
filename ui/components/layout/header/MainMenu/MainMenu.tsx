import React, { useState, useEffect } from "react";
// import Modal from "../layout/modal";
import { IoMenuSharp } from "react-icons/io5";
import styles from './MainMenu.module.scss'


function MainMenu() {
    // const setMainMenuOpen = props.setMainMenuOpen;

    // const mainMeuOpen = props.mainMeuOpen;

    // const toggleMainMenu = () => {
    //     mainMeuOpen ? setMainMenuOpen(0) : setMainMenuOpen(1);
    // }   

        return (
            <>
                <button
                 className={styles.menuButton}
                 // onClick={toggleMainMenu}
                 aria-haspopup="dialog"
                >
                    <span id="dd" className={styles.menuIcon}>
                        <IoMenuSharp/>
                    </span>                 
                </button>
                {/* <Modal modalOpen={mainMeuOpen} setModalOpen={setMainMenuOpen} labeledBy="main-menu-label" >
                    <h2 id='main-menu-label' className='screen-reader-text'>Site Menu</h2>
                    <div>
                        <ul className="main-menu-option-list">
                            <li className="main-menu-item">
                                <a href='' >About</a>
                            </li>
                            <li className="main-menu-item">
                                <a href='' >Contact</a>
                            </li>
                        </ul>
                    </div>


                </Modal> */}
            </>
        )
    }

export default MainMenu