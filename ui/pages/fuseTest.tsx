import Fuse from 'fuse.js'
import { Show, useShowsQuery } from '../hooks/queries/shows';
import ComboBoxSearch from '../components/search/ComboBoxSearch';
import { useFuseOptions } from '../components/search/fuse/hooks/useFuseOptions';

interface fuseResult{
  item: Show;
  score: number;
  refIndex: number;
}

export default function Home() {


  const shows = useShowsQuery();
  if(!shows){return null}

  
  const fuse = new Fuse(shows, useFuseOptions());

  
  function handleSearch(inputValue:string) {

    const searchResults = Object.values(fuse.search(inputValue));
    return searchResults;
    
  }

  return (

    <ComboBoxSearch handleSearch={handleSearch} />
  )
}
