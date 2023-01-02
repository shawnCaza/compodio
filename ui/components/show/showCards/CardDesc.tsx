import { useSnippet } from "../../../hooks/utility/txtSnippet"

interface descType{
    desc: string | null
}


function CardDesc({desc}:descType) {
    
    var descShort;

    if(!desc) {
        descShort = "No description available."
    } else {
        descShort = useSnippet(desc, 170);
    }

    return (
        <>
            <div>{descShort}</div>
        </>
    )
} 

export default CardDesc;