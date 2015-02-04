NOTE: I am no longer developing this plugin. I do not have the time to support a project this big. If you'd like to take over, feel free to fork or take the code and go. It's a great plugin but just far too much overhead for me to support.


Supybot-Titler
==============

Supybot plugin to display information about pasted links.

This functionality already exists via the "Web" plugin that ships in Limnoria and Supybot.
However, it's rather dry and buggy. A few users have also produced plugins that will display
better information about specific links, like YouTube. However, this requires running additional
plugins and I've found a varying degree of bugs, along with some that aren't updated.

Titler aims to solve this problem.

To give credit to some in the past, Detroll: https://github.com/jtatum/Detroll/ was one of my bigger
inspirations but the plugin has an entirely different life of its own from there. I also credit many of
the similar plugins for Supybot and other bots out there with ideas for different sites and strategies for
attacking the "link title on irc" issue many try to solve.

I developed a modular way to "plug-in" functions that will aid in the display of specific links. With
the number of sites that have public APIs out there, it's not hard to parse a link and then make a simple
API call to yield additional information about a link. Examples of this can be found in my own YouTube
parsing, Vimeo parser and imgur parsers.

This plugin will also yield information about images that are not on hosting sites, such as when a user
pastes a direct link to a JPG file. There is also a 'magic' implementation to spit out information about
other types of files, using a system's file magic, thanks to python-magic.

I also combined functionality of ShrinkUrl into this so that you can spit out a shortened (bitly) link with the
title on a single line.

In addition to snarfing titles, a user, snackle, suggested a way for text links (like a link to an online article)
to come back with a "description" if available. Many online news agencies publish short summaries of the articles,
different from the <title> of the article, inside a <meta name="description" content=""> field. There is an option
to have this displayed if available. NOTE: Quite a number of sites don't publish this so don't always expect it if
enabled (on by default).

My intention with this plugin is for fellow developers to fork and add in patches for additional APIs. If you read
the code in plugin.py, it is as simple as adding a function (follow the style in any of the ones at the bottom), and
then supply a dict entry inside of self.domainparsers at top. The format is 'domain.com': '_nameofhandler'. Feel free
to fork the code, add in your function, and I'll be happy to merge.

STATUS: Working but I'm sure bugs are present. Try if you want. Submit to me any logs/errors and I'll look at them.

Setting up
==========

- 1.) Required Python 2 libraries:

    - python-magic, Pillow, requests, bs4 (make a change if you install them locally like I do)

        pip install python-magic
        pip install Pillow
        pip install requests
        pip install bs4

- 2.) To shorten links, you will need a Bitly API key (free).

    You will need to sign-up for a Bitly API key at http://bitly.com. The plugin needs to have the bitly username and API key
    configured via the configuration variables.

    You then need the login and API key under their "legacy" API. When you're logged in, go here:

    https://bitly.com/a/settings/advanced

    Look for the "Show Legacy API key"

    It will have a login and API key. Configure these into the plugin as such:

    /msg <bot> config plugins.Titler.bitlyLogin LOGIN
    /msg <bot config plugins.Titler.bitlyApiKey APIKEYHERE

    Now reload the plugin.

    NOTE: You can also control a bit of the functionality from links that spit out here under settings such as the domain (j.mp vs bit.ly)

    Without these, the plugin will just "copy" the long url. You can also disable this functionality where it does not shorten
    URLs and/or show any urls, just titles (if found).

- 3.) You might already have PIL installed but I recommend ditching it for the newer Python Imaging Library called "Pillow":

    pip install Pillow

- 4.) If you're already using ShrinkURL and Web, disable their overlapping features.

    /msg <bot> plugins.ShrinkUrl.shrinkSnarfer False
    /msg <bot> plugins.Web.titleSnarfer False

    Otherwise, you will have dupes being pasted. You do not need to unload either and I don't recommend it as each has functionality
    elsewhere in the bot.
