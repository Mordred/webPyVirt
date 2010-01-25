# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

import re

MENU = [
    {   # HOME
        "hide":         False,
        "label":        _("Home"),
        "url":          "home",
        "selected":     r"^/$",
        "menu":         [
            {   # Section quick navigation
                "hide":     False,
                "label":    _("Quick Access"),
                "items":    [
                    # TODO pridaj najpouzivanejsie odkazy
                ]
            }
        ]
    },
    {   # USERS
        "hide":         False,
        "label":        _("Users"),
        "module":       "accounts",
        "namespace":    "accounts",
        "url":          "home",
        "selected":     r"^/accounts/"
    },
    {
        # GROUPS
        "hide":         False,
        "label":        _("Groups"),
        "module":       "groups",
        "namespace":    "groups",
        "url":          "home",
        "selected":     r"^/groups/"
    },
    {   # SERVERS
        "hide":         False,
        "label":        _("Servers"),
        "module":       "servers",
        "namespace":    "servers",
        "url":          "home",
        "selected":     r"^/servers/"
    },
    {   # DOMAINS
        "hide":         False,
        "label":        _("Domains"),
        "module":       "domains",
        "namespace":    "domains",
        "url":          "home",
        "selected":     r"^/domains/"
    }
]

def getMainMenu(request):
    """
    Return main menu
    """

    mainMenu = []

    for item in MENU:

        hide = bool("hide" in item and item['hide'])
        selected = bool("selected" in item and re.search(item['selected'], request.path))

        if not hide:

            if "namespace" in item:
                url = reverse("%s:%s" % (item['namespace'], item['url']))
            else:
                url = reverse(item['url'])
            #endif

            mainMenu.append({
                    "label":    item['label'],
                    "url":      url,
                    "selected": selected
                })
        #endif
    #endfor

    return mainMenu

#enddef

def getLeftMenu(request):
    """
    Return data for left menu
    """

    for item in MENU:
        selected = bool("selected" in item and re.search(item['selected'], request.path))

        if not selected: continue

        if "module" in item:
            module = __import__("%s" % item['module'], globals(), locals(), ["menu"])

            if hasattr(module, "menu"):
                return getMenu(request, module.menu.MENU, "namespace" in item and item['namespace'])
            else:
                return []
            #endif
        elif "menu" in item:
            return getMenu(request, item['menu'])
        else:
            return []
        #endif
    #endfor

#enddef

def getMenu(request, moduleMenu, namespace=False):
    """
    Return menu for groups module
    """

    menu = []

    for section in moduleMenu:

        hide = bool("hide" in section and section['hide'])

        if not hide:
            submenu = []

            for item in section['items']:
                itemHide = bool("hide" in item and item['hide'])

                if namespace:
                    url = reverse("%s:%s" % (namespace, item['url']))
                else:
                    url = reverse(item['url'])
                #endif

                if "selected" in item:
                    selected = re.search(item['selected'], request.path)
                else:
                    selected = re.search(re.escape(url), request.path) 
                #endif

                if not itemHide:
                    submenu.append({
                            "label":    item['label'],
                            "url":      url,
                            "selected": bool(selected)
                        })
                #endif
            #endfor

            menu.append({
                    "label":    section['label'],
                    "items":    submenu
                })
        #endif

    #endfor

    return menu

#enddef
