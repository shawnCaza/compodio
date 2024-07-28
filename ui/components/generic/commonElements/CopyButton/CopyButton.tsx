interface copyButton{
    toCopy: string,
    setDisplayCopiedMessage: React.Dispatch<React.SetStateAction<boolean>>,
    linkTitle?: string;
    children: React.ReactNode
}

import styles from "./copyButton.module.scss"

function CopyButton({toCopy, setDisplayCopiedMessage, linkTitle, children}:copyButton,) {
    
    
    const copyToClipboard = async() =>  {
        
              await navigator.clipboard.writeText(toCopy);
              
              setDisplayCopiedMessage(true)
    }


    return (
        <>
            <button className={'copyButton ' + styles.button} onClick={copyToClipboard} title={linkTitle}>
                {children}
            </button>
        </>
    )
} 

export default CopyButton;