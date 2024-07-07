import Card from "../../layout/cardElements/card/Card";
import CardCollection from "../../layout/cardElements/container/CardCollection";
import CardContent from "./CardContent";
import { Show } from "../../../hooks/queries/shows";
import { Pagination, A11y } from 'swiper/modules';
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import 'swiper/css/pagination';
import 'swiper/css/a11y';
import cardCollectionStyles from '../../layout/cardElements/container/CardCollection.module.scss';
import cardStyles from '../../layout/cardElements/card/Card.module.scss';

interface showCollectionProps {
    shows: Show[];
    singleRow?: boolean;
}

function ShowCollection({shows, singleRow=false}:showCollectionProps) {
    if (singleRow) {
        return (
            <Swiper
            className={cardCollectionStyles.cardContainer}         
            modules={[Pagination, A11y]}
            pagination={{ clickable: true }}
            spaceBetween={10}
            slidesPerView={1.1}
            breakpoints={{
              400: {slidesPerView: 'auto'}
            }}>
                {shows.map(currentShow => (
                    <SwiperSlide key={currentShow.id} className={cardStyles.card}>
                        
                        <CardContent currentShow={currentShow} />
                    </SwiperSlide>
                ))}
            </Swiper>
        )
    }
    return (
        <CardCollection >
            {shows.map(currentShow => (
                <Card key={currentShow.id}>
                    <CardContent currentShow={currentShow} />
                </Card>
            ))}
        </CardCollection>
    )
} 


export default ShowCollection;