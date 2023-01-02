interface copyButton{
    toCopy: string,
    setDisplayCopiedMessage: React.Dispatch<React.SetStateAction<boolean>>;
}

import { IoIosCopy } from "react-icons/io";

function CopyButton({toCopy, setDisplayCopiedMessage}:copyButton) {
    
    
    const copyToClipboard = async() =>  {
        
              await navigator.clipboard.writeText(toCopy);
              
              setDisplayCopiedMessage(true)
    }


    return (
        <>
         <span >
            <IoIosCopy onClick={copyToClipboard}/>
        </span>


        </>
    )
} 

export default CopyButton;