# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

import re

def MENU(request):
    return [
        {   # HOME
            #"hide":         False,         # if "hide" is not present => always display
                                            # if "hide" is present and False => hide if submenu is empty
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
            "label":        _("Users & Groups"),
            "module":       "accounts",
            "namespace":    "accounts",
            "url":          "home",
            "selected":     r"^/accounts/"
        },
        {   # NODES
            "hide":         False,
            "label":        _("Nodes"),
            "module":       "nodes",
            "namespace":    "nodes",
            "url":          "node_index",
            "selected":     r"^/nodes/"
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
#enddef

def generateMenu(request):

    if request.user.is_authenticated():
        mainMenu, selectedMainMenuItem = getMainMenu(request)
        leftMenu = getLeftMenu(request, selectedMainMenuItem)
    else:
        mainMenu = []
        leftMenu = []
    #endif

    return {
        "main_menu":    mainMenu,
        "left_menu":    leftMenu
    }

#enddef

def getMainMenu(request):
    """
    Return main menu
    """

    mainMenu = []
    selectedMainMenuItem = None

    for item in MENU(request):

        hide = bool("hide" in item and (item['hide'] or len(getLeftMenu(request, item)) == 0))
        selected = bool("selected" in item and re.search(item['selected'], request.path))

        if selected: selectedMainMenuItem = item

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

    return mainMenu, selectedMainMenuItem

#enddef

def getLeftMenu(request, item):
    """
    Return data for left menu
    """
    if not item: return []

    selected = bool("selected" in item and re.search(item['selected'], request.path))

    if "module" in item:
        module = __import__("%s" % item['module'], globals(), locals(), ["menu"])

        if hasattr(module, "menu"):
            return getMenu(request, module.menu.MENU(request), 
                item['selected'], "namespace" in item and item['namespace'])
        else:
            return []
        #endif
    elif "menu" in item:
        return getMenu(request, item['menu'], item['selected'])
    else:
        return []
    #endif

#enddef

def getMenu(request, moduleMenu, urlPrefixPattern = "", namespace=False, ):
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
                    selected = re.search(urlPrefixPattern + item['selected'], request.path)
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

            if len(submenu):
                menu.append({
                        "label":    section['label'],
                        "items":    submenu
                    })
            #endif
        #endif

    #endfor

    return menu

#enddef
