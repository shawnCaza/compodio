import { Show } from "../hooks/queries/shows"

export function showImgParams(show: Show): Promise<{
  baseUrl: string | null;
  defaultImage: string | null;
  imageSizes: Array<{ w: number; h: number }> | null;
  w2HRatio: number | null;
  needsPadding: boolean | null;
}> {
  return new Promise((resolve, reject) => {
    if (!show.sizes) {
      resolve({
        baseUrl: null,
        defaultImage: null,
        imageSizes: null,
        w2HRatio: null,
        needsPadding: null,
      });
    }

    const baseUrl: string = `${process.env.NEXT_PUBLIC_image_server_URI}shows/${show.slug}/${show.slug}`;

    const defaultImage: string = `${process.env.NEXT_PUBLIC_image_server_URI}shows/${show.slug}/${show.slug}.jpg`;

    const imageSizes: Array<{ w: number; h: number }> = JSON.parse(show.sizes ?? '[{"w":0,"h":0}]');

    const w2HRatio: number = imageSizes[0]['w'] / imageSizes[0]['h'];

    const needsPadding: boolean = w2HRatio < 16 / 9 ? true : false;

    resolve({ baseUrl, defaultImage, imageSizes, w2HRatio, needsPadding });
  });
}
    
