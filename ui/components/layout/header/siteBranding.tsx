
function SiteBranding() {
    return(
        <>
            <a href={process.env.PUBLIC_URL} title='home'>
                <div className="site-branding">
                    <span className='logo'>
                        

                            {/* <img src={logo} className="App-logo" alt="CoPod logo" width="473px" height="182px" /> */}
                        
                    </span>
                    <span className="title-container">

                            CoPod
                        
                    </span>
                </div>
            </a>
        </>
    )
}

export default SiteBranding;