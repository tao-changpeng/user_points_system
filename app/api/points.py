from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from jose import jwt, JWTError

from app.api.users import oauth2_scheme
from app.services.point_service import PointService
from app.services.user_service import UserService
from app.models.point_models import PointRecordCreate, PointRecordResponse, LevelUpResponse
from app.models.user_models import UserInDB
from config import settings

router = APIRouter(prefix="/points", tags=["points"])

# JWT 认证依赖函数
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = UserService.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


# 添加积分端点
@router.post("/add", response_model=dict)
async def add_points(
        points_data: PointRecordCreate,
        current_user: UserInDB = Depends(get_current_user)
):
    success, level_up = PointService.add_points(current_user.id, points_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加积分失败"
        )

    response = {"message": "积分添加成功", "points_added": points_data.points_change}
    if level_up:
        response["level_up"] = level_up

    return response


# 获取积分历史端点
@router.get("/history", response_model=List[PointRecordResponse])
async def get_points_history(
        current_user: UserInDB = Depends(get_current_user),
        limit: int = 50
):
    return PointService.get_user_points_history(current_user.id, limit)


# 获取等级历史端点
@router.get("/level-history")
async def get_level_history(current_user: UserInDB = Depends(get_current_user)):
    return PointService.get_user_level_history(current_user.id)