import requests

from typing import Dict
from typing import List


class IBClient:
    def __init__(self):
        self.baseUrl = "https://localhost:5000/v1/portal/"

    def _build_url(self, endpoint):
        return self.baseUrl + endpoint

    def _make_request(self, endpoint: str, req_type: str, params: Dict = None) -> Dict:
        """Handles the request to the client.
        Handles all the requests made by the client and correctly organizes
        the information so it is sent correctly. Additionally it will also
        build the URL.
        Arguments:
        ----
        endpoint {str} -- The endpoint we wish to request.
        req_type {str} --  Defines the type of request to be made. Can be one of four
            possible values ['GET','POST','DELETE','PUT']
        params {dict} -- Any arguments that are to be sent along in the request. That
            could be parameters of a 'GET' request, or a data payload of a
            'POST' request.

        Returns:
        ----
        {Dict} -- A response dictionary.
        """

        url = self._build_url(endpoint=endpoint)
        headers = {'Content-Type': 'application/json'}

        if req_type == 'POST' and params is not None:
            response = requests.post(url, headers=headers, json=params, verify=False)
        elif req_type == 'POST' and params is None:
            response = requests.post(url, headers=headers, verify=False)
        elif req_type == 'GET' and params is not None:
            response = requests.get(url, headers=headers, params=params, verify=False)
        elif req_type == 'GET' and params is None:
            response = requests.get(url, headers=headers, verify=False)

        if response.ok:
            return response.json()
        else:  # elif not response.ok and url != 'https://localhost:5000/v1/portal/iserver/account':
            print('')
            print('-' * 80)
            print("BAD REQUEST - STATUS CODE: {}".format(response.status_code))
            print("RESPONSE URL: {}".format(response.url))
            print("RESPONSE HEADERS: {}".format(response.headers))
            print("RESPONSE TEXT: {}".format(response.text))
            print('-' * 80)
            print('')

    def _prepare_arguments_list(self, parameter_list: List[str]) -> str:
        """Prepares the arguments for the request.
        Some endpoints can take multiple values for a parameter, this
        method takes that list and creates a valid string that can be
        used in an API request. The list can have either one index or
        multiple indexes.
        Arguments:
        ----
        parameter_list {List} -- A list of parameter values assigned to an argument.

        Returns:
        ----
        {str} -- The joined list.
        """

        # validate it's a list. If not, return the parameter
        if type(parameter_list) is list:
            # specify the delimiter and join the list.
            delimiter = ','
            parameter_list = delimiter.join(parameter_list)

        return parameter_list

    """
        PORTFOLIO ACCOUNTS ENDPOINTS
    """

    def portfolio_accounts(self):
        """
            In non-tiered account structures, returns a list of accounts for which the
            user can view position and account information. This endpoint must be called prior
            to calling other /portfolio endpoints for those accounts. For querying a list of accounts
            which the user can trade, see /iserver/accounts. For a list of subaccounts in tiered account
            structures (e.g. financial advisor or ibroker accounts) see /portfolio/subaccounts.
        """

        # define request components
        endpoint = 'portfolio/accounts'
        req_type = 'GET'
        content = self._make_request(endpoint=endpoint, req_type=req_type)

        return content

    def brokerage_accounts(self):
        """
            Returns a list of accounts the user has trading access to, their respective aliases
            and the currently selected account. Note this endpoint must be called before
            modifying an order or querying open orders.
        """

        # define request components
        endpoint = r'iserver/accounts'
        req_type = 'GET'
        content = self._make_request(endpoint=endpoint, req_type=req_type)

        return content

    def portfolio_account_positions(self, account_id: str, page_id: int = 0) -> Dict:
        """
            Returns a list of positions for the given account. The endpoint supports paging,
            page's default size is 30 positions. /portfolio/accounts or /portfolio/subaccounts
            must be called prior to this endpoint.
            NAME: account_id
            DESC: The account ID you wish to return positions for.
            TYPE: String
            NAME: page_id
            DESC: The page you wish to return if there are more than 1. The
                  default value is `0`.
            TYPE: String
            ADDITIONAL ARGUMENTS NEED TO BE ADDED!!!!!
        """

        # define request components
        endpoint = r'portfolio/{}/positions/{}'.format(account_id, page_id)
        req_type = 'GET'
        content = self._make_request(endpoint=endpoint, req_type=req_type)

        return content

    def market_data(self, conids: List[str], since: str, fields: List[str]) -> Dict:
        """
            Get Market Data for the given conid(s). The end-point will return by
            default bid, ask, last, change, change pct, close, listing exchange.
            See response fields for a list of available fields that can be request
            via fields argument. The endpoint /iserver/accounts should be called
            prior to /iserver/marketdata/snapshot. To receive all available fields
            the /snapshot endpoint will need to be called several times.
            NAME: conid
            DESC: The list of contract IDs you wish to pull current quotes for.
            TYPE: List<String>
            NAME: since
            DESC: Time period since which updates are required.
                  Uses epoch time with milliseconds.
            TYPE: String
            NAME: fields
            DESC: List of fields you wish to retrieve for each quote.
            TYPE: List<String>
        """

        # define request components
        endpoint = r'iserver/marketdata/snapshot'
        req_type = 'GET'

        # join the two list arguments so they are both a single string.
        conids_joined = self._prepare_arguments_list(parameter_list=conids)

        if fields is not None:
            fields_joined = ",".join(str(n) for n in fields)
        else:
            fields_joined = ""

        # define the parameters
        if since is None:
            params = {
                'conids': conids_joined,
                'fields': fields_joined
            }
        else:
            params = {
                'conids': conids_joined,
                'since': since,
                'fields': fields_joined
            }

        content = self._make_request(endpoint=endpoint, req_type=req_type, params=params)
        return content

    def reauthenticate(self) -> Dict:
        """Reauthenticates an existing session.
        Provides a way to reauthenticate to the Brokerage system as long as there
        is a valid SSO session, see /sso/validate.
        """

        # define request components
        endpoint = r'iserver/reauthenticate'
        req_type = 'POST'

        content = self._make_request(endpoint=endpoint, req_type=req_type)

        return content

    def authentication_status(self) -> Dict:
        """Checks if session is authenticated.
        Current Authentication status to the Brokerage system. Market Data and
        Trading is not possible if not authenticated, e.g. authenticated
        shows `False`.
        """

        # define request components
        endpoint = r'iserver/auth/status'
        req_type = 'POST'
        content = self._make_request(endpoint=endpoint, req_type=req_type)

        return content

    def validateSSO(self) -> Dict:
        """Validates the current session for the SSO user."""

        # define request components
        endpoint = r'sso/validate'
        req_type = 'GET'
        content = self._make_request(endpoint=endpoint, req_type=req_type)

        return content

    def tickle(self) -> Dict:
        """Keeps the session open.
        If the gateway has not received any requests for several minutes an open session will
        automatically timeout. The tickle endpoint pings the server to prevent the
        session from ending.
        """

        # define request components
        endpoint = r'tickle'
        req_type = 'POST'
        content = self._make_request(endpoint=endpoint, req_type=req_type)

        return content