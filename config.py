###
# Copyright (c) 2013, spline
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.registry as registry
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization('Titler')

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Titler', True)


Titler = conf.registerPlugin('Titler')

conf.registerGlobalValue(Titler, 'bitlyLogin', registry.String('', _("""bitly login"""), private=True))
conf.registerGlobalValue(Titler, 'bitlyApiKey', registry.String('', _("""bitly key"""), private=True))
conf.registerChannelValue(Titler, 'disableChannel', registry.Boolean(False, _("""Disable all functionality in a certain channel?""")))
conf.registerChannelValue(Titler, 'displayURL', registry.Boolean(True, _("""Display URL with the title?""")))
conf.registerChannelValue(Titler, 'displayShortURL', registry.Boolean(True, _("""Shorten that URL (must set bitly config)?""")))
conf.registerChannelValue(Titler, 'displayImageTitles', registry.Boolean(True, _("""Ignore pasted images? if True, no title nor image dimensions will be pasted.""")))
conf.registerChannelValue(Titler, 'displayOtherTitles', registry.Boolean(True, _("""Display title when we don't know what it is.""")))
conf.registerChannelValue(Titler, 'displayDescriptionIfText', registry.Boolean(True, _("""If text article is pasted, display a summary if available?""")))

#conf.registerChannelValue(Titler, 'throttlePrinting', registry.Boolean(True, _("""Throttle if we paste more than 2 titles in 10 seconds?""")))

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=250:
