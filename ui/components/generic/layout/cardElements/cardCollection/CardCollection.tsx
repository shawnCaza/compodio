import Card from "../card/Card";
import { A11y, Navigation } from 'swiper/modules';
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import 'swiper/css/a11y';
import styles from './CardCollection.module.scss';
 
interface cardCollectionProps {
    cardDataCollection: any[];
    CardContent: React.ComponentType<any>;
    singleRow?: boolean;
}

function CardCollection({cardDataCollection, CardContent, singleRow=false}:cardCollectionProps) {
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
                        400: { slidesPerView: 'auto', enabled: false },
                        768: { slidesPerView: 'auto', spaceBetween: 15 },
                        1024: {slidesPerView: 3,},
                        1069: {enabled: true,
                            slidesPerView: 'auto',
                            slidesPerGroup: 3,
                        },
                        1200: { slidesPerView: 'auto', slidesPerGroup: 3, spaceBetween: 20 },
                        1720: {slidesPerView: 'auto',slidesPerGroup: 4, spaceBetween: 20 }
                    }}
                    className={styles.swiper}
                >
                    {cardDataCollection.map(currentCard => (
                        <SwiperSlide key={currentCard.id} className={styles.swiperSlide}>
                            <CardContent currentCard={currentCard} />
                        </SwiperSlide>
                    ))}
                </Swiper>
            </div>
        )
    } 
    return (
        <div className={styles.cardContainer} >
            {cardDataCollection.map(currentCard => (
                <Card key={currentCard.id} >
                    <CardContent currentCard={currentCard} />
                </Card>
            ))}
        </div>
    )
} 


export default CardCollection;