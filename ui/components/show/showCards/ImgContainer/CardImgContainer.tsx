import { Show } from "../../../../hooks/queries/shows";
import PictureTag from "../../../commonElements/PictureTag/PictureTag";
import { useShowImgParams } from "../../hooks/useShowImgParams";
import styles from './CardImgContainer.module.scss'

interface imgContainerProps {
    show:Show,
}

function CardImgContainer ({show}:imgContainerProps) {
    // if(!show.sizes || show.sizes.length < 3 ){return null}

    const {baseUrl, defaultImage, imageSizes, w2HRatio, needsPadding} = useShowImgParams(show);

    // If show.sizes is null, that means we don't actually have the image.
    // So we'll just return null and not render the image.
    if(!show.sizes || !baseUrl || !defaultImage || !imageSizes || !w2HRatio ){return null}

    let displaySizes = "(min-width: 85.375rem) 24.125rem, (min-width: 96rem) 24.875rem, 21rem"; //based on css values for full width of container
    
    // Margin images, that needsPadding will be of different widths and have a different `displaySizes` value. 
    // Let's calculate the display width for the `sizes` attribute in the picture tag.
    //numbers used in calculation rely in css width/height values.
    if (needsPadding){
        const cardBreakPointWidths= [{'bp': 85.375, 'w': 24.125}, {'bp': 96, 'w': 24.875}, {'bp': 0, 'w': 21}]

        const totalVerticalPadding = 24/16; //Based on css px margin. Converted for use with rem
        // const containerHeight = 336/1.77 // Based on css
        // const imgDisplayHeight = containerHeight - totalVerticalPadding;
        // displaySizes = (imgDisplayHeight * w2HRatio)/16 + 'rem';

        // create srcset sizes string using each breakpoint
        let displaySizesArr = Array<string>();
        cardBreakPointWidths.forEach((size)=>{
            const containerHeight = size.w/1.77
            const imgDisplayHeight = containerHeight - totalVerticalPadding;  
            if (size.bp !== 0){

                displaySizesArr.push(`(min-width: ${size.bp}rem) ${imgDisplayHeight * w2HRatio}rem`);
            } else {   
                displaySizesArr.push(`${imgDisplayHeight * w2HRatio}rem`); 
            }
        });
        displaySizes = displaySizesArr.join(', ');

    } 
    // console.log(displaySizes);
    return (
        <div className={`${styles.cardImgContainer} ${needsPadding ? styles.cardImgPadded : styles.cardImgFullWidth}`} >
            <PictureTag
                loading = {undefined} 
                alt="" 
                imageSizes = {imageSizes} 
                baseUrl = {baseUrl} 
                displaySizes = {displaySizes}
                defaultImage = {defaultImage}
                defaultHeight = {imageSizes[0]['h']}
                defaultWidth = {imageSizes[0]['w']}
                />
        </div>
    )
}

export default CardImgContainer;