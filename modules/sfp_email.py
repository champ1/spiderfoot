#-------------------------------------------------------------------------------
# Name:         sfp_email
# Purpose:      SpiderFoot plug-in for scanning retreived content by other
#               modules (such as sfp_spider) and identifying e-mail addresses
#
# Author:      Steve Micallef <steve@binarypool.com>
#
# Created:     06/04/2012
# Copyright:   (c) Steve Micallef 2012
# Licence:     GPL
#-------------------------------------------------------------------------------

import sys
import re
from sflib import SpiderFoot, SpiderFootPlugin, SpiderFootEvent

# SpiderFoot standard lib (must be initialized in setup)
sf = None

class sfp_email(SpiderFootPlugin):
    """E-Mail:Identify e-mail addresses in any obtained data."""

    # Default options
    opts = {
        # options specific to this module
        'includesubdomains':   True, # Include e-mail addresses on sub-domains of
                                    # the target domain
        'includeexternal':  False # Include e-mail addrs on external domains
    }

    # Option descriptions
    optdescs = {
        'includesubdomains': "Report e-mail addresses on a sub-domain of the target base domain-name?",
        'includeexternal': "Report e-mail addresses not on the target base domain-name?"
    }

    # Target
    baseDomain = None
    results = dict()

    def setup(self, sfc, target, userOpts=dict()):
        global sf

        sf = sfc
        self.baseDomain = target
        self.results = dict()

        for opt in userOpts.keys():
            self.opts[opt] = userOpts[opt]

    # What events is this module interested in for input
    def watchedEvents(self):
        return ["*"]

    # What events this module produces
    # This is to support the end user in selecting modules based on events
    # produced.
    def producedEvents(self):
        return [ "EMAILADDR" ]

    # Handle events sent to this module
    def handleEvent(self, event):
        eventName = event.eventType
        srcModuleName = event.module
        eventData = event.data
        parentEvent = event.sourceEvent

        if eventName == "EMAILADDR":
            return None

        sf.debug("Received event, " + eventName + ", from " + srcModuleName)

        if type(eventData) not in [ str, unicode ]:
            sf.debug("Unhandled type to find e-mails: " + str(type(eventData)))
            return None

        matches = re.findall("([a-zA-Z\.0-9_\-]+@[a-zA-Z\.0-9_\-]+)", eventData)
        for match in matches:
            sf.debug("Found possible email: " + match)

            if len(match) < 4:
                sf.debug("Likely invalid address.")
                continue

            if self.baseDomain not in match.lower():
                sf.debug("E-mail (or something) from somewhere else..")
                continue

            self.results[match] = True

            # Include e-mail addresses on sub-domains within the domain?
            if not self.opts['includesubdomains']:
                if not match.lower().endswith('@' + self.baseDomain):
                    sf.debug("Ignoring e-mail address on a sub-domain: " + match)
                    continue

            # Include external domains as e-mail addresses?
            if not self.opts['includeexternal']:
                if not match.lower().endswith(self.baseDomain):
                    sf.debug("Ignoring e-mail address on an external domain" + match)
                    continue

            sf.info("Found e-mail address: " + match)
            evt = SpiderFootEvent("EMAILADDR", match, self.__name__, parentEvent)
            self.notifyListeners(evt)

        return None

# End of sfp_email class
