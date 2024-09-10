from pydantic import field_validator, BaseModel, Field

class DayOfPrayer(BaseModel):
    date: str = Field(validation_alias='datum')
    day_name: str = Field(validation_alias='littag')
    week_name: str = Field(validation_alias='day_name')
    year_name: str = Field(validation_alias='year_name')
    daily_readings: list[str] = Field(validation_alias='te')
    daily_saints_memorial: list[str] = Field(validation_alias='tf')
    color: str = Field(validation_alias='color')

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
