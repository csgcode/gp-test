import requests

from allauth.socialaccount.models import SocialToken, SocialApp
from django.core.cache import cache


class FacebookWrapper(object):

    def __init__(self, access_token=None, user=None):
        self.user = None
        if not user and not access_token:
            raise AssertionError("user or fb access_token is necessary")
        elif access_token:
            self.access_token = access_token
        else:
            self.access_token = self._get_access_token(user)
            self.user = user
        self.base_url = 'https://graph.facebook.com/'
        self.page_details = None

    def _get_access_token(self, user):
        try:
            s_token = SocialToken.objects.get(account__user=user)
        except SocialToken.DoesNotExist:
            raise ValueError("The user object does not have any social token associated with it")
        token = s_token.token_secret or s_token.token
        return token

    def get_user_pages(self):
        _url = self.base_url+'me/accounts/'
        if self.user:
            pages = cache.get(f'fb_{self.user.id}')
            if not pages:
                pages = self._fetch_data(_url)
                cache.set(f'fb_{self.user.id}', pages, 600)
        else:
            pages = self._fetch_data(_url)
        return pages

    def get_page_detail(self, page_id, page_token):
        # fields needed add as qparams
        _url = f'{self.base_url}{page_id}?fields=about,attire,bio,emails,website,name&access_token={page_token}'
        res = requests.get(_url)
        return res.json()

    def get_all_page_details(self):
        pages = self.get_user_pages()
        self.page_details = []
        for page in pages['data']:
            self.page_details.append(self.get_page_detail(page['id'], page['access_token']))
        return self.page_details

    def get_page_token(self, page_id):
        pages = cache.get(f'fb_{self.user.id}')
        if not pages:
            pages = self.get_user_pages()
        page = list(filter(lambda item: item['id'] == str(page_id), pages['data']))
        return page[0]['access_token']

    def update_page_details(self, page_id, data):
        page_token = self.get_page_token(page_id)
        data.update({'access_token': page_token})
        _url = self.base_url+page_id
        id = data.pop('id', None)
        return self._post_data(_url, params=data)

    def _fetch_data(self, url, params=None):
        # TODO fix this
        res = requests.get(url, params={'access_token': self.access_token})
        return res.json()

    def _post_data(self, url, data=None, params=None):
        res = requests.post(url, params=params)
        return res.json()


def get_long_lived_token(user):
    # TODO add validation check, checck for the secret
    token = SocialToken.objects.get(account__user=user)
    s_app = SocialApp.objects.get(name='facebook')
    _url = f'''https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={s_app.client_id}&client_secret={s_app.secret}&fb_exchange_token={token.token}'''
    res = requests.get(_url)
    token.token_secret = res.json()['access_token']
    token.save()
