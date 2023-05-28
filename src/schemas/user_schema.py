from typing import Optional

from pydantic import BaseModel, EmailStr


class CreateUserSchema(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    # @validator('password')
    # @classmethod
    # def validate_password(cls, password):
    #     pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
    #     if re.match(pattern, password) is None:
    #         raise HTTPException(status_code=406, detail={'data': {
    #         'errors': settings.messages['validation']['PASSWORD']}})
    #     return password


class TokenUserSchema(BaseModel):
    id: int
    email: EmailStr
    username: str


class JWTToken(BaseModel):
    access_token: str
    token_type: str


class JWTTokenPayload(BaseModel):
    sub: str
    username: str
    email: EmailStr
    exp: int
