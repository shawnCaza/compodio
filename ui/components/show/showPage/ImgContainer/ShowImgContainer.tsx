import { Show } from "../../../../hooks/queries/shows";
import PictureTag from "../../../commonElements/PictureTag/PictureTag";
import { showImgParams } from "../../../../functions/showImgParams";
import useAsync from "../../hooks/useAsync";
import styles from './ShowImgContainer.module.scss'

interface imgContainerProps {
    show:Show,
}

async function defineSizes(containerHeights: { height: number, breakpoint: number }[], totalVerticalPadding: number, w2HRatio: number): Promise<string> {
    return new Promise<string>((resolve, reject) => {
        let sizes = '';
        containerHeights.forEach(containerHeight => {
            const imgDisplayHeight = containerHeight.height - totalVerticalPadding;
            let displayWidthEM = (imgDisplayHeight * w2HRatio) / 16;
            //add comma + space to sizes string if not first iteration
            if (sizes.length > 0) { sizes += ', '; };
            //add media query to sizes string
            if (containerHeight.breakpoint > 0) { sizes += `(min-width: ${(containerHeight.breakpoint / 16)}rem) `; };
            sizes += displayWidthEM.toPrecision(3) + 'rem';
        });

        resolve(sizes);
    });
}

function ShowImgContainer ({show}:imgContainerProps) {
    if(!show.sizes || show.sizes.length < 3 ){return null}

    // const {baseUrl, defaultImage, imageSizes, w2HRatio, needsPadding} = useShowImgParams(show);
    var [pendingImgParams, errorImgParams, imgParams] = useAsync(showImgParams, [show]);
 
    if(pendingImgParams){return <div className={`${styles.showImgContainer} ${styles.imgSpacePlaceholder}`} />}
    if(!imgParams){return null}
    
    const {baseUrl, defaultImage, imageSizes, w2HRatio, needsPadding} = imgParams;

    // If show.sizes is null, that means we don't actually have the image.
    if(!show.sizes || !baseUrl || !defaultImage || !imageSizes || !w2HRatio  ){return null}

   

    const totalVerticalPadding = 40; //Based on css margin
    const containerHeights = [{'height':281, "breakpoint":1366}, {'height':180, "breakpoint":0}] // Based on css
    
    // const displaySizes = defineSizes(containerHeights, totalVerticalPadding, w2HRatio);
    var [pendingSizes, errorSizes, displaySizes] = useAsync(defineSizes, [containerHeights, totalVerticalPadding, w2HRatio]);

    if(pendingSizes){return <div className={`${styles.showImgContainer} ${styles.imgSpacePlaceholder}`} />}
    if(!displaySizes){return null}

    

         
    return (
        <div className={`${styles.showImgContainer} ${needsPadding ? styles.showImgPadded : ''}`} >
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

export default ShowImgContainer;