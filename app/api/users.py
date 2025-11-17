from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.services.user_service import UserService
from app.models.user_models import UserCreate, UserResponse, Token
from config import settings

# 等价于Java的：@RestController @RequestMapping("/users")
router = APIRouter(prefix="/users", tags=["users"])
# 来自 fastapi.security 模块 用于实现 OAuth2 密码流程的承载令牌认证 专门处理在请求头中传递的 Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


# 用户注册
@router.post("/register", response_model=UserResponse)
# async相当于Java的CompletableFuture异步处理
async def register(user: UserCreate):
    # 检查用户是否已存在
    if UserService.get_user_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    created_user = UserService.create_user(user)
    # 用户创建失败
    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败"
        )

    # 用户创建成功直接返回
    return created_user

# 用户登录
@router.post("/token", response_model=Token)
# OAuth2PasswordRequestForm: FastAPI 内置的表单数据模型，自动解析 username 和 password 字段 Depends()相当于@Autowired
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = UserService.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = UserService.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}