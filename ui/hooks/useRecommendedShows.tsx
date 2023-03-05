import { useShowsQuery } from '../hooks/queries/shows';


export function useRecommendedShows() {
    const shows = useShowsQuery();
    console.log(shows);
    if(!shows){return null}
    const recIds = ['99', '146', '200', '83', '100', '112', '175', '164', '135', '206']
    const recShows = shows.filter(show => {return recIds.includes(show.id)})
    return recShows
  }