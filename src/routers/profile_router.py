from fastapi import APIRouter, Depends

from src.schemas.profile_schema import UpdateProfile
from src.services.profile_service import ProfileService

router = APIRouter(tags=['profile'])


@router.get('/all')
async def get_profiles(service: ProfileService = Depends()):
    profiles = await service.get_profiles()
    return {'status': 200, 'data': {'profiles': profiles}}


@router.get('/get/{profile_id}')
async def get_profile(profile_id: int, service: ProfileService = Depends()):
    profile = await service.get_profile(profile_id)
    return {'status': 200, 'data': {'profile': profile}}


@router.get('/self')
async def profile(service: ProfileService = Depends()):
    profile = await service.profile()
    return {'status': 200, 'data': {'profile': profile}}


@router.put('/update')
async def update_profile(service: ProfileService = Depends(),
                         profile: UpdateProfile = Depends(UpdateProfile.as_form)):
    return await service.update_profile(profile)
