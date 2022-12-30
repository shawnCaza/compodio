interface descType{
    desc: string | null
}

function useShortDesc(desc:string){

    const splitPoint = 160;

    if (splitPoint-1 < desc.length){
        // Spit at first space after n characters
        var descShort = desc.substring(0, desc.indexOf(" ", splitPoint));

        //If ends in period, we want to remove period before adding ellipse
        descShort.replace(/\.$/,"");
        descShort += "…";
        
        return descShort

    } else {

        return desc

    }
}

function CardDesc({desc}:descType) {
    
    if(!desc) {return null}

    const descShort = useShortDesc(desc)

    return (
        <>
        <div>{descShort}</div>
       </>
    )
} 

export default CardDesc;