import { useShowsQuery, getShows } from '../../../hooks/queries/shows';
import EpDate from '../epDate';
import CardDesc from './CardDesc';
import FeedUrl from '../showFeed';

function ShowCardsContainer() {

    const shows = useShowsQuery();

    if (!shows){
      return null;
    } 
    // console.log(shows[0]);

    return (
        <>
        {shows.map((show) =>

          <div className='showCard' key={show.id }>

            <EpDate dtStr={show.newestEpDate} />
            <h3>{show.showName}</h3>
            <div>Play button</div>
            <FeedUrl showId={show.id} source={show.source} slug={show.slug} />
            <CardDesc desc={show.desc} />
            
          </div>

        )}
      </>
    )
} 

export default ShowCardsContainer;