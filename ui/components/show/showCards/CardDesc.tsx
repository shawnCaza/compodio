interface descType{
    desc: string | null
}

function useSnippet(desc:string, lengthApprox:number){
        
    
    if (desc.indexOf(" ", lengthApprox) > 0){ //If after the split point, there is a space 

        // Spit at first space after n(lengthApprox) characters
        var descShort = desc.substring(0, desc.indexOf(" ", lengthApprox));

        //If snippet ends in period, we want to remove period before adding ellipse
        descShort.replace(/\.$/,"");
        descShort += "…";
        
        return descShort

    } else {

        return desc

    }
}

function CardDesc({desc}:descType) {
    
    if(!desc) {return null}

    const descShort = useSnippet(desc, 170)

    return (
        <>
        <div>{descShort}</div>
       </>
    )
} 

export default CardDesc;