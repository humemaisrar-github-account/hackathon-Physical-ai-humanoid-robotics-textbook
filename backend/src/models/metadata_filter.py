from typing import Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class FilterOperator(str, Enum):
    """
    Enum for supported filter operators.
    """
    EQUALS = "equals"
    CONTAINS = "contains"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"


class MetadataFilter(BaseModel):
    """
    Model representing criteria used to narrow search results by specific attributes like page URL or section.
    """
    field: str = Field(..., description="The field to filter on (e.g., 'url', 'section_hierarchy')")
    value: Union[str, int, float] = Field(..., description="The value to match")
    operator: FilterOperator = Field(
        FilterOperator.EQUALS,
        description="The comparison operator (e.g., 'equals', 'contains')"
    )

    @field_validator('field')
    def validate_field(cls, v):
        """
        Validate that the field name is allowed.
        """
        allowed_fields = {'url', 'section', 'section_hierarchy', 'chunk_id', 'position'}
        if v not in allowed_fields:
            raise ValueError(f'Invalid filter field: {v}. Allowed fields: {allowed_fields}')
        return v

    @field_validator('value')
    def validate_value(cls, v):
        """
        Validate that the value is not empty for string types.
        """
        if isinstance(v, str) and not v.strip():
            raise ValueError('Filter value cannot be empty')
        return v