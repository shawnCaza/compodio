import { useRouter } from 'next/router'
import Fuse from 'fuse.js'
import { Show, useShowsQuery } from '../../hooks/queries/shows';
import ComboBoxSearch from './ComboBox';
import { useFuseOptions } from './fuse/hooks/useFuseOptions';

interface fuseResult{
  item: Show;
  score: number;
  refIndex: number;
}

export default function SearchContainer() {


  const shows = useShowsQuery();
  if(!shows){return null}
  const router = useRouter()
  
  const fuse = new Fuse(shows, useFuseOptions());

  
  function handleSearch(inputValue:string) {
    // Called from useComboBox, to filter shows based on input,
    // Then slice just the top results.
    const searchResults = Object.values(fuse.search(inputValue));
    return searchResults.slice(0,7);
  }

  function handleSelection(selectedItem:fuseResult){
    console.log('User selected: ', selectedItem.item.slug);
    const href = `/shows/${selectedItem.item.slug}`;
    router.push(href)
  }

  return (

    <ComboBoxSearch handleSearch={handleSearch} handleSelection={handleSelection} />
  )
}
