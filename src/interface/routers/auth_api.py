from typing import Optional
from urllib.parse import urlencode
from uuid import UUID
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from core.exceptions import (
    AlreadyExists,
    InvalidCredentials,
    InvalidGrantError,
    InvalidRequestError,
    NotFoundError,
    UnsupportedGrantTypeError,
)
from core.services.auth_service import AuthService
from interface.dependencies import get_auth_service
from interface.schemas.auth_schemas import (
    AuthorizationCodeRequest,
    TokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)


router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")  # added for current user


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_create: UserCreate, auth_service: AuthService = Depends(get_auth_service)
):
    try:
        created_user = await auth_service.register(
            user_create.email, user_create.password
        )
        return created_user
    except AlreadyExists as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/authorize")
async def authorize(
    request: Request, response: Response, params: AuthorizationCodeRequest = Depends()
):
    """
    Authorization endpoint (Step 1 & 2 & 3 of Authorization Code Grant).
    """

    # 1. Validate request parameters (you might want to do this more thoroughly)
    if params.response_type != "code":
        raise InvalidRequestError("Invalid response_type")
    # TODO: You should also validate client_id and redirect_uri against a list of registered clients

    # 2.  Build the URL for *your* login page
    login_url = request.url_for(
        "login_page"
    )  # Assuming you name your login endpoint "login_page"
    query_params = {
        "client_id": params.client_id,
        "redirect_uri": params.redirect_uri,
        "scope": params.scope or "",  # Ensure scope is a string
        "state": params.state or "",
    }

    redirect_url = f"{login_url}?{urlencode(query_params)}"
    response.status_code = 302
    response.headers["Location"] = redirect_url
    return response


@router.get("/login")
async def login_page(
    request: Request,
    client_id: str,
    redirect_uri: str,
    scope: Optional[str] = None,
    state: Optional[str] = None,
):
    """
    Displays the login form (Step 2 of Authorization Code Grant).  This is *your* login form.
    """
    templates = request.app.state.templates  # Получаем templates из state приложения
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
        },
    )


@router.post("/login")
async def process_login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    scope: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Processes the login form submission (Step 2 of Authorization Code Grant)."""
    try:
        user = await auth_service.login(form_data.username, form_data.password)
        if not user:
            raise InvalidCredentials()

        # 3. Create authorization code
        scopes = scope.split() if scope else []  # Convert scope string to list
        code = auth_service.create_authorization_code(
            client_id=client_id,
            redirect_uri=redirect_uri,
            user_id=user.id,
            scopes=scopes,
        )

        # 4. Redirect back to client's redirect_uri with the code
        redirect_params = {"code": code}
        if state:
            redirect_params["state"] = state
        redirect_url = f"{redirect_uri}?{urlencode(redirect_params)}"
        response.status_code = 302
        response.headers["Location"] = redirect_url
        return response

    except (NotFoundError, InvalidCredentials) as e:
        templates = (
            request.app.state.templates
        )  # Получаем templates из state приложения
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": scope,
                "state": state,
                "error": str(e),
            },
        )


@router.post("/token", response_model=TokenResponse)
async def token(
    token_request: TokenRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """
    Token endpoint (Step 4 & 5 of Authorization Code Grant).
    """

    # 1. Validate request
    if token_request.grant_type != "authorization_code":
        raise UnsupportedGrantTypeError()

    # 2. Exchange code for tokens
    try:
        token = await auth_service.exchange_code_for_token(
            code=token_request.code,
            client_id=token_request.client_id,
            redirect_uri=token_request.redirect_uri,
            client_secret=token_request.client_secret,  # Pass client_secret
        )
        return TokenResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            refresh_token=token.refresh_token,
            scopes=token.scopes,
        )
    except InvalidGrantError:
        raise HTTPException(
            status_code=400, detail="Invalid authorization code"
        )  # be more specific
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.logout(token)
    return {"message": "Successfully logged out"}
