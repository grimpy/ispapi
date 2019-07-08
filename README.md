# ispapi
Bundle of client to talk to ISP APIs

## List of implemtend providers

- TelecomEgypt
- Vodafone Egypt

## Add your provider

To add a new provider create a file inside providers module and add the corresponding import to `providers/__init__.py`. The provider implements a subclass of `Provider` class.

### Methods to be implemented in the provider

```py
class MyProvider(Provider):
    def __init__(self, param1, param2='default value'):
        super().__init__(param1, param2)
        # do something with the paramters

    def login_internal(self):
        """Do the login procedure and return session info"""
        return NotImplemented

    def login_from_session_data(self, session_data):
        """Do the login procedure from the cached session info"""
        return NotImplemented

    def get_quota_internal(self):
        """Get quota"""
        raise NotImplementedError()
```

`get_quota_internal` is the only method that is required to be implemented. `login_internal` and `login_from_session_data` are optional.

`login_internal` tries to login, it optionally returns `session_data` to be stored and used later for login.
`login_from_session_data` will be tried first with the last stored `session_data` before trying to use `login_internal` again.

### Formatting for the provider

1. Class name will be used as the subcommand, so it is better to use something that will be unique, for example, adding the country name/code to the class name.
2. Arguments are converted to lower case and underscores are replaced to a dash and they are used as command line arguments. So it is better to use snake case in command line arguments.
