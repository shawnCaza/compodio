import { useShowsQuery } from '../hooks/queries/shows';
import { shuffleArray } from '../functions/utility/shuffleArray';
import { Show } from '../hooks/queries/shows'

interface randomShowResults{
  recShowsShuffled?:Show[],
}
export type {randomShowResults}

export function useRecommendedShows() {
    const shows = useShowsQuery();

    if (!shows ){
      return [];
    }

    const recIds = ['1608','99', '146', '200', '83', '100', '112', '175', '164', '135', '206', '94', '219', '166', '79', '118', '132', '150']

    // select 10 random shows from the list of recommended shows in random order
    const recShowsShuffled = shuffleArray(shows.filter(show => {return recIds.includes(show.id)})).slice(0,10)
    
    // const serverRecShows = shows.filter(show => {return recIds.slice(0,10).includes(show.id)})


    return {recShowsShuffled};
  }