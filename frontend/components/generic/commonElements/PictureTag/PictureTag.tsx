import styles from './PictureTag.module.scss'

interface PictureTagProps{
    loading: 'eager' | 'lazy' | undefined,
    alt: string,
    imageSizes: Array<{'w':number,'h':number}>,
    baseUrl: string,
    displaySizes: string,
    defaultImage: string,
    defaultWidth: number,
    defaultHeight: number
  }


function PictureTag({loading, alt, imageSizes, baseUrl, displaySizes, defaultImage, defaultWidth, defaultHeight}:PictureTagProps) {


        let webpSrcSetArray = [];
        let jpgSrcSetArray = [];
        for (const size of imageSizes) {
            webpSrcSetArray.push(`${baseUrl}_${size['w']}.webp ${size['w']}w`);
            jpgSrcSetArray.push(`${baseUrl}_${size['w']}.jpg ${size['w']}w`);
        }

        return (
            <>
                <picture >
                    <source srcSet={webpSrcSetArray.toString()} sizes={displaySizes} type="image/webp"/>
                    <source srcSet={jpgSrcSetArray.toString()} sizes={displaySizes} type="image/jpeg"/>
                    <img className={styles.cardImg} src={defaultImage} alt={alt} loading={loading}  width={`${defaultWidth}px`} height={`${defaultHeight}px`} />
                </picture>
            </>
        )
    }


export default PictureTag;