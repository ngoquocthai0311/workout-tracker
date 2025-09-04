from app.routers.mappers.base_mapper import BaseResponseMapper
from app.database.models import Exercise
from app.routers.schemas.response_schemas import ExerciseResponse
from typing import Sequence


class ExerciseMapper(BaseResponseMapper):
    def map_list_to_response(self, exercises: Sequence[Exercise]):
        # return as it is because there's no need for special mapping
        return exercises

    def transform_to_response(self, exercise: Exercise, max_weight: int = 0):
        response_model = ExerciseResponse.model_validate(exercise)

        if max_weight:
            response_model.max_weight = max_weight

        return response_model
