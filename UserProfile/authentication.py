from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    JWT 인증을 쿠키와 헤더 모두에서 지원하는 커스텀 인증 클래스
    """
    
    def authenticate(self, request):
        # 먼저 헤더에서 토큰을 찾아보기
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
            if raw_token is not None:
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token
        
        # 헤더에 토큰이 없으면 쿠키에서 찾기
        cookie_token = request.COOKIES.get('access_token')
        if cookie_token:
            try:
                validated_token = self.get_validated_token(cookie_token)
                return self.get_user(validated_token), validated_token
            except (InvalidToken, TokenError):
                pass
        
        return None
