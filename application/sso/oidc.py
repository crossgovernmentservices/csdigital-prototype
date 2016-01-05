import requests


class OIDC(object):
    """
    Handles creation of OIDCProviders
    """

    def __init__(self, app):
        self.providers = app.config['OIDC']

    def provider(self, provider):
        """
        Construct an OIDCProvider for the specified IdP
        """

        if provider in self.providers:
            return OIDCProvider(self.config(provider))

    def provider_from_host(self, host):

        matches = [
            provider for provider, config in self.providers.items()
            if host in config['domain']]

        return OIDCProvider(self.config(matches[0]))

    def config(self, provider):
        """
        Retrieve the OpenID configuration of the specified provider
        """

        return requests.get(
            'https://{domain}/.well-known/openid-configuration'.format(
                domain=self.providers[provider]['domain'])).json()

    def login(self, provider):
        """
        Convenience method to return an authentication URL for a provider
        """

        client = OIDCClient(self.providers[provider]['client'])
        provider = self.provider(provider)
        return client.authentication_url(provider)

    def authenticate(self, provider, auth_code):
        """
        Convenience method to authenticate a user and retrieve their userinfo
        """

        client = OIDCClient(self.providers[provider]['client'])
        provider = self.provider(provider)
        token_response = client.token_request(provider, auth_code)
        access_token = token_response['access_token']
        return client.userinfo_request(provider, access_token)


class DynamicRegistrationNotSupported(Exception):
    pass


class OIDCProvider(object):

    def __init__(self, config):
        self.config = config

    @property
    def authentication_endpoint(self):
        # OIDC renames the OAuth Authorization endpoint to the Authentication
        # endpoint (slightly confusing).
        return self.config['authorization_endpoint']

    @property
    def registration_endpoint(self):

        if 'registration_endpoint' not in self.config:
            raise DynamicRegistrationNotSupported()

        return self.config['registration_endpoint']

    @property
    def token_endpoint(self):
        return self.config['token_endpoint']

    @property
    def userinfo_endpoint(self):
        return self.config['userinfo_endpoint']


class OIDCClient(object):
    """
    Enables authentication against an OpenID Connect Provider
    """

    def __init__(self, config):
        self.config = config

    def register(self, provider):
        """
        Dynamically register this client with a provider
        """

        response = requests.post(
            provider.registration_endpoint,
            data=self.metadata,
            headers={'Content-Type': 'application/json'}).json()

        self.client_id = response['client_id']
        self.client_secret = response.get('client_secret')
        self.secret_expiry = response.get('client_secret_expires_at')

    def authentication_url(self, provider):
        """
        Generate the URL for the provider's authentication endpoint.
        This is the URL to redirect to to get the provider's login page. The
        login form will then redirect to `self.redirect_uri` with an
        authentication code.
        """

        return (
            '{endpoint}?'
            'scope=openid+email+profile&'
            'response_type=code&'
            'client_id={client_id}&'
            'redirect_uri={redirect_uri}').format(
                endpoint=provider.authentication_endpoint,
                client_id=self.config['client_id'],
                redirect_uri=self.config['redirect_uri'])

    @property
    def metadata(self):
        return {
            'redirect_uris': [],
            'response_types': ['code'],
            'grant_types': ['authorization_code'],
            'application_type': 'web',
            'contacts': ['user@example.com'],
            'client_name': self.name,
            'subject_type': 'pairwise'}

    def token_request(self, provider, auth_code):
        """
        Exchange provider auth code for an ID Token and an Access Token
        """

        payload = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'redirect_uri': self.config['redirect_uri'],
            'code': auth_code,
            'grant_type': 'authorization_code'}

        response = requests.post(
            provider.token_endpoint,
            data=payload,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        response = response.json()

        if 'error' in response:
            raise Exception(response['error_description'])

        return response

    def userinfo_request(self, provider, access_token):
        """
        Get userinfo Claims from the provider using an Access Token
        """

        response = requests.get(
            provider.userinfo_endpoint,
            headers={
                'Authorization': 'Bearer {token}'.format(token=access_token)})

        return response.json()
