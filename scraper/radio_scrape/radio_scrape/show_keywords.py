from time import time
from pprint import pprint

from sklearn.feature_extraction.text import (
    TfidfVectorizer,
    CountVectorizer,
    ENGLISH_STOP_WORDS,
)
from spacy.lang.fr.stop_words import STOP_WORDS as FRENCH_STOP_WORDS
from sklearn.decomposition import NMF, MiniBatchNMF, LatentDirichletAllocation

from scraper_MySQL import MySQL


class TagShows:

    def __init__(self):

        self.get_shows()

        self.corpus = [
            self.process_corpus_item(show["desc"])
            for show in self.shows
            if show["desc"]
        ]

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
        curated_unwanted_keywords = [
            "focus",
            "light",
            "deep",
            "city",
            "tracks",
            "air",
            "experience",
            "releases",
            "friday",
            "sets",
            "past",
            "share",
            "tunes",
            "saturday",
            "help",
            "just",
            "john",
            "collection",
            "hours",
            "listeners",
            "happening",
            "broadcast",
            "special",
            "room",
            "sonic",
            "good",
            "years",
            "89",
            "introduction",
            "reintroduction",
            "context",
            "forever",
            "la",
            "hear",
            "hottest",
            "guaranteed",
            "produced",
            "longest",
            "running",
            "left",
            "make",
            "merrier",
            "pot",
            "scene",
            "culture",
            "featuring",
            "ll",
            "content",
            "dreaming",
            "middle",
            "host",
            "sounds",
            "people",
            "tune",
            "play",
            "features",
            "playing",
            "audio",
            "come",
            "favourite",
            "welcome",
            "art",
            "sources",
            "roll",
            "round",
            "hour",
            "including",
            "start",
            "right",
            "breakfast",
            "interspersed",
            "ve",
            "bring",
            "present",
            "plays",
            "ears",
            "showcasing",
            "tuesday",
            "concept",
            "podcast",
            "genre",
            "takes",
            "let",
            "know",
            "point",
            "culture" "featuring",
            "movie",
            "shows",
            "journey",
            "hosted",
            "global",
            "open",
            "history",
            "hits",
            "happen",
            "theme",
            "sound",
            "explore",
            "program",
            "join",
            "love",
            "cfru",
            "ciut",
            "late",
            "fm",
            "description",
            "new",
            "music",
            "day",
            "today",
            "morning",
            "today",
            "radio",
            "weekly",
            "best",
            "artists",
            "night",
            "canada",
            "week",
            "soon",
            "time",
            "musical",
            "coming",
            "listen",
            "early",
            "like",
            "recorded",
            "monday",
            "wednesday",
            "thursday",
            "friday",
            "sunday",
            "saturday",
            "tuesday",
            "host",
            "hosts",
            "show",
            "shows",
            "broadcast",
            "broadcasts",
            "broadcasting",
            "broadcasted",
            "broadcasters",
            "93",
            "85",
            "better",
            "en",
            "bought",
            "recorded",
            "look",
            "goal",
            "rich",
            "featured",
            "campus",
            "related",
            "released",
            "episode",
            "established",
            "involved",
            "sorts",
            "self",
            "com",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "noon",
            "format",
            "prime",
            "brought",
            "year",
            "days",
            "place",
            "pm",
            "am",
            "weekend",
            "daily",
            "wide",
            "heard",
            "youll",
            "ill",
            "dedicated",
            "decades",
            "artist",
            "downtown",
            "home",
            "performers",
            "stations",
            "talent",
            "school",
            "cfrus",
            "ckut",
            "ckuts",
            "weve",
            "youve",
            "thing",
            "things",
            "thursdays",
            "working",
            "taking",
            "todays",
            "want",
            "whats",
            "played",
            "month",
            "monthly",
            "october",
            "midnight",
            "listen",
            "listening",
            "listeners",
            "listener",
            "june",
            "region",
            "brings",
            "station",
            "includes",
            "presenting",
            "onehour",
            "going",
            "fund",
            "20",
            "provides",
            "soundtrack",
            "50",
            "covering",
            "need",
            "way",
            "ca",
            "highlights",
            "collectivelyhosted",
            "forward",
            "face",
            "known",
            "generally",
            "lens",
            "really",
            "expect",
            "member",
            "big",
            "online",
            "end",
            "5fm",
            "emphasis",
            "connect",
            "song",
            "started",
            "dose",
            "great",
            "english",
            "necessary",
            "near",
            "aim",
            "feature",
            "celebrating",
            "showcase",
            "general",
            "contact",
            "founded",
            "presented",
            "members",
            "based",
            "airwaves",
            "topics",
            "set",
            "team",
            "airing",
        ]
        stop_words = ENGLISH_STOP_WORDS.union(curated_unwanted_keywords)
        stop_words = FRENCH_STOP_WORDS.union(stop_words)

        # vectorize keywords and frequency across all show descriptions
        self.vec = CountVectorizer(
            ngram_range=(1, 1), min_df=3, stop_words=stop_words, strip_accents="unicode"
        ).fit(self.corpus)

    def global_tags_2_db(self):
        bag_of_words = self.vec.transform(self.corpus)
        sum_words = bag_of_words.sum(axis=0)

        # list of word-frequency pairs
        words_freq = [
            (word, int(sum_words[0, idx]))
            for word, idx in self.vec.vocabulary_.items()
            if word.isdigit() == False
        ]
        words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)

        keywords_only = [word_score[0] for word_score in words_freq]

        mySQL = MySQL()
        mySQL.insert_all_tags(words_freq, keywords_only)

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

        tag_id_map = {tag["tag"]: tag["id"] for tag in self.all_tags}

        for show in self.shows:
            print("\n\n****", show["showName"], "***\n\n")

            if show["desc"]:

                show_scored = self.vec.transform(
                    [self.process_corpus_item(show["desc"])]
                )

                terms = self.vec.get_feature_names_out()

                scores = show_scored.toarray().flatten().tolist()

                data = list(zip(terms, scores))

                pprint(tag_id_map)

                # create tuples of show id, tag id, frequency for db
                db_data = [
                    (show["id"], tag_id_map[item[0]], item[1])
                    for item in data
                    if item[1] > 0 and item[0].isdigit() == False
                ]
                matched_tag_ids = [data_item[1] for data_item in db_data]
                print(matched_tag_ids)
                self.show_tags_2_db(db_data, show["id"], matched_tag_ids)

    def process_corpus_item(self, txt):
        # normalize common word pairs, minor variations, and remove special characters
        return (
            txt.lower()
            .replace("'", "")
            .replace("'", "")
            .replace("-", "")
            .replace("!", "")
            .replace("activists", "activism")
            .replace("activist", "activism")
            .replace("airing", "")
            .replace("april", "")
            .replace("august", "")
            .replace("december", "")
            .replace("deep dive", "deepDive")
            .replace("february", "")
            .replace("free form", "freeForm")
            .replace("free-jazz", "freeJazz jazz")
            .replace("green screen", "")
            .replace("grooves", "groove")
            .replace("guelphs", "guelph")
            .replace("hip hop", "hipHop")
            .replace("hip-hop", "hipHop")
            .replace("interviewing", "interview")
            .replace("january", "")
            .replace("july", "")
            .replace("june", "")
            .replace("latin america", "LatinAmerica")
            .replace("march", "")
            .replace("may", "")
            .replace("montreals", "montreal")
            .replace("montréals", "montreal")
            .replace("november", "")
            .replace("october", "")
            .replace("performances", "performance")
            .replace("r & b", "rhythmAndBlues")
            .replace("r&b", "rhythmAndBlues")
            .replace("rarities", "rare")
            .replace("selection", "")
            .replace("september", "")
            .replace("singer songwriters", "singerSongwriters")
            .replace("south africa", "southAfrica")
            .replace("south america", "southAmerica")
            .replace("south asia", "southAsia")
            .replace("south asian", "southAsia")
            .replace("southeast asia", "SoutheastAsia")
            .replace("spoken word", "spokenWord")
            .replace("students", "student")
            .replace("take action", "activism")
            .replace("the environment", "environmental")
            .replace("womens", "women")
        )

    #


