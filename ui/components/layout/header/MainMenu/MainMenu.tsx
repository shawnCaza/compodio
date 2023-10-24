import React, { useState, useEffect } from "react";
import Modal from "react-modal";
import { IoMenuSharp, IoCloseSharp } from "react-icons/io5";
import styles from './MainMenu.module.scss'


function MainMenu() {

    Modal.setAppElement('#everything');
    const [isOpen, setIsOpen] = useState(false);

    const toggleMainMenu = () => {
        isOpen ? setIsOpen(false) : setIsOpen(true);
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
                            <li className="main-menu-item">
                                <a href='' >About</a>
                            </li>
                            <li className="main-menu-item">
                                <a href='' >Contact</a>
                            </li>
                        </ul>
                    </div>
                </Modal>
            </>
        )
    }

export default MainMenu