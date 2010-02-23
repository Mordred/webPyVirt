# -*- coding: UTF-8 -*-

def canManageUser(request, *args, **kwargs):
    return request.user.has_perm("auth.change_user")
#enddef

def canRemoveUser(request, *args, **kwargs):
    return request.user.has_perm("auth.delete_user")
#enddef

def canManageGroup(request, *args, **kwargs):
    return request.user.has_perm("auth.change_group")
#enddef

def canRemoveGroup(request, *args, **kwargs):
    return request.user.has_perm("auth.delete_group")
#enddef