# def identify_tags_across_all_shows():
#     mySQL = MySQL()

#     results = mySQL.get_show_descriptions()

#     # Two sets of documents
#     # _corpus contains all documents in your corpus
#     # normalize hip hop, spoken word, and r&b to show up as a single keyword
#     # corpus = [result['desc'].lower().replace("r&b","rhythmAndBlues").replace("r & b","rhythmAndBlues").replace("hip hop","hipHop").replace("hip-hop","hipHop").replace("spoken word","spokenWord") for result in results if result['desc']]
#     corpus = [self.process_corpus_item(result['desc']) for result in results if result['desc']]

#     # corpus = [result['desc'] for result in results if result['desc']]

#     # We don't want common english words or others from our curated list to be used as keywords
#     curated_unwanted_keywords = ['focus','light','deep','city','tracks','air','experience','releases','friday','sets','past','share','tunes','saturday','help','just','john','collection','hours','listeners','happening','broadcast','special', 'room', 'sonic', 'good', 'years', '89','introduction', 'reintroduction', 'context','forever', 'la', 'hear', 'hottest', 'guaranteed', 'produced', 'longest', 'running', 'left', 'make', 'merrier', 'pot', 'scene', 'culture', 'featuring', 'll', 'content', 'dreaming', 'middle', 'host', 'sounds', 'people', 'tune', 'play', 'features', 'playing', 'audio', 'come', 'favourite', 'welcome', 'art', 'sources', 'roll', 'round', 'hour', 'including', 'start', 'right', 'breakfast', 'interspersed', 've', 'bring', 'present', 'plays',  'ears', 'showcasing', 'tuesday', 'concept', 'podcast',  'genre', 'takes', 'let', 'know', 'point','culture''featuring','movie','shows','journey','hosted','global','open','history','hits','happen','theme','sound','explore','program','join','love','cfru','ciut','late','fm','description','new','music','day','today','morning','today',"radio","weekly","best","artists","night","canada","week","soon","time","musical","coming","listen","early"]
#     stop_words = ENGLISH_STOP_WORDS.union(curated_unwanted_keywords)


