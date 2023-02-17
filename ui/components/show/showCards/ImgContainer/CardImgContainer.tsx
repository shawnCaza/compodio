import { Show } from "../../../../hooks/queries/shows";
import PictureTag from "../../../commonElements/PictureTag/PictureTag";
import { useShowImgParams } from "../../hooks/useShowImgParams";
import styles from './CardImgContainer.module.scss'

interface imgContainerProps {
    show:Show,
}

function CardImgContainer ({show}:imgContainerProps) {
    if(!show.sizes || show.sizes.length < 3 ){return null}

    const {baseUrl, defaultImage, imageSizes, w2HRatio, needsPadding} = useShowImgParams(show);


    let displaySizes = "21em"; //based on css value for full width of container
    // Margin images will be of different widths and have a different `displaySizes` value. 
    // Let's calculate the display width for the `sizes` attribute in the picture tag.
    //numbers used in calculation rely in css width/height values.
    if (needsPadding){
        const totalVerticalPadding = 24; //Based on css margin
        const containerHeight = 336/1.77 // Based on css
        const imgDisplayHeight = containerHeight - totalVerticalPadding;
        displaySizes = (imgDisplayHeight * w2HRatio)/16 + 'em';
        
    } 
    // console.log(displaySizes);
    return (
        <div className={`${styles.cardImgContainer} ${needsPadding ? styles.cardImgPadded : ''}`} >
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