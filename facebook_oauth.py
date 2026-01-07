# To use this, install with: pip install authlib
# And set your Facebook OAuth credentials in environment variables or config
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
import os

router = APIRouter()

FACEBOOK_CLIENT_ID = os.environ.get("FACEBOOK_CLIENT_ID", "your-facebook-client-id")
FACEBOOK_CLIENT_SECRET = os.environ.get("FACEBOOK_CLIENT_SECRET", "your-facebook-client-secret")

oauth = OAuth()
oauth.register(
    name='facebook',
    client_id=FACEBOOK_CLIENT_ID,
    client_secret=FACEBOOK_CLIENT_SECRET,
    access_token_url='https://graph.facebook.com/v10.0/oauth/access_token',
    access_token_params=None,
    authorize_url='https://www.facebook.com/v10.0/dialog/oauth',
    authorize_params=None,
    api_base_url='https://graph.facebook.com/v10.0/',
    client_kwargs={'scope': 'email public_profile'},
)

@router.get('/login/facebook')
async def login_via_facebook(request: Request):
    redirect_uri = request.url_for('auth_facebook_callback')
    return await oauth.facebook.authorize_redirect(request, redirect_uri)

@router.get('/auth/facebook/callback')
async def auth_facebook_callback(request: Request, db=Depends(lambda: None)):
    try:
        token = await oauth.facebook.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(status_code=400, detail="Facebook OAuth failed")
    resp = await oauth.facebook.get('me?fields=id,name,email', token=token)
    user_info = resp.json()
    # Here, you would look up or create the user in your DB
    # For now, just return the user info
    return user_info
