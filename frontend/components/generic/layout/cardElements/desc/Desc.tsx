import { makeSnippet } from '../../../../../functions/utility/txtSnippet';

interface descType{
    desc: string | null,
    approxLength: number
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
            {displayDesc}
        </>
    )
} 

export default CardDesc;