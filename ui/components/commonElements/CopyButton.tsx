interface copyButton{
    toCopy: string,
}

import { IoIosCopy } from "react-icons/io";

function CopyButton({toCopy}:copyButton) {
    
    const copyToClipboard = async() =>  {
        
            if ("clipboard" in navigator) {
              await navigator.clipboard.writeText(toCopy);
            } else {
              document.execCommand("copy", true, toCopy);
            }
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