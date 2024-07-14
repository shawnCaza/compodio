import Card from "../card/Card";
import { A11y, Navigation } from 'swiper/modules';
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import 'swiper/css/a11y';
import cardCollectionStyles from './CardCollection.module.scss';
import cardStyles from '../card/Card.module.scss';
 
interface cardCollectionProps {
    cardDataCollection: any[];
    CardContent: React.ComponentType<any>;
    singleRow?: boolean;
}

function CardCollection({cardDataCollection, CardContent, singleRow=false}:cardCollectionProps) {
    if (singleRow) {
        return (
            <div className={cardCollectionStyles.swiperContainer}>
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
                    className={cardCollectionStyles.swiper}
                >
                    {cardDataCollection.map(currentCard => (
                        <SwiperSlide key={currentCard.id} className={cardStyles.card}>
                            <CardContent currentCard={currentCard} />
                        </SwiperSlide>
                    ))}
                </Swiper>
            </div>
        )
    } 
    return (
        <div className={cardCollectionStyles.cardContainer} >
            {cardDataCollection.map(currentCard => (
                <Card key={currentCard.id} cardStyles={cardStyles} >
                    <CardContent currentCard={currentCard} />
                </Card>
            ))}
        </div>
    )
} 


export default CardCollection;