import { Show } from "../../../../../hooks/queries/shows";
import PictureTag from "../../../../generic/commonElements/PictureTag/PictureTag";
import showImgParams from "../../../../../functions/showImgParams";
import { ImgParams } from "../../../../../functions/showImgParams";
import styles from './CardImgContainer.module.scss'


interface ImgContainerProps {
    show:Show,
}

function defineDisplaySizes(imgParams:ImgParams) {

        const w2HRatio = imgParams.w2HRatio;
        const needsPadding = imgParams.needsPadding;

        if(!needsPadding){
            const displaySizes = "(min-width: 85.375rem) 24.125rem, (min-width: 96rem) 24.875rem, 21rem"; //based on css values for full width of container
            return displaySizes;
        }
        
        // Margin images, that needsPadding will be of different widths and have a different `displaySizes` value. 
        // Let's calculate the display width for the `sizes` attribute in the picture tag.
        //numbers used in calculation rely in css width/height values.
        
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

        return displaySizesArr.join(', ');
};

function CardImgContainer ({show}:ImgContainerProps) {
    // baseUrl, defaultImage, imageSizes, w2HRatio, needsPadding, displaySizes
    const imgParams = showImgParams(show);
    if (!imgParams) return null;
    const displaySizes:string = defineDisplaySizes(imgParams);
    
    return (
        <div className={`${styles.cardImgContainer} ${imgParams.needsPadding ? styles.cardImgPadded : styles.cardImgFullWidth}`} >
            <PictureTag
                loading = {undefined} 
                alt="" 
                imageSizes = {imgParams.imageSizes} 
                baseUrl = {imgParams.baseUrl} 
                displaySizes = {displaySizes}
                defaultImage = {imgParams.defaultImage}
                defaultHeight = {imgParams.imageSizes[0]['h']}
                defaultWidth = {imgParams.imageSizes[0]['w']}
                />
        </div>
    )
}

export default CardImgContainer;