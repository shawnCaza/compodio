import { Show } from "../../../../hooks/queries/shows";
import PictureTag from "../../../commonElements/PictureTag/PictureTag";
import useAsync from "../../hooks/useAsync";
import showImgParams from "../../../../functions/showImgParams";
import styles from './CardImgContainer.module.scss'

interface imgContainerProps {
    show:Show,
}

function CardImgContainer ({show}:imgContainerProps) {
    // baseUrl, defaultImage, imageSizes, w2HRatio, needsPadding, displaySizes
    const [pending, error, imgParams]: [boolean, Error | undefined, any] = useAsync(showImgParams, [show]);

    // If show.sizes is null, that means we don't actually have the image.
    // So we'll just return null and not render the image.
    if(!show.sizes || error ){return null}

    if (pending) {
        // Still calculating image params.
        return <div className={`${styles.cardImgContainer} ${styles.cardImgParamsPending}`}></div>
    }
    return (
        <div className={`${styles.cardImgContainer} ${imgParams.needsPadding ? styles.cardImgPadded : styles.cardImgFullWidth}`} >
            <PictureTag
                loading = {undefined} 
                alt="" 
                imageSizes = {imgParams.imageSizes} 
                baseUrl = {imgParams.baseUrl} 
                displaySizes = {imgParams.displaySizes}
                defaultImage = {imgParams.defaultImage}
                defaultHeight = {imgParams.imageSizes[0]['h']}
                defaultWidth = {imgParams.imageSizes[0]['w']}
                />
        </div>
    )
}

export default CardImgContainer;