//handles 3 conditions loading, error, data
import { useEffect } from "react"

export function useItemSelectedValidation(results, setComboItemSelected, comboItemSelected, resultLimit) {
    
    useEffect(() => {
        if(!results) return

        if (!results.length) {
            
            setComboItemSelected(0)
        } else {
        
            setComboItemSelected(1)
        }
  
    }, [results, setComboItemSelected])
    
    if (!results) return
    
    if (results.length < comboItemSelected || resultLimit < comboItemSelected) {
        //console.log('selected combo item out of range',props.comboItemSelected)
        setComboItemSelected(1);
    } else if (comboItemSelected === 0 && results.length) {
        if (results.length < resultLimit) {
            setComboItemSelected(results.length)
        } else {
            setComboItemSelected(resultLimit)
        }
    }


}
