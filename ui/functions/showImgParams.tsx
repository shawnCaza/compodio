import { Show } from "../hooks/queries/shows"

export default function showImgParams(show: Show) {

  return new Promise((resolve, reject) => {

    if (!show.sizes) {
      reject(new Error('No image sizes found'));
    }

    const baseUrl: string = `${process.env.NEXT_PUBLIC_image_server_URI}shows/${show.slug}/${show.slug}`;

    const defaultImage: string = `${process.env.NEXT_PUBLIC_image_server_URI}shows/${show.slug}/${show.slug}.jpg`;

    const imageSizes: Array<{ w: number; h: number }> = JSON.parse(show.sizes ?? '[{"w":0,"h":0}]');

    const w2HRatio: number = imageSizes[0]['w'] / imageSizes[0]['h'];

    const needsPadding: boolean = w2HRatio < 16 / 9 ? true : false;

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


    resolve({ baseUrl, defaultImage, imageSizes, w2HRatio, needsPadding, displaySizes });
  });
}
    
