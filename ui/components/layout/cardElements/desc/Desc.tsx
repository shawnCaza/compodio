import styles from './Desc.module.scss'

interface descType{
    desc: string | null,
    approxLength: number
}

function makeSnippet(txt:string, approxLength:number){
    // approxLength is the approximate max-length of our snippet.
    // If txt is longer than max, will return string up to approxLength + remainder of any word that might be cut.
    
    if (txt.trim().indexOf(" ", approxLength) > 0){ 
        //Need to shorten txt
        // Spit at first space after 'lengthApprox' characters
        var txtShort = txt.substring(0, txt.trim().indexOf(" ", approxLength));

        // In case snippet ends in period or comma, we want to remove them before adding ellipse 
        // TODO relevant to remove other punctuation?
        txtShort = txtShort.replace(/[\.,]$/,"");
        txtShort += "…";
        
        return txtShort

    } else {
        //Description does not need to be shortened.  
        return txt

    }
}

function CardDesc({desc, approxLength=0}:descType) {
    // Adds show despription. If approxLength is greater than 0, will shorten description rounding up to the nearest space after approxLength.

    var displayDesc:string;

    if(!desc) {
        displayDesc = "No description available."
    } else if(approxLength > 0) {
        displayDesc = makeSnippet(desc, approxLength);
    } else {
        displayDesc = desc;
    }

    return (
        <>
            <div className={styles.desc}>{displayDesc}</div>
        </>
    )
} 

export default CardDesc;