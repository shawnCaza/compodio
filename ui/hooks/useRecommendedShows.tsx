import { useShowsQuery } from '../hooks/queries/shows';


export function useRecommendedShows() {
    const shows = useShowsQuery();
    // console.log(shows);
    if(!shows){return null}
    const recIds = ['99', '146', '200', '83', '100', '112', '175', '164', '135', '206', '94', '219', '166']

    // select 10 random shows from the list of recommended shows in random order
    const recShowsSuffled = shows.filter(show => {return recIds.includes(show.id)}).sort(() => Math.random() - 0.5).slice(0,10)
    
    const serverRecShows = shows.filter(show => {return recIds.slice(0,10).includes(show.id)})
    
    return {recShowsSuffled, serverRecShows};
  }