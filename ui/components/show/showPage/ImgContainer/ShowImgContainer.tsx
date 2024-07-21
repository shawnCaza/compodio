import { Show } from "../../../../hooks/queries/shows";
import PictureTag from "../../../commonElements/PictureTag/PictureTag";
import showImgParams from "../../../../functions/showImgParams";
import { ImgParams } from "../../../../functions/showImgParams";
import useAsync from "../../hooks/useAsync";
import styles from './ShowImgContainer.module.scss'

interface imgContainerProps {
    show:Show,
}

async function defineDisplaySizes(imgParams: ImgParams):Promise<string> {
    return new Promise<string>((resolve, reject) => {
        if (!imgParams) {
            reject(new Error('No image Parameters available'));
        }
        const w2HRatio = imgParams.w2HRatio;
        const totalVerticalPadding = 40; //Based on css margin
        const containerHeights = [{'height':281, "breakpoint":1366}, {'height':180, "breakpoint":0}] // Based on css
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

    var [pendingImgParams, errorImgParams, imgParams] = useAsync(showImgParams, [show]);
     
    var [pendingDisplaySizes, errorDisplaySizes, displaySizes] = useAsync(defineDisplaySizes, [imgParams]);

    if (errorImgParams) return null

    // If we're still waiting for the image parameters, return a placeholder div.
    if(pendingImgParams || pendingDisplaySizes){return <div className={`${styles.showImgContainer}`} />}
        
    const {baseUrl, defaultImage, imageSizes, w2HRatio, needsPadding} = imgParams;

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