#     # identify keywords and frequency across all show descriptions
#     vec = CountVectorizer(ngram_range = (1, 1), min_df=3, stop_words=stop_words).fit(corpus)
#     bag_of_words = vec.transform(corpus)
#     sum_words = bag_of_words.sum(axis=0)

#     # list of word-frequency pairs
#     words_freq = [(word, int(sum_words[0, idx])) for word, idx in vec.vocabulary_.items() ]
#     words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True)

#     keywords_only = [word_score[0] for word_score in words_freq ]
#     print(words_freq)
#     mySQL.insert_all_tags(words_freq)

#     for result in results:
#         print("\n\n****",result['showName'],"***\n\n")
#         if result['desc']:
#             show_scored = vec.transform([result['desc'].lower().replace("r&b","rhythmAndBlues").replace("r & b","rhythmAndBlues").replace("hip hop","hipHop").replace("hip-hop","hipHop")])

#             terms = vec.get_feature_names_out()
#             # print(terms)

#             scores = show_scored.toarray().flatten().tolist()

#             data = list(zip(terms,scores))

#             matched_tags = [(item[0], item[1]) for item in data if item[1] > 0]
#             print(matched_tags)


if __name__ == "__main__":
    tagger = TagShows()
    tagger.global_tags_2_db()
    tagger.tag_each_show()
