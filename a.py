import glob
import mutagen
import sqlite3
from alive_progress import alive_bar
import errno

playlist_name = "zhong"


def prepare_sqllite():
    log = open("log.txt", "w", encoding="utf-8")
    con = sqlite3.connect("songs.db")
    cur = con.cursor()
    cur.execute(
        """ 
        DROP TABLE IF EXISTS songs
        """
    )
    cur.execute("CREATE TABLE songs(title, artist, path, file_name, ext)")
    files = glob.glob("yinyue/**/*", recursive=True)
    with alive_bar(len(files)) as bar:
        for file in files:
            try:
                if "." not in file:
                    continue
                [file_name, ext] = file[7:].rsplit(".", 1)
                tags = mutagen.File(file, easy=True)
                if tags is None:
                    continue
                cur.executemany(
                    "INSERT INTO songs VALUES(?, ?, ?, ?, ?)",
                    [(tags["title"][0], tags["artist"][0], file[7:], file_name, ext)],
                )
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
                    "INSERT INTO songs VALUES(?, ?, ?, ?, ?)",
                    [(file[7:], "dummy artist", file[7:], file_name, ext)],
                )
            except Exception as error:
                log.write(f"An exception occurred while processing {file} : {error}\n")
                log.flush()
            finally:
                bar()
    con.commit()
    cur.close()
    con.close()


def prepare_playlist():
    con = sqlite3.connect("songs.db")
    cur = con.cursor()
    log = open("log.txt", "w", encoding="utf-8")
    with open(f"{playlist_name}.txt", "r", encoding="utf-8") as playlist:
        songs = [line.rstrip() for line in playlist]
        result = []
        for song in songs:
            if len(song) == 0:
                continue
            [title, artist] = song.rsplit("-", 1)
            title = title.strip()
            artist = artist.strip()
            result.append(
                cur.execute(
                    "select path from songs where title like ? order by case when artist like ? then 1 else 99 end asc,case when ext = 'flac' then 1 else 99 end asc, length(title) asc",
                    ("%" + title + "%", artist),
                ).fetchall()
            )
            if len(result[-1]) == 0:
                result.pop()
                log.write(f"{title} not found\n")
        playlist_file = open(f"{playlist_name}.m3u8", "w", encoding="utf-8")
        playlist_file.write("#EXTM3U\n")
        for song in result:
            playlist_file.write("#EXT-X-RATING:0\n")
            playlist_file.write(song[0][0] + "\n")
    con.commit()
    cur.close()
    con.close()


# prepare_sqllite()

prepare_playlist()
