import { useShowsQuery, getShows, Show } from '../../../hooks/queries/shows';
import Container from '../../layout/cardElements/container/Container';
import Card from '../../layout/cardElements/card/Card';
import Heading from '../../layout/cardElements/heading/Heading';
import EpDate from '../epDate/EpDate';
import Desc from '../../layout/cardElements/desc/Desc';
import FeedLinks from '../podcastFeedLinks/feedLinks/FeedLinks';
import ShowLink from '../ShowLink';
import GradientBg from '../../commonElements/GradientBg';
import CardImgContainer from './ImgContainer/CardImgContainer';
import TagsContainer from '../../layout/cardElements/TagsContainer/TagsContainer';
import ContentSection from '../../layout/ContentSection/contentSection';

import { Swiper, SwiperSlide } from 'swiper/react';
import { Pagination, A11y } from 'swiper/modules';
import 'swiper/swiper-bundle.min.css';

import styles from "./ShowCards.module.scss";

interface ShowCardsProps {
  shows: Show[];
  singleRow?: boolean;  // Should the collection of cards be displayed on a single horizontally scrolling row? 
}

function ShowCards({ shows, singleRow = false }: ShowCardsProps) {
  if (!shows) {
    return null;
  }

  const cardContent = (show: Show) => (
    <Card key={show.id}>
      <div>
        <Heading>
          <div className={styles.epDate}>
            <EpDate dtStr={show.newestEpDate} />
          </div>
          <ShowLink slug={show.slug}>
            <h3 className={styles.title}>{show.showName}</h3>
          </ShowLink>
        </Heading>
        <GradientBg colours={show.dom_colours}>
          <ShowLink slug={show.slug}>
            <CardImgContainer show={show} />
          </ShowLink>
        </GradientBg>
      </div>
      <ContentSection heading='Subscribe:' tag='h5' centered={true} spacing='tight'>
        <FeedLinks showId={show.id} slug={show.slug} showName={show.showName} extFeeds={show.extFeeds} />
      </ContentSection>
      <div className={styles.desc}>
        <Desc desc={show.desc} approxLength={125} />
        <span>
          <ShowLink slug={show.slug}>
            &nbsp;More.
          </ShowLink>
        </span>
      </div>
      {show.tagIds && <TagsContainer currentTagIds={JSON.parse(show.tagIds)} maxTags={3} />}
    </Card>
  );

  return (
    <>
      {singleRow ? (
        <Swiper
          modules={[Pagination, A11y]}
          pagination={{ clickable: true }}
          spaceBetween={10}
          slidesPerView={1.1}
          breakpoints={{
            400: {slidesPerView: 'auto'}
          }}
          freeMode={true}
        >
          {shows.map(show => (
            <SwiperSlide key={show.id} className={styles.swiperSlide}>
              {cardContent(show)}
            </SwiperSlide>
          ))}
        </Swiper>
      ) : (
        <Container>
          {shows.map(show => cardContent(show))}
        </Container>
      )}
    </>
  );
}

export default ShowCards;
