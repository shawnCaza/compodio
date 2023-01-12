import Link from 'next/link';

function SiteBranding() {
    return(
        <>
            <Link href="/" title="home">
                <div className="site-branding">
                    <span className='logo'>

                            {/* <img src={logo} className="App-logo" alt="CoPod logo" width="473px" height="182px" /> */}
                    </span>
                    <span className="title-container">

                            CoPod
                        
                    </span>
                </div>
            </Link>
        </>
    )
}

export default SiteBranding;