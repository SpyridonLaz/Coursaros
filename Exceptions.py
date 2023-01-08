
# Is raised when login attempt fails
class EdxLoginError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# Is raised when the course cannot be fetched
class EdxInvalidCourseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# Raised when no blocks found for the course
class EdxNotEnrolledError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# Raised when some HTTP error occurs
class EdxRequestError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# Raised when an unauthenticated request is made
class EdxNotAuthenticatedError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
