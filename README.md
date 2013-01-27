Supybot-Titler
==============

Supybot plugin to display link/url titles with specialization for Youtube/Vimeo videos/images

NOTE: far from working. Try if you want.


https://github.com/frumiousbandersnatch/sobrieti-plugins/blob/master/plugins/Scores/plugin.py
https://github.com/grantbow/plugins/blob/668f058e7fed9119bf07e636de956337eafae2a3/WikiSearch/plugin.py
https://github.com/gsf/supybot-plugins/blob/aeafd7350822d56305c10a365a83f322e557264e/edsu-plugins/AudioScrobbler/plugin.py
https://github.com/dahu/Supybot-Infobot/blob/8197bb95fddecc7702d1e6745441577330449caa/plugin.py
https://github.com/ProgVal/Limnoria/blob/98996be2511a95b8f1f0608b76e5af13af22d6b8/plugins/URL/plugin.py
https://github.com/ProgVal/Limnoria/blob/master/plugins/News/plugin.py
https://github.com/gsf/supybot-plugins/blob/a57cb6aaab1d52b7b9fad73be4e869ce8c108f60/plugins/Cast/plugin.py
https://github.com/rubinlinux/supybot-twitter/blob/master/plugin.py

INFO 2013-01-23T18:40:37 ERROR: Cannot open: http://git.io/8zuPDQ HTTP Error
     code: 400
ERROR 2013-01-23T18:40:37 Uncaught exception:
Traceback (most recent call last):
  File "/home/spline/.local/lib/python2.7/site-packages/supybot/log.py", line 353, in m
    return f(self, *args, **kwargs)
  File "/home/spline/.local/lib/python2.7/site-packages/supybot/irclib.py", line 133, in __call__
    method(irc, msg)
  File "/home/spline/supybot/plugins/Titler/plugin.py", line 117, in doPrivmsg
    title = self.titledirector(url)
  File "/home/spline/supybot/plugins/Titler/plugin.py", line 186, in titledirector
    title = self.fetchtitle(url)
  File "/home/spline/supybot/plugins/Titler/plugin.py", line 272, in fetchtitle
    content = response.read(self.MAXREAD)
AttributeError: 'NoneType' object has no attribute 'read'
ERROR 2013-01-23T18:40:37 Exception id: 0x6da3a

- Maybe pass already tiny'd links?

http://mashable.com/2013/01/23/unlocking-cellphones-illegal/
