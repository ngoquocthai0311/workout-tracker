from app.routers.mappers.base_mapper import BaseResponseMapper
from app.database.models import Exercise
from app.routers.schemas.response_schemas import ExerciseResponse, MaxWeightResponse
from typing import Sequence


class ExerciseMapper(BaseResponseMapper):
    def map_list_to_response(self, exercises: Sequence[Exercise]):
        # return as it is because there's no need for special mapping
        results: list[ExerciseResponse] = []
        for exercise in exercises:
            result = ExerciseResponse.model_validate(exercise)
            if exercise.personal_record:
                result.personal_record = MaxWeightResponse.model_validate(
                    exercise.personal_record
                )
            results.append(result)
        return results

    def transform_to_response(self, exercise: Exercise):
        # return as it is because there's no need for special mapping
        result: ExerciseResponse = ExerciseResponse.model_validate(exercise)
        if exercise.personal_record:
            result.personal_record = MaxWeightResponse.model_validate(
                exercise.personal_record
            )
        return result
