class StripeCheckoutSessionException(Exception):
    def __init__(self, msg: str = "Stripe checkout session error"):
        super().__init__(msg)


class HostStripeAccountNotFoundException(Exception):
    def __init__(self, msg: str = "Host does not have a Stripe account"):
        super().__init__(msg)


class HostStripeAccountCreationException(Exception):
    def __init__(self, msg: str = "Error creating host Stripe account"):
        super().__init__(msg)
