# -*- coding: utf-8 -*-
###
# Copyright (c) 2013, spline
# All rights reserved.
#
#
###

# my libs.
import re
import json
import urllib2
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse, parse_qs
import socket  # capture timeout from socket
import time
import sqlite3 as sqlite  # linkdb.
import os  # linkdb
# extra supybot libs
import supybot.ircmsgs as ircmsgs
import supybot.conf as conf
# supybot libs
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring
url_normalize = utils.python.universalImport('local.url_normalize')

_ = PluginInternationalization('Titler')

LINKDB = conf.supybot.directories.data.dirize("Titler.db")

class LinkDB:
    def __init__(self):
        self.testinit()

    def testinit(self):
        """Test if DB exists. Create if not."""

        if not os.path.exists(LINKDB):
            try:
                F = open(LINKDB, "w")
                F.close()
            except IOError, ioe:
                callbacks.Plugin.log.debug("IOError in DB creation")
        else:
            return
        with sqlite.connect(LINKDB) as conn:
            query = """
            CREATE TABLE IF NOT EXISTS `links` (
                `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                `time` DATETIME NOT NULL,
                `url` TEXT NOT NULL,
                `title` TEXT,
                `channel` TEXT NOT NULL,
                `user` TEXT NOT NULL
            );
            """
            cur = conn.cursor()
            cur.executescript(query)
            cur.commit()

    def __safe_unicode(self, s):
        """Return the unicode representation of obj"""

        try:
            return s.decode("utf-8").encode("utf-8")
        except UnicodeDecodeError:
            return s.decode("iso8859-1").encode("utf-8")

    def add(self, url, title, channel, user):
        """Insert a link into the DB."""

        with sqlite.connect(LINKDB) as conn:
            query = "INSERT INTO links VALUES (NULL, strftime('%s', 'now'), ?, ?, ?, ?)"
            conn.text_factory = str
            results = conn.execute(query, (url, title, channel, user))
        return True

    def check(self, link):
        """Determine whether the link should be fetched again. """

        with sqlite.connect(LINKDB) as conn:
            query = "SELECT title, channel, user FROM links WHERE link LIKE ? AND (strftime('%s', 'now') - last_access) >= ?;"
            results = conn.execute(q, (link, 86400 * 7))
            results = results.fetchone()
        return True if results is not None else False

    def update(self, link):
        """docstring for updateLinkLastseen"""
        with sqlite.connect(LINKDB) as conn:
            q = u"UPDATE links SET last_access=strftime('%s', 'now') WHERE link LIKE ?;"
            results = conn.execute(q, [link])
        return True if results is not None else False


