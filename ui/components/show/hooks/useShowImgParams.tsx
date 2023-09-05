import { Show } from "../../../hooks/queries/shows"

export function useShowImgParams(show:Show) {
        // TODO length > 3 required for image not resized as it has empty sizes array
    // Should we have a way to know the size of super small images?

      if(!show.sizes ){return {baseUrl:null, defaultImage:null, imageSizes:null, w2HRatio:null, needsPadding:null}}

      const baseUrl:string = `${process.env.NEXT_PUBLIC_image_server_URI}shows/${show.slug}/${show.slug}`

      //For the sizes attribute in img tag with srcset
      //https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#attr-sizes
        

      const defaultImage:string = `${process.env.NEXT_PUBLIC_image_server_URI}shows/${show.slug}/${show.slug}.jpg`
      console.log(show.showName, show.sizes);

      const imageSizes:Array<{'w':number,'h':number}> = JSON.parse(show.sizes ?? '[{"w":0,"h":0}]')
      
      //Pad if height is greater than width in a 16:9 ratio
      const w2HRatio:number = imageSizes[0]['w']/imageSizes[0]['h'];

      const needsPadding:Boolean = w2HRatio < 16/9 ? true : false;

      return {baseUrl, defaultImage, imageSizes, w2HRatio, needsPadding};
    
  }