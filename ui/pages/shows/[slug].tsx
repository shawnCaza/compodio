import { useRouter } from 'next/router'
import Link from 'next/link';
import { dehydrate, QueryClient} from 'react-query';
import { Server, Client } from "react-hydration-provider";

import {GoGlobe} from 'react-icons/go';
import {CiClock2} from 'react-icons/ci';
import {IoPeopleSharp} from 'react-icons/io5';
import {IoTimeSharp} from 'react-icons/io5';

import GradientBg from '../../components/commonElements/GradientBg';
import ShowImgContainer from '../../components/show/showPage/ImgContainer/ShowImgContainer';
import RssLink from '../../components/show/podcastFeedLinks/rssLink/RssLink';
import EpDate from '../../components/show/epDate/EpDate';
import { useShowLength } from '../../components/show/hooks/useShowLength';
import { useRecommendedShows } from '../../hooks/useRecommendedShows';
import ContentSection from '../../components/layout/ContentSection/contentSection';
import CardCollection from '../../components/layout/cardElements/cardCollection/CardCollection';
import CardContent from '../../components/show/showCards/cardContent/CardContent';
import FeedLinks from '../../components/show/podcastFeedLinks/feedLinks/FeedLinks'

import { useShowsQuery, Show } from '../../hooks/queries/shows';
import { getTags } from '../../hooks/queries/tags';
import TagsContainer from '../../components/layout/cardElements/TagsContainer/TagsContainer';

import styles from './showsPage.module.scss'



// export async function getServerSideProps() {
//     const queryClient = new QueryClient();

//     await Promise.all([
//       queryClient.prefetchQuery('tags', getTags),
//       queryClient.prefetchQuery('shows', getShows)
//     ]);
  
//     return {
//       props: {
//         dehydratedState: dehydrate(queryClient),
//       },
//     }
//   }

interface LinkIconProps {
  icon: React.ReactNode;
  label: string;
  txt: string;
  link?: string;
}

function LinkIcon({icon, label, txt, link=undefined }:LinkIconProps){
  return (
    <div className={styles.iconAndTextContainer}>
      
          <span className={styles.linkIcon} role='presentation'>{icon}</span>
          <span className='screen-reader-text'>{label}:</span> 
          {link && <a className={styles.iconTxt} href={link} target='_blank' rel="noreferrer">{txt}</a> }
          {!link && <span className={styles.iconTxt}>{txt}</span>}
         
    </div>
  )
}

export default function ShowPage() {
  const router = useRouter()
  const querySlug = router.query.slug as string
  const shows = useShowsQuery();
  const show = shows?.find(show => show.slug === querySlug);
  const showLength = useShowLength(show?.duration);
  // wrap show.desc in paragraph tags if not already present
  const htmlDesc = show?.desc && show.desc.match(/^<p>/) ? show.desc : `<p>${show?.desc}</p>`;
  
  const recShowsShuffled:Show[]|undefined = useRecommendedShows();
  if (!show){
    return null;
  }

  return (
    <>
    <div className={styles.detailAndImageWrapper}>

      <div className={styles.showImgWrapper}>
          <ShowImgContainer show={show} />
      </div> 

      <div className={styles.showDetails}>
        
        <h1>{show.showName}</h1>
        
        <ContentSection heading='Subscribe:' tag='h5' centered={true} spacing='tight'>
            <FeedLinks
              showId={show.id}
              slug={show.slug}
              showName={show.showName}
              extFeeds={show.extFeeds}
            />
        </ContentSection>
        

        {show.desc &&

          <div className={styles.desc} dangerouslySetInnerHTML={{__html:htmlDesc}}  />
        }
        <div className={styles.iconDetailsList}>
          {/* <LinkIcon icon={<IoCalendarClearSharp/>} label='Latest Episode' txt={<EpDate dtStr={show.newestEpDate}/>} /> */}
          
          
          {show.host && <LinkIcon icon={<IoPeopleSharp/>} label='Host' txt={show.host} />}
          
          <LinkIcon icon={<GoGlobe/>} label='Website' txt={`${show.source.toUpperCase()}`} link={show.internal_link} />
      
          
          {showLength && 
          <LinkIcon icon={<IoTimeSharp/>} label={'Episode Length'} txt={showLength} />
          }
        </div>
        {show.tagIds &&
          <TagsContainer currentTagIds={JSON.parse(show.tagIds)} maxTags={null} />
        }
      </div>



    </div>
    <ContentSection heading='Recommended' tag='h2'>

        {recShowsShuffled &&
          <CardCollection cardDataCollection={recShowsShuffled} CardContent={CardContent} singleRow={true} />         
        }
    </ContentSection>
    </>
  )
}