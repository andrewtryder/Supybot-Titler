
  File "/home/spline/supybot/plugins/Titler/plugin.py", line 723, in titler
    output = self._titler(opturl, channel)
  File "/home/spline/supybot/plugins/Titler/plugin.py", line 588, in _titler
    if domain in self.longUrlServices:
TypeError: argument of type 'NoneType' is not iterable


BUGGY URL:

http://mp3.rtvslo.si/ars


- Maybe pass already tiny'd links?

http://mashable.com/2013/01/23/unlocking-cellphones-illegal/

https://github.com/weezel/supybot-plugins/blob/master/Youtube/plugin.py
https://github.com/frumiousbandersnatch/sobrieti-plugins/blob/master/plugins/Scores/plugin.py
https://github.com/grantbow/plugins/blob/668f058e7fed9119bf07e636de956337eafae2a3/WikiSearch/plugin.py
https://github.com/gsf/supybot-plugins/blob/aeafd7350822d56305c10a365a83f322e557264e/edsu-plugins/AudioScrobbler/plugin.py
https://github.com/dahu/Supybot-Infobot/blob/8197bb95fddecc7702d1e6745441577330449caa/plugin.py
https://github.com/ProgVal/Limnoria/blob/98996be2511a95b8f1f0608b76e5af13af22d6b8/plugins/URL/plugin.py
https://github.com/ProgVal/Limnoria/blob/master/plugins/News/plugin.py
https://github.com/gsf/supybot-plugins/blob/a57cb6aaab1d52b7b9fad73be4e869ce8c108f60/plugins/Cast/plugin.py
https://github.com/rubinlinux/supybot-twitter/blob/master/plugin.py
https://github.com/Erika-Mustermann/Limnoria/blob/master/plugins/Web/plugin.py
https://github.com/Suwako/Naoko/blob/2bc130d88fa675ff4d2aca708dcb096aeb3995d6/naoko/lib/apiclient.py

https://github.com/m13253/titlebot/blob/master/titlebot.py

IDEA/CODE for amazon plugin.
- A friend suggested this but I find it's too difficult for people to implement.
- My understanding is that Amazon also is 'random' in the information returned on each item, so a plugin could be challenging.
- Here is scratch code that works

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hmac
from hashlib import sha256
import base64
import urllib
import urllib2
import time

AWS_SECRET_KEY = ''

kwargs = {}
kwargs['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
kwargs['Operation'] = "ItemLookup"
kwargs['Version'] = "2011-08-01"
kwargs['AWSAccessKeyId'] = ''
kwargs['Service'] = "AWSECommerceService"
kwargs['ItemId'] = 'B00008OE6I'
kwargs['AssociateTag'] = '' # https://affiliate-program.amazon.com/gp/associates/network/main.html
kwargs['MerchantId'] = 'All'
kwargs['Condition'] = 'All'
kwargs['IncludeReviewsSummary'] = 'True'
kwargs['ResponseGroup'] = 'ItemAttributes,OfferSummary'
# ['Request','ItemIds','Small','Medium','Large','Offers','OfferFull','OfferSummary',
# 'OfferListings','PromotionSummary','PromotionDetails','Variations','VariationImages',
# 'VariationMinimum','VariationSummary','TagsSummary','Tags','VariationMatrix','VariationOffers',
# 'ItemAttributes','MerchantItemAttributes','Tracks','Accessories','EditorialReview','SalesRank',
# 'BrowseNodes','Images','Similarities','Subjects','Reviews','ListmaniaLists','SearchInside',
# 'PromotionalTag','AlternateVersions','Collections','ShippingCharges','RelatedItems','ShippingOptions'].
service_domain = 'ecs.amazonaws.com'
# = 'xml-us.amznxslt.com'
keys = sorted(kwargs.keys())
quoted_strings = "&".join("%s=%s" % (k, urllib.quote(unicode(kwargs[k]).encode('utf-8'), safe = '~')) for k in keys)
data = "GET\n" + service_domain + "\n/onca/xml\n" + quoted_strings
digest = hmac.new(AWS_SECRET_KEY, data, sha256).digest()
signature = urllib.quote(base64.b64encode(digest))
api_string = "http://" + service_domain + "/onca/xml?" + quoted_strings + "&Signature=%s" % signature
api_request = urllib2.Request(api_string) #, headers={"Accept-Encoding": "gzip"})
response = urllib2.urlopen(api_request)
response_text = response.read()

print type(response_text)
print response_text
```
