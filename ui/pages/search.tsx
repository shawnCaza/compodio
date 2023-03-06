import React from "react";
import Fuse from "fuse.js";
import { dehydrate, QueryClient} from 'react-query';
import ContentSection from "../components/layout/ContentSection/contentSection";
import ShowCards from "../components/show/showCards/ShowCards";
import { useShowsQuery, getShows } from "../hooks/queries/shows";
import { getTags } from "../hooks/queries/tags";
import { useFuseOptions } from "../components/search/fuse/hooks/useFuseOptions";

interface searchProps {
  searchTerm: string
}

export async function getServerSideProps(context) {
  
  const searchTerm = context.query.s;

  const queryClient = new QueryClient();
  await Promise.all([
    queryClient.prefetchQuery('tags', getTags),
    queryClient.prefetchQuery('shows', getShows)
  ]);
  

    return {props: {searchTerm: searchTerm}}
    // will be passed to the page component as props
  }

  export default function Search({searchTerm}:searchProps){
    const shows = useShowsQuery();
    if(!shows){return null}

    const fuse = new Fuse(shows, useFuseOptions());
    const searchResults = Object.values(fuse.search(searchTerm));
    //create array using only the item prop from each object in the searchResults array
    const searchItems = searchResults.map((result) => result.item);




    return (
        <ContentSection heading={`Searching for: ${searchTerm}`} tag='h1'>
          <ShowCards shows={searchItems} />
        </ContentSection>
      );
}