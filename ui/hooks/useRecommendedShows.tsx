import { useShowsQuery } from '../hooks/queries/shows';
import { shuffleArray } from '../functions/utility/shuffleArray';
import { Show } from '../hooks/queries/shows'


export interface randomShowResults {
  recShowsShuffled: Show[];
}

export function useRecommendedShows() {
    const shows = useShowsQuery();

    if (!shows ){
      return;
    }

    const recIds = ['99', '146', '200', '83', '112', '175', '206', '94', '166', '79', '118', '132', '150','270053','270105', '270056', '102180', '270042', '270114', '269984', '270097', '270100', '269938', '159']

    // select 10 random shows from the list of recommended shows in random order
    const recShowsShuffled = shuffleArray(shows.filter(show => {return recIds.includes(show.id)})).slice(0,10)
    
    // const serverRecShows = shows.filter(show => {return recIds.slice(0,10).includes(show.id)})


    return recShowsShuffled;
  }