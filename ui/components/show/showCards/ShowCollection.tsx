import Card from "../../layout/cardElements/card/Card";
import CardCollection from "../../layout/cardElements/cardCollection/CardCollection";
import CardContent from "./cardContent/CardContent";
import { Show } from "../../../hooks/queries/shows";
import { A11y, Navigation } from 'swiper/modules';
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import 'swiper/css/a11y';
import styles from './ShowCollection.module.scss';
import cardCollectionStyles from '../../layout/cardElements/cardCollection/CardCollection.module.scss';
import cardStyles from '../../layout/cardElements/card/Card.module.scss';

interface showCollectionProps {
    shows: Show[];
    singleRow?: boolean;
}

function ShowCollection({shows, singleRow=false}:showCollectionProps) {
    if (singleRow) {
        return (
            <div className={styles.swiperContainer}>
                <Swiper
                    cssMode={true}
                    mousewheel={true}
                    modules={[A11y, Navigation]}
                    navigation={true}
                    spaceBetween={10}
                    slidesPerView={1.1}
                    breakpoints={{
                        0: {enabled: false},
                        400: {slidesPerView: 'auto', enabled: false},
                        1069: {enabled: true,
                            slidesPerView: 'auto',
                            slidesPerGroup: 3
                        }
                    }}
                    className={styles.swiper}
                >
                    {shows.map(currentShow => (
                        <SwiperSlide key={currentShow.id} className={cardStyles.card}>
                            <CardContent currentShow={currentShow} />
                        </SwiperSlide>
                    ))}
                </Swiper>
            </div>
        )
    }
    return (
        <CardCollection cardCollectionStyles={cardCollectionStyles} >
            {shows.map(currentShow => (
                <Card key={currentShow.id} cardStyles={cardStyles} >
                    <CardContent currentShow={currentShow} />
                </Card>
            ))}
        </CardCollection>
    )
} 


export default ShowCollection;