import { Show } from "../hooks/queries/shows"

interface ImgParams {
  baseUrl: string,
  defaultImage: string,
  imageSizes: Array<{ w: number; h: number }>,
  w2HRatio: number,
  needsPadding: boolean,
}

export type {ImgParams};

export default function showImgParams(show: Show): ImgParams | undefined {

    if (!show.sizes) {
      return undefined;
    }
 
    const baseUrl: string = `${process.env.NEXT_PUBLIC_IMAGE_SERVER_URI}/shows/${show.slug}/${show.slug}`;

    const defaultImage: string = `${process.env.NEXT_PUBLIC_IMAGE_SERVER_URI}/shows/${show.slug}/${show.slug}.jpg`;

    const imageSizes: Array<{ w: number; h: number }> = JSON.parse(show.sizes ?? '[{"w":0,"h":0}]');

    const w2HRatio: number = imageSizes[0]['w'] / imageSizes[0]['h'];

    const needsPadding: boolean = w2HRatio < 16 / 9 ? true : false;

    return{ baseUrl, defaultImage, imageSizes, w2HRatio, needsPadding};
};
    
