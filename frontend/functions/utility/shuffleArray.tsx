// From https://stackoverflow.com/a/12646864
export function shuffleArray(arrayForShuffle: any[]) {
        for (let i = arrayForShuffle.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [arrayForShuffle[i], arrayForShuffle[j]] = [arrayForShuffle[j], arrayForShuffle[i]];
        }  
        return arrayForShuffle;
  }