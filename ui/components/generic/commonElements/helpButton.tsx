interface helpButtonProps{
    setHelpActive: React.Dispatch<React.SetStateAction<boolean>>;
}

import { IoMdHelpCircle } from "react-icons/io";

function HelpButton({setHelpActive}:helpButtonProps) {
    
    
    const doHelp = () =>  {
                      
        setHelpActive(true)
    }


    return (
        <>
            <span>
                <IoMdHelpCircle onClick={doHelp}/>
            </span>
        </>
    )
} 

export default HelpButton;