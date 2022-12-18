from time import time

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, ENGLISH_STOP_WORDS
from sklearn.decomposition import NMF, MiniBatchNMF, LatentDirichletAllocation

from etc_MySQL import MySQL

class TagShows:
    
    def __init__(self):
        
        self.get_shows()

        self.corpus = [self.process_corpus_item(show['desc']) for show in self.shows if show['desc']]

        self.create_count_vect()

    def get_shows(self):
        """retrieves show data from DB"""

        mySQL = MySQL()
        self.shows = mySQL.get_show_descriptions()

    def get_all_tags(self):
        """retrieves all from all_tags table in DB"""

        mySQL = MySQL()
        self.all_tags = mySQL.get_all_tags()

    def create_count_vect(self):
        """creates a countVectorizer from the corpus"""

        # We don't want common english words or others from our curated list to be used as keywords
        curated_unwanted_keywords = ['focus','light','deep','city','tracks','air','experience','releases','friday','sets','past','share','tunes','saturday','help','just','john','collection','hours','listeners','happening','broadcast','special', 'room', 'sonic', 'good', 'years', '89','introduction', 'reintroduction', 'context','forever', 'la', 'hear', 'hottest', 'guaranteed', 'produced', 'longest', 'running', 'left', 'make', 'merrier', 'pot', 'scene', 'culture', 'featuring', 'll', 'content', 'dreaming', 'middle', 'host', 'sounds', 'people', 'tune', 'play', 'features', 'playing', 'audio', 'come', 'favourite', 'welcome', 'art', 'sources', 'roll', 'round', 'hour', 'including', 'start', 'right', 'breakfast', 'interspersed', 've', 'bring', 'present', 'plays',  'ears', 'showcasing', 'tuesday', 'concept', 'podcast',  'genre', 'takes', 'let', 'know', 'point','culture''featuring','movie','shows','journey','hosted','global','open','history','hits','happen','theme','sound','explore','program','join','love','cfru','ciut','late','fm','description','new','music','day','today','morning','today',"radio","weekly","best","artists","night","canada","week","soon","time","musical","coming","listen","early"]
        stop_words = ENGLISH_STOP_WORDS.union(curated_unwanted_keywords)

        # vectorize keywords and frequency across all show descriptions
        self.vec = CountVectorizer(ngram_range = (1, 1), min_df=3, stop_words=stop_words).fit(self.corpus)

    def global_tags_2_db(self):
        bag_of_words = self.vec.transform(self.corpus)
        sum_words = bag_of_words.sum(axis=0) 

        # list of word-frequency pairs 
        words_freq = [(word, int(sum_words[0, idx])) for word, idx in self.vec.vocabulary_.items() ]
        words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True)

        keywords_only = [word_score[0] for word_score in words_freq ] 
        print(words_freq)
        mySQL = MySQL()
        mySQL.insert_all_tags(words_freq)

    def show_tags_2_db(self, data_for_db, show_id, tag_ids):

        mySQL = MySQL()
        # remove any tags no longer assigned to the show
        if len(tag_ids):
            mySQL.remove_outdated_show_tags(show_id, tag_ids)

        # add new tags
        if len(data_for_db):
            mySQL.insert_show_tags(data_for_db)

    def tag_each_show(self):
        """Iterates through show results and identifies tags for each one"""

        self.get_all_tags()

        tag_id_map = {tag['tag']: tag['id'] for tag in self.all_tags}

        for show in self.shows:
            print("\n\n****", show['showName'],"***\n\n")
            
            if show['desc']:

                show_scored = self.vec.transform([self.process_corpus_item(show['desc'])]) 

                terms = self.vec.get_feature_names_out()

                scores = show_scored.toarray().flatten().tolist()

                data = list(zip(terms,scores))

                # create tuples of show id, tag id, frequency for db
                db_data = [(show['id'], tag_id_map[item[0]], item[1]) for item in data if item[1] > 0]
                matched_tag_ids = [data_item[1] for data_item in db_data]
                print(matched_tag_ids)
                self.show_tags_2_db(db_data, show['id'], matched_tag_ids)

    def process_corpus_item(self, txt):
        # normalize hip hop, spoken word, and r&b to show up as a single keyword 
        # corpus = [result['desc'].lower().replace("r&b","rhythmAndBlues").replace("r & b","rhythmAndBlues").replace("hip hop","hipHop").replace("hip-hop","hipHop").replace("spoken word","spokenWord") for result in results if result['desc']]
        return txt.lower().replace("r&b","rhythmAndBlues").replace("r & b","rhythmAndBlues")

