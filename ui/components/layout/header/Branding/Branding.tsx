import Link from 'next/link';
import styles from './Branding.module.scss'

function Branding() {
    return(
        <>
            <Link href="/" title="home">
                <div className={styles.container}>
                    <span className={styles.logoContainer}>
                        <svg className={styles.logo}>
                            <use href="/compodio_logo.svg#logo" />
                        </svg> 
                    </span>
                    <span className="title-container">
                            compodio
                    </span> 
                </div>
            </Link>
        </>
    )
}

export default Branding;