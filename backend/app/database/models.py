from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from decimal import Decimal


class BaseModel(SQLModel):
    pass


class User(BaseModel, table=True):
    __tablename__ = "users"

    # this is the way to let database to the id increment for us not sqlmodel
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    created_at: float
    updated_at: float

    # Relationship to exercises, routines, and sessions
    exercises: Optional[list["Exercise"]] = Relationship(back_populates="user")
    routines: Optional[list["Routine"]] = Relationship(back_populates="user")
    sessions: Optional[list["WorkoutSession"]] = Relationship(back_populates="user")
    max_weights: Optional[list["MaxWeightRecord"]] = Relationship(
        back_populates="user", cascade_delete=True
    )


class RoutineExercise(BaseModel, table=True):
    __tablename__ = "routines_exercises"

    id: Optional[int] = Field(default=None, primary_key=True)
    routine_id: Optional[int] = Field(
        default=None, foreign_key="routines.id", ondelete="CASCADE", nullable=False
    )
    exercise_id: Optional[int] = Field(
        default=None, foreign_key="exercises.id", nullable=False
    )
    order: int = Field(default=1)
    created_at: float
    updated_at: float

    # Relationships
    routine: "Routine" = Relationship(back_populates="exercise_links")
    exercise: "Exercise" = Relationship(back_populates="routine_links")
    routine_exercise_sets: list["RoutineExerciseSet"] = Relationship(
        back_populates="routine_exercise", cascade_delete=True
    )


class RoutineExerciseSet(BaseModel, table=True):
    __tablename__ = "routines_exercises_sets"

    id: Optional[int] = Field(default=None, primary_key=True)

    routine_exercise_id: Optional[int] = Field(
        default=None, foreign_key="routines_exercises.id", ondelete="CASCADE"
    )
    set_number: int = Field(default=1)
    set_type: str = Field(default="normal")
    targeted_weight: Optional[Decimal] = Field(default=0, decimal_places=2)
    targeted_reps: Optional[int] = Field(default=0)

    # Relationships
    routine_exercise: RoutineExercise = Relationship(
        back_populates="routine_exercise_sets"
    )


class SessionExercise(BaseModel, table=True):
    __tablename__ = "sessions_exercises"

    id: Optional[int] = Field(default=None, primary_key=True)

    session_id: int = Field(foreign_key="sessions.id", ondelete="CASCADE")
    exercise_id: Optional[int] = Field(default=None, foreign_key="exercises.id")

    # order of the exercises within a session
    order: Optional[int] = Field(default=1)
    # set number is used with exercise id when an exercise is added during a session
    set_type: Optional[str] = Field(default="normal")
    set_number: int = Field(default=1)
    weight_lifted: Optional[Decimal] = Field(default=0, decimal_places=2)
    reps_completed: Optional[int] = Field(default=0)
    created_at: float

    # Relationships
    session: "WorkoutSession" = Relationship(back_populates="exercise_links")
    exercise: "Exercise" = Relationship(back_populates="session_links")
    max_weight: "MaxWeightRecord" = Relationship(back_populates="session_exercise")


class Exercise(BaseModel, table=True):
    __tablename__ = "exercises"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str]
    created_at: float
    updated_at: float
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")

    # Relationships
    user: User = Relationship(back_populates="exercises")
    max_weight: "MaxWeightRecord" = Relationship(
        back_populates="exercise", cascade_delete=True
    )
    routine_links: list[RoutineExercise] = Relationship(back_populates="exercise")
    session_links: list[SessionExercise] = Relationship(back_populates="exercise")


class Routine(BaseModel, table=True):
    __tablename__ = "routines"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str]
    created_at: float
    updated_at: float
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")

    # Relationships
    user: User = Relationship(back_populates="routines")
    exercise_links: list[RoutineExercise] = Relationship(
        back_populates="routine", cascade_delete=True
    )
    sessions: list["WorkoutSession"] = Relationship(back_populates="routine")


class WorkoutSession(BaseModel, table=True):
    __tablename__ = "sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    description: Optional[str]
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    routine_id: Optional[int] = Field(default=None, foreign_key="routines.id")
    created_at: float
    duration: Optional[int] = Field(default=0)
    updated_at: Optional[float] = Field(default=None)
    notes: Optional[str]

    # Relationships
    user: User = Relationship(back_populates="sessions")
    routine: Routine = Relationship(back_populates="sessions")
    exercise_links: list[SessionExercise] = Relationship(
        back_populates="session", cascade_delete=True
    )


class MaxWeightRecord(BaseModel, table=True):
    __tablename__ = "max_weights"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(
        default=None, foreign_key="users.id", ondelete="CASCADE"
    )
    exercise_id: Optional[int] = Field(
        default=None, foreign_key="exercises.id", ondelete="CASCADE"
    )
    session_exercise_id: Optional[int] = Field(
        default=None, foreign_key="sessions_exercises.id", ondelete="CASCADE"
    )
    weight: Optional[Decimal] = Field(default=0, decimal_places=2)
    notes: Optional[str]
    updated_at: Optional[float] = Field(default=None)

    # Relationships
    user: User = Relationship(back_populates="max_weights")
    exercise: Exercise = Relationship(back_populates="max_weight")
    session_exercise: SessionExercise = Relationship(back_populates="max_weight")
