import Link from 'next/link';
import styles from './Branding.module.scss'
import { useMenuStore, MenuState } from '../../../../stores/menuStore';



function Branding() {

    const closeMenu = useMenuStore((state: MenuState) => state.closeMenu)

    return(
        <>
            <Link href="/" onClick={closeMenu} title="home">
                <div className={styles.container}>
                    <span className={styles.logoContainer}>
                        <svg className={styles.logo}>
                            <use href="/compodio_logo.svg#logo" />
                        </svg> 
                    </span>
                    <span className={styles.siteName}>
                            compodio
                    </span> 
                </div>
            </Link>
        </>
    )
}

export default Branding;