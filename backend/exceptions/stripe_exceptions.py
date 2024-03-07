class StripeCheckoutSessionException(Exception):
    """
    Exception raised for errors related to Stripe checkout sessions.

    Args:
        msg (str): Optional. The error message associated with the exception.
    """

    def __init__(self, msg: str = "Stripe checkout session error"):
        super().__init__(msg)


class HostStripeAccountNotFoundException(Exception):
    """
    Exception raised when a host does not have a Stripe account when it is expected to.

    Args:
        msg (str): Optional. The error message associated with the exception.
    """

    def __init__(self, msg: str = "Host does not have a Stripe account"):
        super().__init__(msg)


class HostStripeAccountCreationException(Exception):
    """
    Exception raised when there is an error creating a host Stripe account.

    Args:
        msg (str): Optional. The error message associated with the exception.
    """

    def __init__(self, msg: str = "Error creating host Stripe account"):
        super().__init__(msg)