class Titler(callbacks.Plugin):
    """Titler plugin."""
    threaded = True
    noIgnore = True

    def __init__(self, irc):
        self.__parent = super(Titler, self)
        self.__parent.__init__(irc)
        self.encoding = 'utf8'  # irc output.
        self.headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2'}
        self.longUrlCacheTime = time.time()
        self.longUrlServices = None
        if not self.longUrlServices:
            self.longUrlServices = self.getlongurlservices()

    ####################
    # BASE62 FUNCTIONS #
    ####################

    def base62_encode(number):
        """Encode a number in base62 (all digits + a-z + A-Z)."""
        base62chars = string.digits + string.letters
        l = []
        while number > 0:
            remainder = number % 62
            number = number // 62
            l.insert(0, base62chars[remainder])
        return ''.join(l) or '0'

    def base62_decode(str_value):
        """Decode a base62 string (all digits + a-z + A-Z) to a number."""
        base62chars = string.digits + string.letters
        return sum([base62chars.index(char) * (62 ** (len(str_value) - index - 1)) for index, char in enumerate(str_value)])

    #############################
    # INTERNAL HELPER FUNCTIONS #
    #############################

    def numfmt(self, num):
        """Format numbers into human readable units."""
        num = float(num)
        for x in ['','k','m','b']:
            if num < 1000.0 and num > -1000.0:
                return "%3.1f%s" % (num, x)
            num /= 1000.0

    def sizefmt(self, num):
        """Format size information into human readable units."""

        if num is None:
            return 'No size'
        num = int(num)
        for x in ['b','KB','MB','GB']:
            if num < 1024.0:
                return "%3.1f%s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TB')

    #####################
    # LONGURL FUNCTIONS #
    #####################

    def longurlservices(self, irc, msg, args):
        """
        Debug command to test longurl services.
        """
        
        irc.reply("Services: {0}".format(self.getlongurlservices()))
    longurlservices = wrap(longurlservices)

    def getlongurlservices(self):
        """Function to maintain list of shorturl services for resolving
        with cache.
        """

        if self.longUrlServices is not None and (time.time()-self.longUrlCacheTime < 86400):
            return self.longUrlServices
        else:
            self.log.info("Fetching longurl services.")
            req_url = 'http://api.longurl.org/v2/services?format=json'
            req = urllib2.Request(req_url, headers=self.headers)
            services = json.loads(urllib2.urlopen(req).read())
            domains = [item for item in services]
            self.longUrlCacheTime = time.time()
            self.longUrlServices = domains
            return domains

    def longurl(self, surl):
        """Resolve shortened urls into their long form."""
        try:
            req_url = 'http://api.longurl.org/v2/expand?format=json&url=%s' % surl
            req = urllib2.Request(req_url, headers=self.headers)
            lookup = json.loads(urllib2.urlopen(req).read())
            return lookup['long-url']
        except:
            return None

    ########################
    # URL HELPER FUNCTIONS #
    ########################

    def clean(self, msg):
        """Clean up the title."""

        cleaned = msg.translate(dict.fromkeys(range(32))).strip()
        return re.sub(r'\s+', ' ', cleaned)

    def tidyurl(self, url):
        """Tidy up urls for prior to processing."""

        # do utf-8 stuff here? decode.
        url = re.sub('(.*)(http[^\s]*)', '\g<2>', url)
        return url

    #########################
    # HTTP HELPER FUNCTIONS #
    #########################

    def openurl(self, url):
        """Generic http fetcher we can use here."""

        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2')]
        try:
            response = opener.open(url, timeout=5)
        except urllib2.HTTPError, e:
            self.log.info('ERROR: Cannot open: {0} HTTP Error code: {1} '.format(url,e.code))
            return None
        except urllib2.URLError, e:
            self.log.info('ERROR: Cannot open: {0} URL error: {1} '.format(url,e.reason))
            return None
        except socket.timeout:
            self.log.info('ERROR: Cannot open: {0} timed out.'.format(url))
            return None
        return response

    def shortenurl(self, url):
        """Shorten links via bit.ly."""

        if urlparse(url).hostname in ('bit.ly', 'j.mp', 'bitly.com'):  # don't reshorten bitly links.
            return url
        # now try to shorten links.
        try:
            req_url = 'http://api.bitly.com/v3/shorten?login=ehunter&apiKey=R_2aa4785c8c1f87226d329c7cf224a455&longUrl=%s' % (url)
            response=urllib2.urlopen(req_url)
            a = json.loads(response.read())
            if a['status_code'] is not 200:
                self.log.error("Error trying to shorten {0}. bitly api returned {1}".format(url,str(a)))
                return None
            else:
                return a['data']['url']
        except:
            return None

    def vimeotitle(self, url):
        """Fetch information about vimeo videos from API."""

        query = urlparse(url)
        if query.hostname == 'vimeo.com':
            if query.path.startswith('/m/'):
                videoid = query.path.split('/')[2]
            else:
                videoid = query.path.split('/')[1]
        elif query.hostname == 'player.vimeo.com':
            if query.path.startswith('/video/'):
                videoid = query.path.split('/')[2]
        else:
            videoid = None

        # now check.
        if not videoid or not videoid.isdigit():
            self.log.error("Something went wrong finding the vimeo videoid for {0}".format(url))
            return None

        # try loading vimeo api
        try:
            f = urllib2.urlopen('http://vimeo.com/api/v2/video/%s.json' % videoid)
            data = json.load(f)[0]
        except Exception, e:
            self.log.error("ERROR opening vimeo API url message {0} text {1}".format(e,str(f)))

        return "Vimeo Video: {0}  Size: {1}x{2}  Duration: {3}".format(data['title'], data['width'], data['height'],("%dm%ds"%divmod(data['duration'],60)))

    def yttitle(self, url):
        """Try and fetch youtube video information."""

        query = urlparse(url)
        if query.hostname == 'youtu.be':
            videoid = query.path[1:]
        elif query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                videoid = parse_qs(query.query)['v'][0]
            elif query.path[:7] == '/embed/':
                videoid = query.path.split('/')[2]
            elif query.path[:3] == '/v/':
                videoid = query.path.split('/')[2]
            else:
                videoid = None
        elif query.hostname == "m.youtube.com":
            if query.path == "/details":
                videoid = parse_qs(query.query)['v'][0]
            else:
                videoid = None
        else:
            videoid = None

        # for cases w/o a video ID like feeds or www.youtube.com
        if not videoid:
            title = self.fetchtitle(url)
            return title
        try:
            f = urllib2.urlopen('http://gdata.youtube.com/feeds/api/videos/%s?alt=jsonc&v=2' % videoid)
        except Exception, e:
            self.log.error("ERROR: opening gdata API message {0}".format(e))
            return None

        data = json.load(f)
        if 'error' in data:
            self.log.error("ERROR: {0} trying to fetch {1}".format(data['error']['message'], gdataurl))
            return None
        else:
            data = data['data']
            title = data.get('title')
            category = data.get('category')
            duration = data.get('duration')
            if duration:
                duration = "%dm%ds"%divmod(duration,60)
            viewCount = data.get('viewCount')
            if viewCount:
                viewCount = self.numfmt(viewCount)
            rating = data.get('rating')
            return "Youtube Video: %s  Category: %s  Duration: %s  Views: %s  Rating: %s"\
                % (title, category, duration, viewCount, rating)

    def titledirector(self, url):
        """Main logic for how to handle links."""

        domain = urlparse(url).hostname  # parse out domain.
        # first, check if our link is inside a shortener. fetch real url.
        if domain in self.longUrlServices or domain == 'pic.twitter.com':
            realurl = self.longurl(url)  # try to shorten.
            if realurl:  # if we get something back,
                domain = urlparse(realurl).hostname  # parse the new domain.
                url = realurl  # use the realurl.

        self.log.info(url)

        # put a handler per domain(s)
        if domain in ('m.youtube.com', 'www.youtube.com', 'youtube.com', 'youtu.be'):
            title = self.yttitle(url)
        elif domain in ('vimeo.com', 'player.vimeo.com'):
            title = self.vimeotitle(url)
        else:
            title = self.fetchtitle(url)

        # now return the title.
        if title:
            return title
        else:
            return "No Title"

    def fetchtitle(self, url):
        """Generic title fetcher for non-specific titles."""

        response = self.openurl(url)
        if not response:
            return "No title - had error fetching."
        content = response.read(100*1024*1024)
        bsoptions = {}
        charset = response.info().getheader('Content-Type').split('charset=')
        if len(charset) == 2: bsoptions['fromEncoding'] = charset[-1]
        contentdict = {}
        contentdict['type'] = response.info().getheader('Content-Type')
        contentdict['size'] = response.info().getheader('Content-Length')
        if not contentdict['size']: contentdict['size'] = len(content)

        # now, process various types here. Image->text->others.
        if contentdict['type'].startswith('image/'):  # determine if it's an image and process.
            from PIL import Image
            from cStringIO import StringIO

            try:  # try/except because images can be corrupt.
                im = Image.open(StringIO(content))
            except:
                self.log.error("ERROR: {0} is an invalid image I cannot read.".format(url))
                return "Invalid image format."
            imgformat = im.format
            if imgformat == 'GIF':  # check to see if animated.
                try:
                    im.seek(1)
                    im.seek(0)
                    imgformat = "Animated GIF"
                except EOFError:
                    pass
            return "Image type: {0}  Dimensions: {1}x{2}  Size: {3}".format(imgformat, im.size[0],im.size[1], self.sizefmt(contentdict['size']))
        elif contentdict['type'].startswith('text/'): # text
            soup = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES,**bsoptions)
            try:
                title = self.clean(soup.first('title').string)
            except AttributeError:
                title = 'Error reading title'
            return title.encode('utf-8', 'ignore')
        else: # handle any other filetype using libmagic.
            try:
                import magic
                typeoffile = magic.from_buffer(content)
                return "Content type: {0}  Size: {1}".format(typeoffile,self.sizefmt(contentdict['size']))
            except:
                self.log.info("error: no handler for {0} at {1}".format(response.info().getheader('Content-Type'), url))
                return "Cannot determine file content. Size: {0}".format(contentdict['size'])

    ################
    # MAIN TRIGGER #
    ################

    def doPrivmsg(self, irc, msg):
        channel = msg.args[0]
        user = msg.nick
        linkdb = LinkDB()

        if ircmsgs.isCtcp(msg) and not ircmsgs.isAction(msg):
            return
        if irc.isChannel(channel):  # must be in channel.
            if ircmsgs.isAction(msg):  # if in action, remove.
                text = ircmsgs.unAction(msg)
            else:
                text = msg.args[1]
            for url in utils.web.urlRe.findall(text):  # find urls.
                url = self.tidyurl(url)
                title = self.titledirector(url).decode('utf-8')
                shorturl = self.shortenurl(url)
                if not shorturl:
                    output = url + " - " + title
                else:
                    output = shorturl + " - " + title
                # db
                linkdb.add(url, title, channel, user)

                irc.queueMsg(ircmsgs.privmsg(channel, output.encode('utf-8')))

    def titler(self, irc, msg, args, opttitle):
        """<url>
        Public test function for Titler.
        """

        title = self.titledirector(opttitle).decode('utf-8')
        shorturl = self.shortenurl(opttitle)
        if not shorturl:
            output = opttitle + " - " + title
        else:
            output = shorturl + " - " + title
        irc.reply(output)
    titler = wrap(titler, [('text')])

Class = Titler


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
