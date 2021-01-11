from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView

from apps.accounts.utils import get_long_lived_token, FacebookWrapper


class FacebookLoginView(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter

    def process_login(self):
        super().process_login()
        print("flowa after sucessfull process")
        if self.request.user:
            get_long_lived_token(self.request.user)


class PagesListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            fb = FacebookWrapper(user=request.user)
            pages_list = fb.get_all_page_details()
        except Exception as e:
            # TODO remove exception
            print("exception", e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # pages_list = [{"about":"this is api about222","bio":"this is api bio222","website":"http://www.website.com/","name":"Test page","id":"102461438483120"},{"about":"Food blog Insights ","name":"Food blog","id":"106891001362690"}]
        return Response(data=pages_list, status=status.HTTP_200_OK)


class PageUpdateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        page_id = request.data.get('id')
        data = request.data.get('data')
        if not page_id:
            return Response(status.HTTP_400_BAD_REQUEST)
        fb = FacebookWrapper(user=request.user)
        res = fb.update_page_details(page_id=page_id, data=data)
        updated_data = fb.get_all_page_details()

        return Response(data={'data': updated_data}, status=status.HTTP_202_ACCEPTED)
