from app.routers.mappers.base_mapper import BaseResponseMapper
from app.routers.schemas.response_schemas import (
    SessionExerciseResponse,
    SessionResponse,
)
from typing import Sequence
from app.database.models import WorkoutSession


class WorkoutSessionMapper(BaseResponseMapper):
    def map_list_to_response(self, workout_sessions: Sequence[WorkoutSession]):
        results: list[SessionResponse] = []
        for workout_session in workout_sessions:
            session_response_model: SessionResponse = SessionResponse.model_validate(
                workout_session
            )

            # create a dictionary to look up for each exercise plus its sets
            dictionary: dict[int, SessionExerciseResponse] = {}
            for session_exercise in workout_session.exercise_links:
                if session_exercise.order not in dictionary.keys():
                    # TODO: make sure database has consistent data
                    dictionary[session_exercise.order] = (
                        SessionExerciseResponse.model_validate(
                            session_exercise
                            if not session_exercise.exercise
                            else session_exercise.exercise
                        )
                    )
                    dictionary[session_exercise.order].sets = []
                session_exercise_response_model = (
                    SessionExerciseResponse.SessionExerciseSetResponse.model_validate(
                        session_exercise
                    )
                )
                session_exercise_response_model.session_exercise_id = (
                    session_exercise.id
                )

                dictionary[session_exercise.order].sets.append(
                    session_exercise_response_model
                )

            session_response_model.exercises = []
            for value in dictionary.values():
                session_response_model.exercises.append(value)

            results.append(session_response_model)

        return results

    def transform_to_response(self, workout_session: WorkoutSession):
        session_response_model: SessionResponse = SessionResponse.model_validate(
            workout_session
        )
        # create a dictionary to look up for each exercise plus its sets
        dictionary: dict[int, SessionExerciseResponse] = {}
        for session_exercise in workout_session.exercise_links:
            if session_exercise.order not in dictionary.keys():
                # add new order to dict
                dictionary[session_exercise.order] = (
                    SessionExerciseResponse.model_validate(session_exercise.exercise)
                )
                dictionary[session_exercise.order].sets = []

            session_exercise_response_model = (
                SessionExerciseResponse.SessionExerciseSetResponse.model_validate(
                    session_exercise
                )
            )
            session_exercise_response_model.session_exercise_id = session_exercise.id
            session_exercise_response_model.set_type = session_exercise.set_type

            dictionary[session_exercise.order].sets.append(
                session_exercise_response_model
            )

        session_response_model.exercises = []
        for value in dictionary.values():
            session_response_model.exercises.append(value)

        return session_response_model
