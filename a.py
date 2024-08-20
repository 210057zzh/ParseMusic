import glob
import mutagen
import sqlite3
from alive_progress import alive_bar
import errno


def prepare_sqllite():
    log = open("log.txt", "w", encoding="utf-8")
    con = sqlite3.connect("songs.db")
    cur = con.cursor()
    cur.execute(
        """ 
        DROP TABLE IF EXISTS songs
        """
    )
    cur.execute("CREATE TABLE songs(title, artist, path)")
    files = glob.glob("yinyue/**/*", recursive=True)
    with alive_bar(len(files)) as bar:
        for file in files:
            try:
                tags = mutagen.File(file, easy=True)
                if tags is None:
                    continue
                cur.executemany(
                    "INSERT INTO songs VALUES(?, ?, ?)",
                    [(tags["title"][0], tags["artist"][0], file[7:])],
                )
                pass
            except mutagen.MutagenError as error:
                if isinstance(error.args[0], PermissionError):
                    continue
                else:
                    log.write(
                        f"An exception occurred while processing {file} : {error}\n"
                    )
                    log.flush()
            except KeyError as error:
                cur.executemany(
                    "INSERT INTO songs VALUES(?, ?, ?)",
                    [(file[7:], "dummy artist", file[7:])],
                )
            except Exception as error:
                log.write(f"An exception occurred while processing {file} : {error}\n")
                log.flush()
            finally:
                bar()
    con.commit()
    cur.close()
    con.close()


def read_playlist():
    con = sqlite3.connect("songs.db")
    cur = con.cursor()
    with open("gudian.txt", "r", encoding="utf-8") as playlist:
        songs = [line.rstrip() for line in playlist]
        for song in songs:
            title = song.rsplit("-", 1)[0].strip()
            res = cur.execute(
                "select path from songs where title like ?",
                ("%" + title + "%",),
            ).fetchall()
            pass
    pass
    con.commit()
    cur.close()
    con.close()


# prepare_sqllite()

read_playlist()
