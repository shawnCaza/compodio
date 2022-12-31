export function useSnippet(txt:string, lengthApprox:number){
    // lengthApprox is the approximate max-length of our snippet.
    // If txt is longer than max, will return string up to lengthApprox + remainder of any word that might be cut.
    
    if (txt.trim().indexOf(" ", lengthApprox) > 0){ 
        //Need to shorten txt
        // Spit at first space after 'lengthApprox' characters
        var txtShort = txt.substring(0, txt.trim().indexOf(" ", lengthApprox));

        //In case snippet ends in period, we want to remove end-period before adding ellipse
        txtShort.replace(/\.$/,"");
        txtShort += "…";
        
        return txtShort

    } else {
        //Description is already short
        return txt

    }
}