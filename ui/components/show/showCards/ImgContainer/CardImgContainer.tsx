import { Show } from "../../../../hooks/queries/shows";
import PictureTag from "../../../commonElements/PictureTag/PictureTag";

import styles from './CardImgContainer.module.scss'

interface imgContainerProps {
    show:Show,
}

function CardImgContainer ({show}:imgContainerProps) {

    // TODO length > 3 required for image not resized as it has empty sizes array
    // Should we have a way to know the size of super small images?
    if(!show.sizes || show.sizes.length < 3 ){return null}

    const baseUrl = `${process.env.NEXT_PUBLIC_image_server_URI}shows/${show.slug}/${show.slug}`

    //For the sizes attribute in img tag with srcset
    //https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#attr-sizes
      

    const defaultImage = `${process.env.NEXT_PUBLIC_image_server_URI}shows/${show.slug}/${show.slug}.jpg`
    const imageSizes:Array<{'w':number,'h':number}> = JSON.parse(show.sizes)
    
    //Pad if height is greater than width in a 16:9 ratio
    const w2HRatio = imageSizes[0]['w']/imageSizes[0]['h'];

    const needsPadding = w2HRatio < 16/9 ? true : false;

    let displaySizes = "222px"; //based on css value for full width of container
    // Margin images will be of different widths and have a different `displaySizes` value. 
    // Let's calculate the display width for the `sizes` attribute in the picture tag.
    //numbers used in calculation rely in css width/height values.
    if (needsPadding){
        const totalVerticalPadding = 24; //Based on css margin
        const containerHeight = 124 // Based on css
        const imgDisplayHeight = containerHeight - totalVerticalPadding;
        displaySizes = imgDisplayHeight * w2HRatio + 'px';
        
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