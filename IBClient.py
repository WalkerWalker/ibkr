import requests

from typing import Dict
from typing import List
from pprint import pprint


class IBClient:
    def __init__(self):
        self.baseUrl = "https://localhost:5000/v1/portal/"
        self.authenticated = False
        self.authenticated = self._authenticate()

    def _authenticate(self) -> bool:
        max_retries = 4
        retries = 0

        while max_retries > retries or self.authenticated is False:

            auth_response = self.authentication_status()

            if 'statusCode' in auth_response.keys() and auth_response['statusCode'] == 401:
                print("Server isn't connected. Authentication Failed")
                self.authenticated = False
                return False

            elif 'authenticated' in auth_response.keys() and auth_response['authenticated'] is True:
                self.authenticated = True
                return True

            elif 'authenticated' in auth_response.keys() and auth_response['authenticated'] is False:
                self.validate_SSO()
                self.reauthenticate()
                self.brokerage_accounts()
                # self.authentication_status()

            retries += 1

        return self.authenticated

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

        response = None
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

    def market_data(self, conids: List[int], since: str = None, fields: List[str] = ['31']) -> Dict:
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

        # define the parameters
        params ={}
        conids_joined = ",".join(str(conid) for conid in conids)
        params['conids'] = conids_joined

        fields_joined = ",".join(str(field) for field in fields)
        params['fields'] = fields_joined

        if since is not None:
            params['since'] = since

        content = self._make_request(endpoint=endpoint, req_type=req_type, params=params)
        # retry if the field is not there
        retry = False
        for field in fields:
            if field not in content[0].keys():
                retry = True
                break

        if retry:
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

    def validate_SSO(self) -> Dict:
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

    def contracts_definitions(self, conids: List[int]) -> List[Dict]:
        """
            Returns a list of security definitions for the given conids.
            NAME: conids
            DESC: A list of contract IDs you wish to get details for.
            TYPE: List<Integer>
            RTYPE: List<Dictionary>
        """

        # define the request components
        endpoint = '/trsrv/secdef'
        req_type = 'POST'
        payload = {
            'conids': conids
            }
        content = self._make_request(endpoint=endpoint, req_type=req_type, params=payload)

        return content['secdef']
