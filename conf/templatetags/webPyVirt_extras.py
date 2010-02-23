# -*- coding: UTF-8 -*-

from django.template        import Library, Node
from django.utils.encoding  import smart_str

register = Library()

class URLWithVarNode(Node):
    def __init__(self, var_name, args, kwargs, addArgs, addKwargs, asvar):
        self.var_name = var_name
        self.args = args
        self.kwargs = kwargs
        self.addArgs = addArgs
        self.addKwargs = addKwargs
        self.asvar = asvar
    #enddef

    def render(self, context):
        from django.core.urlresolvers import reverse, NoReverseMatch
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        if self.addArgs:
            args[len(args):] = context[self.addArgs]
        #endif

        if self.addKwargs:
            kwargs.update(context[self.addKwargs])
        #endif

        url = ''
        try:
            url = reverse(context[self.var_name], args=args, kwargs=kwargs, current_app=context.current_app)
        except NoReverseMatch, e:
            if self.asvar is None:
                raise e
            #endif
        #endtry

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url
        #endif
    #enddef
#endclass

@register.tag(name="urlWithVar")
def urlWithVar(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplatsmareSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    varname = bits[1]
    args = []
    kwargs = {}

    addArgs = None
    addKwargs = None

    asvar = None

    if len(bits) > 2:
        bits = iter(bits[2:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            elif bit.startswith("**"):
                addKwargs = bit[2:]
            elif bit.startswith("*"):
                addArgs = bit[1:]
            else:
                for arg in bit.split(","):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return URLWithVarNode(varname, args, kwargs, addArgs, addKwargs, asvar)

#enddef
