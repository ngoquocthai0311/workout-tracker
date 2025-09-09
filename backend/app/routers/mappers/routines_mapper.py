from app.routers.mappers.base_mapper import BaseResponseMapper
from app.routers.schemas.response_schemas import RoutineResponse
from typing import Sequence
from app.database.models import Routine
from app.routers.schemas.response_schemas import RoutineExerciseResponse


class RoutineMapper(BaseResponseMapper):
    def map_list_to_response(self, routines: Sequence[Routine]):
        results: list[RoutineResponse] = []
        # mapping each routine
        for routine in routines:
            # construct response dict
            routine_response = RoutineResponse.model_validate(routine)

            exercises: list[RoutineExerciseResponse] = []
            # map for each exercise and its set
            for exercise_link in routine.exercise_links:
                exercise: RoutineExerciseResponse = (
                    RoutineExerciseResponse.model_validate(exercise_link.exercise)
                )
                exercise.exercise_id = exercise.id
                exercise.id = exercise_link.id
                exercise.sets = exercise_link.routine_exercise_sets
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

        exercises: list[RoutineExerciseResponse] = []
        # map for each set
        for exercise_link in routine.exercise_links:
            exercise: RoutineExerciseResponse = RoutineExerciseResponse.model_validate(
                exercise_link.exercise
            )
            exercise.exercise_id = exercise.id
            exercise.id = exercise_link.id
            exercise.sets = exercise_link.routine_exercise_sets
            exercises.append(exercise)

        results.exercises = exercises

        return results
