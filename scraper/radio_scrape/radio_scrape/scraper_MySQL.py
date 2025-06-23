import json
import logging
import os
import time
from dataclasses import asdict

import mysql.connector as mysql
from dotenv import load_dotenv


class MySQL:  # ------------------------------------------------------
    def connect(self):
        logging.getLogger("mysql.connector").setLevel(logging.WARNING)
        load_dotenv(".env.local", override=True)

        conn = mysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT"),
            auth_plugin="mysql_native_password",
            use_pure=True,
        )
        # create cursor
        cursor = conn.cursor(dictionary=True)
        # cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        return conn, cursor

    # ------------------------------------------------------
    def close(self, cursor, conn):
        # close cursor
        cursor.close()

        # close connection to MySQL
        conn.close()

    # ------------------------------------------------------
    def use_compodio_DB(self, cursor):
        """Expects open connection."""
        # select DB
        cursor.execute("USE compodio")

    # ---------------------------------------------------------
    def insert_multiple(self, mySql_insert_query, data_for_db):

        # connect to MySQL
        conn, cursor = self.connect()

        self.use_compodio_DB(cursor)

        cursor.executemany(mySql_insert_query, data_for_db)
        conn.commit()
        print(cursor.rowcount, "Record inserted successfully")

    def insert_episode(self, episode):
        # connect to MySQL
        conn, cursor = self.connect()

        self.use_compodio_DB(cursor)

        query = """INSERT INTO episodes (show_id, ep_date, mp3, file_size) VALUES (%s, %s, %s, %s)"""
        cursor.execute(
            query,
            (
                episode["show_id"],
                episode["ep_date"],
                episode["mp3"],
                episode["file_size"],
            ),
        )

        try:
            conn.commit()
        except:
            print(
                cursor.statement,
            )

        time.sleep(0.2)
        self.close(cursor, conn)

    # ------------------------------------------------------

    def insert_show(self, show):
        # connect to MySQL
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)

        query = """INSERT INTO shows (`showName`, `source`, `img`, `desc`, `host`, `internal_link`, `ext_link`, `email`, `duration`, `slug`)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) as new
                 ON DUPLICATE KEY UPDATE
                `showName` = new.`showName`, `source` = new.`source`, `img` = new.`img`, `desc` = new.`desc`, `host` = new.`host`, `internal_link` = new.`internal_link`, `ext_link` = new.`ext_link`, `email` = new.`email`, `duration` = new.`duration`, `slug` = new.`slug`;
                """
        # print("""INSERT INTO shows (showName, source, img, desc, host, internal_link, ext_link, email) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')""" % (show['showName'], show['source'], show['img'], show['desc'], show['host'], show['internal_link'], show['ext_link'], show['email']))

        cursor.execute(
            query,
            (
                show["showName"],
                show["source"],
                show["img"],
                show["desc"],
                show["host"],
                show["internal_link"],
                show["ext_link"],
                show["email"],
                show["duration"],
                show["slug"],
            ),
        )

        try:
            conn.commit()
        except:
            print(
                cursor.statement,
            )

        time.sleep(0.2)
        self.close(cursor, conn)

    # ---------------------------------------------------------
    def insert_ext_feed_link(self, ext_feed_link):
        # connect to MySQL
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)

        query = """INSERT INTO ext_feed_links (show_id, link, feedType) VALUES (%s, %s, %s) as new
                ON DUPLICATE KEY UPDATE
                `show_id` = new.`show_id`, `link` = new.`link`, `feedType` = new.`feedType`;
                """

        cursor.execute(
            query,
            (
                ext_feed_link["show_id"],
                ext_feed_link["link"],
                ext_feed_link["feed_type"],
            ),
        )

        try:
            conn.commit()
        except:
            print(
                cursor.statement,
            )
        time.sleep(0.2)
        self.close(cursor, conn)

    # ---------------------------------------------------------
    def insert_all_tags(self, data_for_db, keywords_only: list):

        query = """INSERT INTO all_tags (`tag`, `freq`)
                VALUES (%s, %s) as new
                ON DUPLICATE KEY UPDATE
                `tag` = new.`tag`, `freq` = new.`freq`;
                """

        # connect to MySQL
        conn, cursor = self.connect()

        self.use_compodio_DB(cursor)

        cursor.executemany(query, data_for_db)
        conn.commit()
        print(cursor.rowcount, "Records inserted successfully")

        # remove record from all_tags if it is not in keywords_only
        query = f"""DELETE FROM all_tags WHERE tag NOT IN ('{"', '".join(keywords_only)}')"""
        print(query)
        cursor.execute(query)
        conn.commit()
        print(cursor.rowcount, "Records deleted successfully")

    # ---------------------------------------------------------

    def insert_show_tags(self, data_for_db):

        query = """INSERT INTO show_tags (`show_id`, `tag_id`, `frequency`)
                VALUES (%s, %s, %s) as new
                ON DUPLICATE KEY UPDATE
                `frequency` = new.`frequency`;
                """

        # connect to MySQL
        conn, cursor = self.connect()

        self.use_compodio_DB(cursor)

        cursor.executemany(query, data_for_db)
        conn.commit()
        print(cursor.rowcount, "Records inserted successfully")

    # ------------------------------------------------------

    def get_all_tags(self):
        # connect to MySQL
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)
        # select data
        cursor.execute(f"""select * from all_tags""")

        return cursor.fetchall()

    # ------------------------------------------------------

    def get_shows_by_source(self, source):
        # connect to MySQL
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)
        # select data
        cursor.execute(f"""select * from shows where source='{source}'""")

        return cursor.fetchall()

    # ------------------------------------------------------

    def get_shows_ext_sites(self):
        # connect to MySQL
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)
        # select data
        cursor.execute(
            """
            SELECT id, showName, ext_link 
            FROM shows
            WHERE ext_link != ''
        """
        )

        return cursor.fetchall()

    # ------------------------------------------------------

    def get_show_descriptions(self):
        # connect to MySQL
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)
        # select data
        cursor.execute("""select `id`, `showName`, `desc` from shows""")

        return cursor.fetchall()

    def get_newest_ep_by_source(self, source):
        # connect to MySQL
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)
        # select data
        cursor.execute(
            f"""with date_ranked_eps AS (
                                select episodes.id, mp3, show_id, ep_date,
                                    rank() OVER (PARTITION BY show_id
                                                    ORDER BY ep_date DESC
                                                ) AS `Rank`
                                FROM episodes
                                left join shows
                                on shows.id = episodes.show_id
                                where shows.source = '{source}'
                            )
                            SELECT id, mp3, show_id, ep_date
                            FROM date_ranked_eps
                            WHERE `Rank` = 1"""
        )

        return cursor.fetchall()

    def remove_old_eps_by_show(self, show_id, where_clause=None):
        # connect to MySQL
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)

        query = f"""delete from episodes where show_id = {show_id}"""
        if where_clause:
            query += f""" and {where_clause}"""
        print("query", query)

        cursor.execute(
            query,
        )

        try:
            conn.commit()
        except:
            print(
                cursor.statement,
            )

        time.sleep(0.2)
        self.close(cursor, conn)

    def remove_outdated_show_tags(self, show_id, tag_ids):
        # connect to MySQL
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)

        query = f"""delete from show_tags where show_id = {show_id} and `tag_id` not in ({','.join(str(id) for id in tag_ids)})"""
        print("query", query)

        cursor.execute(
            query,
        )

        try:
            conn.commit()
        except:
            print(
                cursor.statement,
            )

        time.sleep(0.2)
        self.close(cursor, conn)

    # ------------------------------------------------------
    def get_show_images(self):

        show_images = self.get_query(
            """
                SELECT id, slug, img as image_url, last_updt
                FROM shows
                LEFT JOIN show_images ON show_id = id
            """
        )

        return show_images

    def show_images_to_sync(self):
        show_images = self.get_query(
            """
                SELECT slug
                FROM shows
                LEFT JOIN show_images ON show_id = id
                WHERE synched = 0
            """
        )
        return show_images

    def update_synced_show_images(self, show_slugs):
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)

        cursor.execute(
            f"""UPDATE show_images
                SET synched = 1
                WHERE show_id IN (SELECT id FROM shows WHERE slug IN ('{"', '".join(show_slugs)}'))
            """
        )

        conn.commit()

    def insert_image(self, props):

        # connect to MySQL
        conn, cursor = self.connect()

        self.use_compodio_DB(cursor)
        query = """
                    INSERT INTO show_images (show_id, last_updt, sizes, dom_colours, synched)
                    VALUES (%s, %s, %s, %s, %s)  as new
                    ON DUPLICATE KEY UPDATE
                    `last_updt` = new.`last_updt`,
                    `sizes` = new.`sizes`,
                    `dom_colours` = new.`dom_colours`,
                    `synched` = new.`synched`;
            """
        cursor.execute(
            query,
            (
                props.show_id,
                props.last_modified,
                json.dumps(asdict(props)["sizes"]),
                json.dumps(props.dom_colours),
                False,
            ),
        )
        conn.commit()
        # print(cursor.statement,)

    # ------------------------------------------------------
    def get_query(self, query):

        # connect to MySQL
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)
        # select data
        cursor.execute(query)

        return cursor.fetchall()

    # ---------------------------------------------------------
    def insert_ep_ai_details(self, ep_id, desc):
        # connect to MySQL
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)

        query = """UPDATE episodes
                set ai_desc = %s
                WHERE id = '%s';
                """

        cursor.execute(query, (desc, ep_id))

        try:
            conn.commit()
        except:
            print(
                cursor.statement,
            )
        self.close(cursor, conn)

        # ---------------------------------------------------------

    def set_show_lang(self, show_id, lang):
        # connect to MySQL
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)

        query = """UPDATE shows
                set lang = %s
                WHERE id = %s;
                """

        cursor.execute(query, (lang, show_id))

        try:
            conn.commit()
        except:
            print(
                cursor.statement,
            )
        self.close(cursor, conn)

    def get_shows_without_ext_feed_link_by_feedType(self, feedType):
        conn, cursor = self.connect()
        self.use_compodio_DB(cursor)

        cursor.execute(
            f"""select * from shows where id not in (select show_id from ext_feed_links where feedType = '{feedType}')""",
        )

        return cursor.fetchall()
