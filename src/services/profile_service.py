import os
from typing import AsyncGenerator

from fastapi import Depends, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.orm import load_only, joinedload

from src.models.sessions import get_async_session
from src.models.tables import Profile, User
from src.schemas.user_schema import TokenUserSchema
from src.services.user_service import get_current_user
from src.services.auxiliary_service import UploadFileService


class ProfileService:
    def __init__(self, session: AsyncGenerator = Depends(get_async_session),
                 current_user: TokenUserSchema = Depends(get_current_user)):
        self.session = session
        self.current_user = current_user
        self.user_id = self.current_user['id']

    async def create_profile(self):
        await self.session.execute(insert(Profile).values(user_id=self.user_id).returning(Profile))
        await self.session.commit()
        return self.get_profile(self.user_id)

    async def profile(self):
        return await self.get_profile(self.user_id)

    async def get_profile(self, user_id):

        profile = await self.session.execute(select(Profile).filter(Profile.user_id == int(user_id)).options(
            load_only(Profile.id, Profile.date_of_birth, Profile.city_of_birth, Profile.city_of_residence,
                      Profile.family_status, Profile.photography, Profile.additional_information)
                .selectinload(Profile.user).load_only(User.id, User.username, User.first_name, User.last_name)
        ))

        profile = profile.scalars().one_or_none()

        if user_id == self.user_id and profile is None:
            return await self.create_profile()
        elif profile is None:
            raise HTTPException(status_code=404, detail={'status': 404, 'data': {'errors': 'page not found'}})
        return {'user_id': profile.user.id,
                'profile_id': profile.id,
                'username': profile.user.username,
                'first_name': profile.user.first_name,
                'last_name': profile.user.last_name,
                'date_of_birth': profile.date_of_birth,
                'city_of_birth': profile.city_of_birth,
                'city_of_residence': profile.city_of_residence,
                'family_status': profile.family_status,
                'photography': profile.photography,
                'additional_information': profile.additional_information}

    async def get_profiles(self):
        try:
            profiles = await self.session.execute(select(Profile).options(
                load_only(Profile.id, Profile.date_of_birth, Profile.city_of_birth, Profile.city_of_residence,
                          Profile.family_status, Profile.photography, Profile.additional_information)
                    .selectinload(Profile.user).load_only(User.id, User.username, User.first_name, User.last_name)
            ))
        except Exception as errData:
            print('ProfileService.get_profiles -> : ', errData)
            return HTTPException(status_code=500, detail={'status': 500, 'data': {'errors': 'server error'}})
        profiles = profiles.scalars().all()
        return [{'user_id': profile.user.id,
                 'profile_id': profile.id,
                 'username': profile.user.username,
                 'first_name': profile.user.first_name,
                 'last_name': profile.user.last_name,
                 'date_of_birth': profile.date_of_birth,
                 'city_of_birth': profile.city_of_birth,
                 'city_of_residence': profile.city_of_residence,
                 'family_status': profile.family_status,
                 'photography': profile.photography,
                 'additional_information': profile.additional_information} for profile in profiles]

    async def update_profile(self, profile):
        uploded_file = None
        if profile.photography is not None:
            uploded_file = await UploadFileService.upload_image(profile.photography, 'user_profiles',
                                                                self.current_user['username'], (300, 700))
        try:
            await self.session.execute(update(User)
                                       .filter(User.id == self.user_id)
                                       .values(first_name=profile.first_name, last_name=profile.last_name))
            await self.session.execute(update(Profile)
                                       .filter(Profile.user_id == self.user_id)
                                       .values(date_of_birth=profile.date_of_birth,
                                               city_of_birth=profile.city_of_birth,
                                               city_of_residence=profile.city_of_residence,
                                               family_status=profile.family_status,
                                               photography=uploded_file,
                                               additional_information=profile.additional_information))

            await self.session.commit()
        except Exception as errData:
            print('ProfileService.update_profile -> ', errData)
            if uploded_file is not None:
                os.remove(uploded_file)
            raise HTTPException(status_code=500, detail={'status': 500, 'data': {'errors': 'server error'}})

        profile = await self.profile()

        return {'status': 204, 'data': {'message': 'resource updated successfully', 'post': profile, }}
