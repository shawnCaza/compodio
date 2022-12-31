import { useSnippet } from "../../../hooks/utility/txtSnippet"

interface descType{
    desc: string | null
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