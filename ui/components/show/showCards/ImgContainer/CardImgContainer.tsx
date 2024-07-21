import { Show } from "../../../../hooks/queries/shows";
import PictureTag from "../../../commonElements/PictureTag/PictureTag";
import useAsync from "../../hooks/useAsync";
import showImgParams from "../../../../functions/showImgParams";
import styles from './CardImgContainer.module.scss'

interface imgContainerProps {
    show:Show,
}

interface imgParams {
    baseUrl: string,
    defaultImage: string,
    imageSizes: Array<{ w: number; h: number }>,
    w2HRatio: number,
    needsPadding: boolean,
    displaySizes: string,
}

function CardImgContainer ({show}:imgContainerProps) {
    // baseUrl, defaultImage, imageSizes, w2HRatio, needsPadding, displaySizes
    const [pending, error, imgParams]: [boolean, Error | undefined, imgParams | undefined] = useAsync(showImgParams, [show]);
    
    if (error) return null

    if (pending || !imgParams) return (<div className={`${styles.cardImgContainer} ${styles.cardImgParamsPending}`}></div>)

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