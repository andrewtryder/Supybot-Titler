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

NOTE: far from working. Try if you want.

My intention with this plugin is for fellow developers to fork and add in patches for additional APIs. If you read
the code in plugin.py, it is as simple as adding a function (follow the style in any of the ones at the bottom), and
then supply a dict entry inside of self.domainparsers at top. The format is 'domain.com': '_nameofhandler'.

Setting up
==========

You will need to sign-up for a Bitly API key at http://bitly.com. The plugin needs to have the bitly username and API key
configured via the configuration variables.

Needs Image installed (PIL) and https://github.com/ahupp/python-magic.git
