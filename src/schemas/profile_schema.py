from datetime import date
from enum import Enum
from typing import Optional

from fastapi import Form, File, UploadFile
from pydantic import BaseModel, Field


class FamilyStatus(str, Enum):
    single = 'single'
    divorced = 'divorced'
    widowed = 'widowed'
    married = 'married'


class UpdateProfile(BaseModel):
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    date_of_birth: Optional[date] = None
    city_of_birth: Optional[str] = None
    city_of_residence: Optional[str] = None
    family_status: Optional[FamilyStatus] = None
    photography: Optional[UploadFile] = None
    additional_information: Optional[str] = None

    @classmethod
    def as_form(cls,
                first_name: str = Form(min_length=3, max_length=150),
                last_name: str = Form(min_length=3, max_length=150),
                date_of_birth: date = Form(None),
                city_of_birth: str = Form(None),
                city_of_residence: str = Form(None),
                family_status: FamilyStatus = Form(None),
                photography: UploadFile = File(None),
                additional_information: str = Form(None)
                ):
        return cls(first_name=first_name, last_name=last_name, date_of_birth=date_of_birth,
                   city_of_birth=city_of_birth, city_of_residence=city_of_residence, family_status=family_status,
                   photography=photography, additional_information=additional_information)
