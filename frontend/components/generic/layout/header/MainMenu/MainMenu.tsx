import React, { useState, useEffect } from "react";
import Modal from "react-modal";
import { IoMenuSharp, IoCloseSharp } from "react-icons/io5";
import styles from './MainMenu.module.scss'
import { useRouter } from 'next/router'
import {useMenuStore, MenuState} from '../../../../../stores/menuStore'

function MainMenu() {

    Modal.setAppElement('#everything');
    const isOpen = useMenuStore((state: MenuState) => state.menuOpen);
    const toggleMainMenu = useMenuStore((state: MenuState) => state.toggleMenu);
    const closeMainMenu = useMenuStore((state: MenuState) => state.closeMenu);

    const router = useRouter()
    const menuItemClicked = (page:string) => {
        
        router.push(`/${page}`)
        closeMainMenu()
    }

        return (
            <>
                <button
                 className={styles.menuButton}
                 onClick={toggleMainMenu}
                 aria-label="Open Main Menu"
                 aria-haspopup="dialog"
                >
                    <span className={styles.menuIcon}>
                        {isOpen ? <IoCloseSharp/> : <IoMenuSharp/>}
                    </span>                 
                </button>
                <Modal 
                    isOpen={isOpen}
                    onRequestClose={toggleMainMenu}
                    parentSelector={() => document.getElementById('content') as HTMLElement}
                    aria={{
                        labelledby: "main-menu-label"
                    }} 
                    overlayClassName={styles.mainMenuModalOverlay}
                    className={styles.mainMenuModalContent}
                >
                    <h2 id='main-menu-label' className='screen-reader-text'>Site Menu</h2>
                    <div>
                        <ul className="main-menu-option-list">
                            <li className="main-menu-item" onClick={() => menuItemClicked('about')} >
                                <a href='#' tabIndex={1}>About</a>
                            </li>
                            {/* <li className="main-menu-item">
                                <a href='#' >Contact</a>
                            </li> */}
                        </ul>
                    </div>
                </Modal>
            </>
        )
    }

export default MainMenu