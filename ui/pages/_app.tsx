import React, { useState } from "react";
import { useRouter } from "next/router";
import { Hydrate, QueryClient, QueryClientProvider } from "react-query";
import type { AppProps } from "next/app";
import "../styles/globals.scss";
import Layout from "../components/layout/Layout";
import { getShows, showsStaleTime } from "../hooks/queries/shows";
import { getTags, tagsStaleTime } from "../hooks/queries/tags";
import { HydrationProvider} from "react-hydration-provider";
function App({ Component, pageProps }: AppProps) {
  
  const [queryClient] = useState(() => new QueryClient());
  queryClient.setQueryDefaults('shows', { queryFn: getShows, staleTime: showsStaleTime()})
  queryClient.setQueryDefaults('tags', { queryFn: getTags, staleTime: tagsStaleTime()})


  // Because page scolling happens within content div (to maintain header at top of page), we need to update the scroll position of the "#content" div on changing to a new page. If a particular page has already been visited, we can use the scroll position from the previous visit of that specific page. Otherwise, we scroll to the top of the page.
  const router = useRouter();
  const [scrollPositions, setScrollPositions] = useState<{[key: string]: number}>({});
  
  React.useEffect(() => {
    console.log(scrollPositions)
    const handleRouteChange = (url: string) => {
      const contentDiv = document.getElementById("content");
      if (contentDiv) {

        // Save the scroll position of the current page
        const currentUrl = router.asPath;
        console.log('old page', currentUrl)
        const currentScrollPosition = contentDiv.scrollTop;
        setScrollPositions((prev) => ({ ...prev, [currentUrl]: currentScrollPosition }));

      }
    };

    // function to handle scroll position on new page
    const handleNewPageScrollPosition = () => {
      const contentDiv = document.getElementById("content");
      if (contentDiv) {
        console.log('new page', router.asPath)
        // Scroll to the position of the new page
        if(!scrollPositions[router.asPath]) {
        const scrollPosition = scrollPositions[router.asPath] || 0;
        contentDiv.scrollTo(0, scrollPosition);
        }
      }
    };

    // add event listener to save scroll position of current page
    router.events.on("routeChangeStart", handleRouteChange);
    // add event listener to handle scroll position on new page
    router.events.on("routeChangeComplete", handleNewPageScrollPosition);

    // remove event listener on unmount
    return () => {
      router.events.off("routeChangeComplete", handleNewPageScrollPosition);
      router.events.off("routeChangeStart", handleRouteChange);
    }

  }, [router.events, scrollPositions, router.asPath]);

  
  return (
    <QueryClientProvider client={queryClient}>
      <Hydrate state={pageProps.dehydratedState}>
        <HydrationProvider>
          <Layout>
            <Component {...pageProps} />
          </Layout>
        </HydrationProvider>
      </Hydrate>
    </QueryClientProvider>
  );
}

export default App;
