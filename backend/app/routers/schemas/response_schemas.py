from pydantic import RootModel
from sqlmodel import SQLModel
from typing import Optional


# region Exercise response schemas
class ExerciseResponse(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: float
    updated_at: float
    max_weight: Optional[int] = None


# endregion


# region Routine response schemas
class ExerciseSetResponse(SQLModel):
    id: Optional[int] = None
    routine_exercise_id: Optional[int] = None
    set_type: str
    targeted_weight: int
    targeted_reps: int


class RoutineExerciseResponse(SQLModel):
    id: Optional[int] = None
    exercise_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_at: float
    updated_at: float
    max_weight: Optional[int] = None
    sets: list["ExerciseSetResponse"] = None


class RoutineResponse(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: float
    updated_at: float
    user_id: int
    exercises: list[RoutineExerciseResponse] = None


# endregion


# region Workout session response schemas
class SessionResponse(SQLModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: float
    updated_at: Optional[float] = None
    notes: Optional[str] = None

    # Relationships
    # routine: Optional[RoutineResponse] = None
    exercises: Optional[list["SessionExerciseResponse"]] = None


class SessionExerciseResponse(SQLModel):
    class SessionExerciseSetResponse(SQLModel):
        id: Optional[int] = 0
        set_type: Optional[str] = "normal"
        weight_lifted: Optional[int] = 0
        reps_completed: Optional[int] = 0

    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    sets: Optional[list[SessionExerciseSetResponse]] = None


# endregion


# region Report response schemas
class DayReportResponse(SQLModel):
    total_weights: int = 0


class WeekReportResponse(RootModel[dict[str, int]]):
    root: dict[str, int]


class YearReportResponse(RootModel[dict[str, int]]):
    root: dict[str, int]


# endregion
