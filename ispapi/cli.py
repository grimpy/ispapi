import inspect

def load_providers():
    """Loads providers"""
    import providers
    return get_providers_info([val for key, val in providers.Providers.__dict__.items() if not key.startswith("_")])

shorthands = {
    "username": "u",
    "password": "p",
}

class Arg(object):
    def __init__(self, name, required, default_value):
        self.name = name
        self.required = required
        self.default_value = default_value

    @staticmethod
    def get_args_from_argspec(argspec):
        args = []
        reversed_defaults = argspec.defaults and list(reversed(argspec.defaults))
        reversed_args = list(reversed(argspec.args))
        for i, arg in enumerate(reversed_args):
            name = arg
            required = True
            default_value = None
            if arg == 'self':
                continue
            if argspec.defaults is not None and i < len(reversed_defaults):
                required = False
                default_value = reversed_defaults[i]
            args.insert(0, Arg(name, required, default_value))
        return args

    def add_argument(self, parser):
        name = self.name.replace('_', '-')
        shorthand = shorthands.get(name)
        if shorthand is not None:
            parser.add_argument('--{name}'.format(name=name), '-{shorthand}'.format(shorthand=shorthand), required=self.required, default=self.default_value)
        else:
            parser.add_argument('--{name}'.format(name=name), required=self.required, default=self.default_value)

    def __str__(self):
        s =  "Name: {name}\nRequired: {required}".format(name=self.name, required=self.required)
        if not self.required:
            s += "\nDefault value: {default_value}".format(default_value=self.default_value)
        return s

    __repr__ = __str__


class ProviderInfo(object):
    def __init__(self, provider, name, description, args):
        self.provider = provider
        self.name = name
        self.description = description
        self.args = args

    def process(self, args):
        args_names = [arg.name for arg in self.args]
        d = {k.replace('-', '_'): v for k, v in args._get_kwargs() if k.replace('-', '_') in args_names}
        p = self.provider(**d)
        p.login()
        return p.get_quota()

    def add_parser(self, subparsers):
        parser = subparsers.add_parser(self.name.lower(), help='{name} adapter'.format(name=self.name))
        for arg in self.args:
            arg.add_argument(parser)
        parser.set_defaults(func=lambda args: self.process(args))

    def __str__(self):
        return "\nCommand:{lower_name}\nName:{name}\nDescription:{description}\nArgs:\n{args}\n".format(
            lower_name=self.name.lower(),
            name=self.name,
            description=self.description,
            args='\n'.join(['- \t' + str(arg).replace('\n', '\n\t') for arg in self.args]),
        )

    __repr__ = __str__

def get_providers_info(providers):
    return [ProviderInfo(
        provider=provider,
        name=provider.__name__,
        description=provider.__doc__ or "",
        args=Arg.get_args_from_argspec(inspect.getargspec(provider.__init__)),
    ) for provider in providers]

def repr_providers_info(providers_info):
    return '\n'.join(str(provider_info) for provider_info in providers_info)

if __name__ == '__main__':
    import argparse
    providers = load_providers()
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list-providers', action='store_true', help='detailed list of supported providers')
    subparsers = parser.add_subparsers(help='provider commands')
    for provider in providers:
        provider.add_parser(subparsers)
    options = parser.parse_args()
    if options.list_providers:
        print(repr_providers_info(providers))
        exit(0)
    elif not hasattr(options, 'func'):
        parser.print_help()
        exit(255)
    else:
        print(options.func(options))
