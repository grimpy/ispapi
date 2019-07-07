class Provider(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def load_session_data(self):
        # TODO: local storage for session data
        return NotImplemented

    def store_session_data(self, session_data):
        # TODO: local storage for session data
        pass

    def login(self):
        session_data = self.load_session_data()
        if session_data is not NotImplemented and session_data is not None:
            login = self.login_from_session_data(session_data)
            if login is not NotImplemented and login is not None:
                return login
        login = self.login_internal()
        if login is not NotImplemented and login is not None:
            self.store_session_data(login)

    def login_internal(self):
        """Do the login procedure and return session info"""
        return NotImplemented

    def login_from_session_data(self, session_data):
        """Do the login procedure from the session info"""
        return NotImplemented

    def get_quota(self):
        """Get quota"""
        return self.get_quota_internal()

    def get_quota_internal(self):
        """Get quota"""
        raise NotImplementedError()
