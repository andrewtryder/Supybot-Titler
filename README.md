Supybot-Titler
==============

Supybot plugin to display information about pasted links.

This functionality already exists via the "Web" plugin that ships in Limnoria and Supybot.
However, it's rather dry and buggy. A few users have also produced plugins that will display
better information about specific links, like YouTube. However, this requires running additional
plugins and I've found a varying degree of bugs, along with some that aren't updated.

Titler aims to solve this problem.

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

- 1.) You will need 'python-magic': https://github.com/ahupp/python-magic

    The current stable version of python-magic is available on pypi and can be installed by running pip install python-magic.

- 2.) To shorten links, you will need a Bitly API key (free).

    You will need to sign-up for a Bitly API key at http://bitly.com. The plugin needs to have the bitly username and API key
    configured via the configuration variables.

    Without these, the plugin will just "copy" the long url. You can also disable this functionality where it does not shorten
    URLs and/or show any urls, just titles (if found).

- Third, you might already have PIL installed but I recommend ditching it for the newer Python Imaging Library called "Pillow":

    pip install Pillow

- If you're already using ShrinkURL and Web, disable their overlapping features.

    /msg <bot> plugins.ShrinkUrl.shrinkSnarfer False
    /msg <bot> plugins.Web.titleSnarfer False

    Otherwise, you will have dupes being pasted. You do not need to unload either and I don't recommend it as each has functionality
    elsewhere in the bot.