def identify_tags_across_all_shows():
    mySQL = MySQL()

    results = mySQL.get_show_descriptions()

    # Two sets of documents
    # _corpus contains all documents in your corpus 
    # normalize hip hop, spoken word, and r&b to show up as a single keyword 
    # corpus = [result['desc'].lower().replace("r&b","rhythmAndBlues").replace("r & b","rhythmAndBlues").replace("hip hop","hipHop").replace("hip-hop","hipHop").replace("spoken word","spokenWord") for result in results if result['desc']]
    corpus = [result['desc'].lower().replace("r&b","rhythmAndBlues").replace("r & b","rhythmAndBlues") for result in results if result['desc']]

    # corpus = [result['desc'] for result in results if result['desc']]

    # We don't want common english words or others from our curated list to be used as keywords
    curated_unwanted_keywords = ['focus','light','deep','city','tracks','air','experience','releases','friday','sets','past','share','tunes','saturday','help','just','john','collection','hours','listeners','happening','broadcast','special', 'room', 'sonic', 'good', 'years', '89','introduction', 'reintroduction', 'context','forever', 'la', 'hear', 'hottest', 'guaranteed', 'produced', 'longest', 'running', 'left', 'make', 'merrier', 'pot', 'scene', 'culture', 'featuring', 'll', 'content', 'dreaming', 'middle', 'host', 'sounds', 'people', 'tune', 'play', 'features', 'playing', 'audio', 'come', 'favourite', 'welcome', 'art', 'sources', 'roll', 'round', 'hour', 'including', 'start', 'right', 'breakfast', 'interspersed', 've', 'bring', 'present', 'plays',  'ears', 'showcasing', 'tuesday', 'concept', 'podcast',  'genre', 'takes', 'let', 'know', 'point','culture''featuring','movie','shows','journey','hosted','global','open','history','hits','happen','theme','sound','explore','program','join','love','cfru','ciut','late','fm','description','new','music','day','today','morning','today',"radio","weekly","best","artists","night","canada","week","soon","time","musical","coming","listen","early"]
    stop_words = ENGLISH_STOP_WORDS.union(curated_unwanted_keywords)


    # identify keywords and frequency across all show descriptions
    vec = CountVectorizer(ngram_range = (1, 1), min_df=3, stop_words=stop_words).fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0) 

    # list of word-frequency pairs 
    words_freq = [(word, int(sum_words[0, idx])) for word, idx in vec.vocabulary_.items() ]
    words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True)

    keywords_only = [word_score[0] for word_score in words_freq ] 
    print(words_freq)
    mySQL.insert_all_tags(words_freq)

    for result in results:
        print("\n\n****",result['showName'],"***\n\n")
        if result['desc']:
            show_scored = vec.transform([result['desc'].lower().replace("r&b","rhythmAndBlues").replace("r & b","rhythmAndBlues").replace("hip hop","hipHop").replace("hip-hop","hipHop")]) 

            terms = vec.get_feature_names_out()
            # print(terms)

            scores = show_scored.toarray().flatten().tolist()

            data = list(zip(terms,scores))

            matched_tags = [(item[0], item[1]) for item in data if item[1] > 0]
            print(matched_tags)


if __name__ == '__main__':  
    tagger = TagShows()
    # tagger.global_tags_2_db()
    tagger.tag_each_show()
