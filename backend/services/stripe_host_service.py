"""
Stripe payment service for creating checkout sessions.
"""

import stripe
from fastapi import Depends
from sqlalchemy.orm import Session

from ..database import db_session
from ..settings.config import STRIPE_SECRET_KEY
from ..models import Host
from .host_service import HostService
from ..exceptions import (
    HostStripeAccountNotFoundException,
    HostStripeAccountCreationException,
)


class StripeHostService:
    host_service: HostService
    _session: Session

    def __init__(
        self,
        session: Session = Depends(db_session),
        host_service: HostService = Depends(HostService),
    ):
        stripe.api_key = STRIPE_SECRET_KEY
        self._session = session
        self.host_service = host_service

    def create_stripe_account_for_host(self, host_id: int) -> str:
        """
        Creates a Stripe connected account for a host and updates the host entity with the Stripe ID.

        Args:
            host_id (int): The ID of the host to create a Stripe account for.

        Returns:
            str: The Stripe account ID.

        Raises:
            HostStripeAccountCreationException: If there is an error creating the Stripe account.
            HostNotFoundException: If no host is found with the specified ID.
        """
        host = self.host_service.get_by_id(host_id)

        if host.stripe_id is not None:
            return host.stripe_id

        try:
            account = stripe.Account.create(
                country="US",
                type="express",
                email=host.email,
                metadata={
                    "host_id": str(host.id),
                    "host_first_name": host.first_name,
                    "host_last_name": host.last_name,
                    "host_email": host.email,
                },
                settings={
                    "payouts": {
                        "debit_negative_balances": True,
                        "statement_descriptor": "Scanbandz Payout",
                    },
                },
                capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                    "bank_transfer_payments": {"requested": True},
                    "us_bank_account_ach_payments": {"requested": True},
                },
            )
            host: Host = self.host_service.set_stripe_id(host_id, account.id)
            return host.stripe_id  # type: ignore

        except stripe.StripeError as e:
            raise HostStripeAccountCreationException(
                f"Error creating Stripe account: {e}"
            )
        except Exception as e:
            raise HostStripeAccountCreationException(f"Unknown Stripe error: {e}")

    def get_onboarding_link(self, host_id: int) -> str:
        """
        Retrieves the Stripe onboarding link for a host.

        Args:
            host_id (int): The ID of the host to retrieve the onboarding link for.

        Returns:
            str: The Stripe onboarding link.

        Raises:
            HostStripeAccountNotFoundException: If the host does not have a Stripe account.
        """
        host = self.host_service.get_by_id(host_id)

        if host.stripe_id is None:
            raise HostStripeAccountNotFoundException()

        # TODO: Add refresh and return URLs
        try:
            account_links = stripe.AccountLink.create(
                account=host.stripe_id,
                refresh_url="https://v2.host.scanbandz.com",
                return_url="https://v2.host.scanbandz.com",
                type="account_onboarding",
                collection_options={"fields": "eventually_due"},
            )
        except stripe.StripeError as e:
            raise HostStripeAccountNotFoundException(
                "Error creating Stripe account link"
            )
        return account_links.url

    def get_update_link(self, host_id: int) -> str:
        """
        Retrieves the Stripe update link for a host.

        Args:
            host_id (int): The ID of the host to retrieve the update link for.

        Returns:
            str: The Stripe update link.

        Raises:
            HostStripeAccountNotFoundException: If the host does not have a Stripe account.
        """
        host = self.host_service.get_by_id(host_id)

        if host.stripe_id is None:
            raise HostStripeAccountNotFoundException()

        try:
            account_links = stripe.AccountLink.create(
                account=host.stripe_id,
                refresh_url="https://v2.host.scanbandz.com",
                return_url="https://v2.host.scanbandz.com",
                type="account_update",
            )
        except stripe.InvalidRequestError as e:
            # Needs to onboard first
            return self.get_onboarding_link(host_id)
        except stripe.StripeError as e:
            raise HostStripeAccountNotFoundException(
                f"Error creating Stripe account link: {e}"
            )
        return account_links.url

    def is_account_enabled(self, host_id: int) -> bool:
        host = self.host_service.get_by_id(host_id)

        if host.stripe_id is None:
            raise HostStripeAccountNotFoundException()

        account = stripe.Account.retrieve(host.stripe_id)

        # Check if any requirements are pending
        if (
            account["capabilities"]["transfers"] == "active"
            and account["payouts_enabled"]
        ):
            # Fully verified and can receive payouts
            return True
        else:
            return False

    def get_account_link(self, host_id: int) -> str:
        host = self.host_service.get_by_id(host_id)

        if not host.stripe_id:
            raise HostStripeAccountNotFoundException()

        if not self.is_account_enabled(host_id):
            return self.get_onboarding_link(host_id)

        account = stripe.Account.create_login_link(host.stripe_id)
        return account.url
