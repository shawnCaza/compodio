interface ShowCardsProps{
    loading: 'eager' | 'lazy' | undefined,
    alt: string,
    imageWidths: Array<number>,
    baseUrl: string,
    displaySizes: string,
    defaultImage: string,
    defaultWidth: number,
    defaultHeight: number
  }


function PictureTag({loading, alt, imageWidths, baseUrl, displaySizes, defaultImage, defaultWidth, defaultHeight}:ShowCardsProps) {


        let webpSrcSetArray = [];
        let jpgSrcSetArray = [];
        for (const size of imageWidths) {
            webpSrcSetArray.push(baseUrl + '_' + size + ".webp " + size + "w");
            jpgSrcSetArray.push(baseUrl + '_' + size + ".jpg " + size + "w");
        }

        return (
            <>
                <picture>
                    <source srcSet={webpSrcSetArray.toString()} sizes={displaySizes} type="image/webp"/>
                    <source srcSet={jpgSrcSetArray.toString()} sizes={displaySizes} type="image/jpeg"/>
                    <img src={defaultImage} alt={alt} loading={loading}  width="defaultWidth" height="defaultHeight" />
                </picture>
            </>
        )
    }


export default PictureTag;