import { useRouter } from 'next/router'
import Fuse from 'fuse.js'
import { Show, useShowsQuery} from "../../../hooks/queries/shows"
import ComboBoxSearch from './ComboBox/ComboBox';
import { useFuseOptions } from './fuse/hooks/useFuseOptions';
import {useMenuStore} from '../../../stores/menuStore';

interface fuseResult{
  item: Show;
  score: number;
  refIndex: number;
}

export default function Search() {

  const shows = useShowsQuery() ?? [];
  const router = useRouter()
  const fuse = new Fuse(shows, useFuseOptions());

  
  function handleSearch(inputValue:string) {
    // Called from useComboBox, to filter shows based on input,
    // Then slice just the top results.
    let searchResults: Array<Fuse.FuseResult<Show> | String>  = Object.values(fuse.search(inputValue)).slice(0,5);
    
    //add inputValue to the end of the array if not empty
    if(inputValue !== ''){
      searchResults.push(inputValue)
    }

    return searchResults;
  }

  function handleSelection(selectedItem:fuseResult){
    // Called from useComboBox, to handle the selection of a show
    // from the search results.
   
    // close the menu in case it's open. Othewise, the menu will
    // hide the content of the new page.
    useMenuStore.getState().closeMenu();

    // if string, then it's the search input value, so we need to
    // navigate to the search page.
    if(typeof selectedItem === 'string'){
      const href = `/search?s=${selectedItem}`;
      router.push(href)
      return
    }

    const href = `/shows/${selectedItem.item.slug}`;
    router.push(href)
  }

  return (

    <ComboBoxSearch handleSearch={handleSearch} handleSelection={handleSelection} />
  )
}
