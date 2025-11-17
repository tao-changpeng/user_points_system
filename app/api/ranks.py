from fastapi import APIRouter, Depends, HTTPException
from typing import List

from starlette import status

from app.api.points import get_current_user
from app.services.rank_service import RankService
from app.models.point_models import RankUser
from app.models.user_models import UserInDB

router = APIRouter(prefix="/ranks", tags=["ranks"])

# 获取排行榜前limit位用户
@router.get("/top", response_model=List[RankUser])
async def get_top_ranks(limit: int = 10):
    return RankService.get_top_ranks(limit)

# 获取当前用户排名
@router.get("/my-rank", response_model=RankUser)
async def get_my_rank(current_user: UserInDB = Depends(get_current_user)):
    user_rank = RankService.get_user_rank(current_user.id)
    if not user_rank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到排名信息"
        )
    return user_rank

# 刷新排行榜
@router.post("/refresh")
async def refresh_rankings():
    RankService.refresh_rankings()
    return {"message": "排行榜刷新完成"}