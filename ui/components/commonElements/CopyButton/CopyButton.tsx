interface copyButton{
    toCopy: string,
    setDisplayCopiedMessage: React.Dispatch<React.SetStateAction<boolean>>;
}

import { IoIosCopy } from "react-icons/io";
import styles from "./copyButton.module.scss"

function CopyButton({toCopy, setDisplayCopiedMessage}:copyButton) {
    
    
    const copyToClipboard = async() =>  {
        
              await navigator.clipboard.writeText(toCopy);
              
              setDisplayCopiedMessage(true)
    }


    return (
        <>
         <span >
            {/* <IoIosCopy onClick={copyToClipboard}/> */}
            <button className={styles.button} onClick={copyToClipboard} title="Copy RSS Podcast Subscription link">Copy</button>
        </span>


        </>
    )
} 

export default CopyButton;