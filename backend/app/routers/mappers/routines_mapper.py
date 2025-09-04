from app.routers.mappers.base_mapper import BaseResponseMapper
from app.routers.schemas.response_schemas import ExerciseResponse, RoutineResponse
from typing import Sequence
from app.database.models import Routine


class RoutineMapper(BaseResponseMapper):
    def map_list_to_response(self, routines: Sequence[Routine]):
        results: list[RoutineResponse] = []
        # mapping each routine
        for routine in routines:
            # construct response dict
            routine_response = RoutineResponse.model_validate(routine)
            routine_response.exercises = [
                routine_exercise.exercise for routine_exercise in routine.exercise_links
            ]

            exercises: list[ExerciseResponse] = []
            # map for each set
            for routine_exercise in routine.exercise_links:
                exercise: ExerciseResponse = ExerciseResponse.model_validate(
                    routine_exercise.exercise
                )
                exercise.sets = routine_exercise.routine_exercise_sets
                exercises.append(exercise)

            routine_response.exercises = exercises

            results.append(routine_response)

        return results

    def transform_to_response(self, routine: Routine):
        # construct response dict
        results = RoutineResponse.model_validate(routine)
        results.exercises = [
            routine_exercise.exercise for routine_exercise in routine.exercise_links
        ]

        exercises: list[ExerciseResponse] = []
        # map for each set
        for routine_exercise in routine.exercise_links:
            exercise: ExerciseResponse = ExerciseResponse.model_validate(
                routine_exercise.exercise
            )
            exercise.sets = routine_exercise.routine_exercise_sets
            exercises.append(exercise)

        results.exercises = exercises

        return results
