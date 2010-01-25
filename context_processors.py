# -*- coding: UTF-8 -*-

from menu   import getMainMenu, getLeftMenu

def menu(request):
    return { 
        "main_menu":    getMainMenu(request),
        "left_menu":    getLeftMenu(request)
    }
#enddef
