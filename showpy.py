#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Ver: 0.6

from time import sleep
import libtorrent as lt
import feedparser
import tempfile
import shutil
import mmap
import md5

# Global Vars
path = "/home/torrents/"
path_cache = "/home/showpy/"
url = "http://showrss.info/rss.php?user_id=######"
feed = feedparser.parse(url)

for item in feed['items']:
    title = item['title']
    id = item['id']
    key = md5.new(id).hexdigest()
    link = item['links'][0]['href']

    with open(path_cache + 'cache.dat', "r") as k:
        s = mmap.mmap(k.fileno(), 0, access=mmap.ACCESS_READ)

    if s.find(key) == -1:
        print "Found new EP: " + title

        tempdir = tempfile.mkdtemp()
        ses = lt.session()
        params = {
                    'save_path': tempdir,
                    'duplicate_is_error': True,
                    'storage_mode': lt.storage_mode_t(2),
                    'paused': False,
                    'auto_managed': True,
                    'duplicate_is_error': True
        }
        handle = lt.add_magnet_uri(ses, link, params)
        print("Downloading Metadata (this may take a while)")

        while (not handle.has_metadata()):
            try:
                sleep(1)
            except KeyboardInterrupt:
                print("Aborting...")
                ses.pause()
                print("Cleanup dir " + tempdir)
                shutil.rmtree(tempdir)
                sys.exit(0)
                ses.pause()
                print("Done")

        torinfo = handle.get_torrent_info()
        torfile = lt.create_torrent(torinfo)

        with open(path_cache + 'cache.dat', "a+") as k:
            k.write(key + "\n")

        with open(path + title + ".torrent", "wb") as f:
            f.write(lt.bencode(torfile.generate()))

        print("Saving torrent file here : " + title + " ...")
        print("Saved! Cleaning up dir: " + tempdir)

        ses.remove_torrent(handle)
        shutil.rmtree(tempdir)
