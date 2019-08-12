class Providers:
    from .telecomegypt import TelecomEgypt
    from .vodafoneegypt import VodafoneEgypt
    try:
        from .lebaranl import LebaraNL
    except ImportError:
        pass
