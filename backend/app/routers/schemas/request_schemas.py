from typing import Optional

from pydantic import RootModel
from sqlmodel import SQLModel


# region User request schemas
class CreateUserRequest(SQLModel):
    username: str


class UpdateUserRequest(SQLModel):
    username: str


# endregion

# region Exercise request schemas


class CreateExerciseRequest(SQLModel):
    name: str
    description: Optional[str] = None
    user_id: int = 1  # Default to user_id 1 for simplicity, can be changed later


class UpdateExerciseRequest(SQLModel):
    name: str
    description: Optional[str] = None
    user_id: Optional[int]


# endregion


# region Routine request schemas


class CreateRoutineRequest(SQLModel):
    class RoutineExerciseRequest(SQLModel):
        class ExerciseSet(SQLModel):
            set_type: Optional[str] = "normal"
            targeted_weight: Optional[int] = 0
            targeted_reps: Optional[int] = 0

        exercise_id: Optional[int] = None
        sets: list[ExerciseSet] = None

    name: str
    description: Optional[str] = None
    exercises: Optional[list[RoutineExerciseRequest]] = None
    user_id: int = 1  # Default to user_id 1 for simplicity, can be changed later


class UpdateRoutineRequest(SQLModel):
    class RoutineExerciseRequest(SQLModel):
        class ExerciseSet(SQLModel):
            id: Optional[int] = None
            set_type: Optional[str] = "normal"
            targeted_weight: Optional[int] = 0
            targeted_reps: Optional[int] = 0

        id: Optional[int] = None
        exercise_id: int
        sets: list[ExerciseSet] = None

    name: str
    description: Optional[str] = None
    exercises: Optional[list[RoutineExerciseRequest]] = None
    user_id: int


# endregion


# region Workout Session request schemas
class CreateWorkoutSessionRequest(SQLModel):
    class RoutineExerciseRequest(SQLModel):
        class ExerciseSet(SQLModel):
            set_type: Optional[str] = "normal"
            weight_lifted: Optional[int] = 0
            reps_completed: Optional[int] = 0

        id: int
        sets: list[ExerciseSet] = None

        # TODO: Notes field can be add for each workout session exercise link
        notes: Optional[str] = None

    name: Optional[str] = None
    description: Optional[str] = None
    routine_id: Optional[int] = None
    exercises: Optional[list[RoutineExerciseRequest]] = None
    user_id: int = 1  # Default to user_id 1 for simplicity, can be changed later
    notes: Optional[str] = None


class UpdateWorkoutSessionRequest(SQLModel):
    class RoutineExerciseRequest(SQLModel):
        class ExerciseSet(SQLModel):
            id: Optional[int] = None
            set_type: Optional[str] = "normal"
            weight_lifted: Optional[int] = 0
            reps_completed: Optional[int] = 0

        id: int
        sets: list[ExerciseSet] = None

        # TODO: Notes field can be add for each workout session exercise link
        notes: Optional[str] = None

    name: Optional[str] = None
    description: Optional[str] = None
    routine_id: Optional[int] = None
    exercises: Optional[list[RoutineExerciseRequest]] = None
    user_id: int = None
    notes: Optional[str] = None


# endregion

# region Report request schemas


class DayReportRequest(SQLModel):
    total_weights: int = 0


class WeekReportRequest(RootModel[dict[str, int]]):
    root: dict[str, int]


class YearReportRequest(RootModel[dict[str, int]]):
    root: dict[str, int]
