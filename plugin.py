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
from urlparse import *
import socket # capture timeout from socket
import time
# extra supybot libs
import supybot.ircmsgs as ircmsgs
import supybot.dbi as dbi
# supybot libs
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization('Titler')

#@internationalizeDocstring
# UrlRecord - modified from URL plugin.
class UrlRecord(dbi.Record):
    __fields__ = [
        ('url', eval),
        ('by', eval),
        ('channel', eval),
        ('at', eval),
        ]

class DbiUrlDB(plugins.DbiChannelDB):
    class DB(dbi.DB):
        Record = UrlRecord
        def add(self, url, msg):
            record = self.Record(url=url, by=msg.nick,channel=msg.args[0], at=time.time())
            super(self.__class__, self).add(record)
        def urls(self, p):
            L = list(self.select(p))
            L.reverse()
            return L
        
class Titler(callbacks.Plugin):
    """Add the help for "@plugin help Titler" here
    This should describe *how* to use this plugin."""
    threaded = True
    noIgnore = True

    def __init__(self, irc):
        self.__parent = super(Titler, self)
        self.__parent.__init__(irc)
        self.encoding = 'utf8' # irc output.
        self.headers = {'User-agent':'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2'}
        self.MAXREAD = 100*1024*1024 # max filesize to read in. 100mb seems fine.
        self.longUrlCacheTime = time.time()
        self.longUrlServices = None
        if not self.longUrlServices:
            self.longUrlServices = self.getlongurlservices()
        #self.db = TitlerDB()

    #def die(self):
    #    self.__parent.die()
    #    self.db.close()
    
    def longurlservices(self, irc, msg, args):
        irc.reply("Services: {0}".format(self.getlongurlservices()))
    longurlservices = wrap(longurlservices)
    
    def getlongurlservices(self):        
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
    
    # resolve tinyurls into their normal form.
    def longurl(self, surl):
        try:
            req_url = 'http://api.longurl.org/v2/expand?format=json&url=%s' % surl
            req = urllib2.Request(req_url, headers=self.headers)
            lookup = json.loads(urllib2.urlopen(req).read())
            return lookup['long-url']
        except:
            return None

    # clean-up title.
    def clean(self, msg):
        cleaned = msg.translate(dict.fromkeys(range(32))).strip()
        return re.sub(r'\s+', ' ', cleaned)

    # main handler to find urls in public messages.
    def doPrivmsg(self, irc, msg):
        if ircmsgs.isCtcp(msg) and not ircmsgs.isAction(msg):
            return
        channel = msg.args[0]
        if irc.isChannel(channel):
            if ircmsgs.isAction(msg):
                text = ircmsgs.unAction(msg)
            else:
                text = msg.args[1]
            for url in utils.web.urlRe.findall(text):
                title = self.titledirector(url)
                shorturl = self.shortenurl(url)
                if not shorturl:
                    irc.queueMsg(ircmsgs.privmsg(channel,"{0} - {1}".format(url,title)))
                else:
                    irc.queueMsg(ircmsgs.privmsg(channel,"{0} - {1}".format(shorturl,title)))

    # test function.
    def titler(self, irc, msg, args, opttitle):
        title = self.titledirector(opttitle)
        shorturl = self.shortenurl(opttitle)
        if not shorturl:
            irc.reply("{0} - {1}".format(opttitle,title))
        else:
            irc.reply("{0} - {1}".format(shorturl,title))
    titler = wrap(titler, [('text')])

    # shorten url using bitly.
    def shortenurl(self, url):
        # don't try to reshorten bit.ly links.
        domain = urlparse(url).hostname
        if domain in ('bit.ly', 'j.mp', 'bitly.com'):
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

    # format numbers into human-readable units.
    def numfmt(self, num):
        num = float(num)
        for x in ['','k','m','b']:
            if num < 1000.0 and num > -1000.0:
                return "%3.1f%s" % (num, x)
            num /= 1000.0

    # format filesize/bytes into human-readable units.
    def sizefmt(self, num):
        if num is None:
            return 'No size'
        num = int(num)
        for x in ['b','KB','MB','GB']:
            if num < 1024.0:
                return "%3.1f%s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TB')

    # takes url, grabs domain, directs if for a special handler.
    def titledirector(self, url):
        domain = urlparse(url).hostname # parse out domain.
   
        # first, check if our link is inside a shortener. fetch real url.
        if domain in self.longUrlServices or domain == 'pic.twitter.com':
            realurl = self.longurl(url) # try to shorten.
            if realurl: # if we get something back,
                domain = urlparse(realurl).hostname # parse the new domain.
                url = realurl # use the realurl.
        self.log.info(url)
        self.log.info(str(domain))
        # put a handler per domain(s)
        if domain in ('www.youtube.com','youtube.com','youtu.be'): #youtube.
            title = self.yttitle(url)
        elif domain in ('vimeo.com','player.vimeo.com'):
            title = self.vimeotitle(url)
        else:
            title = self.fetchtitle(url)
            
        # now return the title.
        if title:
            return title
        else:
            return "No Title"
    
    # grab title for vimeo videos:
    def vimeotitle(self, url):
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
    
    # grab title for youtube videos.
    def yttitle(self, url):
        """Code from: http://bit.ly/Z2y8rC"""
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
            return "Youtube Video: {0}  Category: {1}  Duration: {2}  Views: {3}  Rating: {4}".format(data.get('title'),\
                data.get('category'),("%dm%ds"%divmod(data.get('duration'),60)),self.numfmt(data.get('viewCount')),\
                    data.get('rating'))

    # this will open a build a urlopener, inject headers, and then open a url and return the response object.
    def openurl(self, url):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2')]
        try:
            response = opener.open(url,timeout=5)
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
    
    def fetchtitle(self, url):
        response = self.openurl(url)
        if not response:
            return "No title - had error fetching."
        content = response.read(self.MAXREAD)
        bsoptions = {}        
        charset = response.info().getheader('Content-Type').split('charset=')
        if len(charset) == 2:
            bsoptions['fromEncoding'] = charset[-1]
        contentdict = {}
        contentdict['type'] = response.info().getheader('Content-Type')
        contentdict['size'] = response.info().getheader('Content-Length')
        if not contentdict['size']:
            contentdict['size'] = len(content)
        
        # now, process various types here. Image->text->others.
        if contentdict['type'].startswith('image/'): # determine if it's an image and process.
            # do our imports.
            from PIL import Image
            from cStringIO import StringIO
            # now go.
            try:
                im = Image.open(StringIO(content))
            except:
                self.log.error("ERROR: {0} is an invalid image I cannot read.".format(url))
                return "Invalid image format."
            imgformat = im.format
            if imgformat == 'GIF': # check to see if animated.
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
        
Class = Titler


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
