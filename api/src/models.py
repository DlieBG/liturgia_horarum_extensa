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
    antiphon = 'antiphon'

class Verse(BaseModel):
    type: VerseType
    text: Optional[str] = None
    ordination: Optional[int] = None
    sheet: Optional[str] = None

class Section(BaseModel):
    title: Optional[str] = None
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
        __verse_type = {
            'format_none': 'generic',
            'format_removeFormat': 'generic',
            'format_subhbold': 'comment',
            'format_subh': 'comment',
            'format_center': 'comment',
            'format_bold': 'subtitle',
            'format_preAnt': 'response',
            'format_preFirstAnt': 'response',
            'format_preSecAnt': 'response',
            'format_preThiAnt': 'response',
            'format_preOra': 'oration',
            'format_preAntiphon': 'antiphon',
        }

        __verse_ordination = {
            'format_preFirstAnt': 1,
            'format_preSecAnt': 2,
            'format_preThiAnt': 3,
        }

        html = BeautifulSoup(
            markup=raw,
            features='html.parser'
        )

        sections = []
        current_section = Section(
            title=None,
            verses=[],
        )

        for element in html.children:
            if element.name:
                match element.name:
                    case 'h2':
                        if element.text.strip().upper() == element.text.strip():
                            sections.append(current_section)

                            current_section = Section(
                                title=element.text.strip(),
                                verses=[],
                            )
                        else:
                            current_section.verses.append(
                                Verse(
                                    type=VerseType.subtitle,
                                    ordination=None,
                                    text=element.text.strip(),
                                )
                            )
                    case 'p':
                        spans = element.find_all(
                            name='span',
                            attrs={
                                'class': 'hl',
                            },
                        )

                        for text in [
                            element.text.strip()
                        ] if len(spans) == 0 else [
                            span.text.strip()
                                for span in spans if span.text.strip() != ''
                        ]:
                            current_section.verses.append(
                                Verse(
                                    type=__verse_type.get(element['class'][0], VerseType.generic),
                                    ordination=__verse_ordination.get(element['class'][0], None),
                                    text=text,
                                )
                            )

        sections.append(current_section)
        return sections

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
