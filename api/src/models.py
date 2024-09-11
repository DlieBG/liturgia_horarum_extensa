from pydantic import field_validator, BaseModel, Field
from bs4 import BeautifulSoup
from typing import Optional
from enum import Enum

class VerseType(Enum):
    generic = 'generic'
    subtitle = 'subtitle'
    comment = 'comment'
    response = 'response'
    oration = 'oration'

class Verse(BaseModel):
    type: VerseType
    text: Optional[str] = None
    ordination: Optional[int] = None
    sheet: Optional[str] = None

class Section(BaseModel):
    title: str
    verses: list[Verse]

class PrayerType(Enum):
    lesehore = 'Lesehore'
    invitatorium = 'Invitatorium'
    laufes = 'Laudes'
    vesper = 'Vesper'
    laudes = 'Laudes'
    terz = 'Terz'
    sext = 'Sext'
    non = 'Non'
    komplet = 'Komplet'
    tageslesungen = 'Tageslesungen'
    other = 'Other'

class Prayer(BaseModel):
    name: str
    type: PrayerType
    sections: list[Section]
    
    @field_validator('sections', mode='before')
    def parse_sections(raw: str) -> list[Section]:
        html = BeautifulSoup(raw)

        print(html.children)

        return [
            Section(
                title=html.prettify(),
                subtitle='',
                verses=[],
            )
        ]

class DayOfPrayer(BaseModel):
    date: str = Field(validation_alias='datum')
    day_name: str = Field(validation_alias='littag')
    week_name: str = Field(validation_alias='day_name')
    year_name: str = Field(validation_alias='year_name')
    book_name: str = Field(validation_alias='tg')
    daily_readings: list[str] = Field(validation_alias='te')
    daily_saints_memorial: list[str] = Field(validation_alias='tf')
    color: str = Field(validation_alias='color')
    prayers: list[Prayer] = Field(validation_alias='childs')

    @field_validator('daily_readings', mode='before')
    def split_daily_readings(raw: str) -> list[str]:
        return raw.split(';')

    @field_validator('daily_saints_memorial', mode='before')
    def split_daily_saints_memorial(raw: str) -> list[str]:
        if raw == '':
            return []

        return [
            item.strip() for item in raw.split(';')
        ]
    
    @field_validator('prayers', mode='before')
    def parse_prayers(raw: list) -> list[Prayer]:
        return [
            Prayer(
                name=prayer['name'],
                type=prayer['name'] if prayer['name'] in PrayerType._value2member_map_ else PrayerType.other,
                sections=prayer['html'],
            ) for prayer in raw
        ]
