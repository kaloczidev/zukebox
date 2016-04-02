"""
zukebox: Main module

Copyright 2015, Tamas Domok
Licensed under MIT.
"""

from contextlib import contextmanager
import youtube_dl
import re


class DownloadError(Exception):
    pass


class Logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


class Youtube:

    options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': Logger(),
    }

    def extract_info(self, youtube_url: str):
        with self.handle_errors():
            with youtube_dl.YoutubeDL(self.options) as ydl:
                info = ydl.extract_info(youtube_url, download=False)

                def check_info():
                    if not info:
                        return False
                    for check in ('title', 'duration', 'thumbnail'):
                        if check not in info:
                            return False
                    return True

                if not check_info():
                    raise DownloadError("Could not extract song details; response='{response}'"
                                        .format(response=str(info)))

                return {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnails', [{}])[0].get('url', ''),
                }

    def download_audio(self, youtube_url: str, output: str):
        with self.handle_errors():
            options = self.options.copy()
            options['outtmpl'] = output
            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([youtube_url])

    @contextmanager
    def handle_errors(self):
        try:
            yield
        except DownloadError:
            raise
        except youtube_dl.DownloadError as e:
            raise DownloadError("Could not download song; error='{error}'".format(error=str(e)))
        except:
            raise DownloadError("Could not download song; error='unknown'")

    @classmethod
    def get_id(cls, youtube_url: str):
        result = re.match("^(?:http(?:s)?://)?(?:www\.)?(?:m\.)?(?:youtu\.be/|youtube\.com"
                          "/(?:(?:watch)?\?(?:.*&)?v(?:i)?=|(?:embed|v|vi|user)/))([^\?&\"'>]+)", youtube_url)
        return result.group(1) if result else None
