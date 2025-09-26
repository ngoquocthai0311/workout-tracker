from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from decimal import Decimal


class BaseModel(SQLModel):
    pass


# TODO: Future feature to promote keep track of other friends
# Case when a PT or someone that keeps track of other workouts and let them share the workout
class User(BaseModel, table=True):
    """Represents a user of the workout tracking application.

    This is the core model for a user, linking them to all their
    created exercises, routines, sessions, and personal records.

    Attributes:
        id (Optional[int]): The unique identifier for the user.
        username (str): The user's unique username.
        created_at (float): Timestamp of when the user was created.
        updated_at (float): Timestamp of when the user was last updated.
    """

    __tablename__ = "users"

    # this is the way to let database to the id increment for us not sqlmodel
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(nullable=False)
    created_at: float = Field(nullable=False)
    updated_at: float = Field(nullable=False)

    # Relationship to exercises, routines, and sessions
    exercises: Optional[list["Exercise"]] = Relationship(back_populates="user")
    routines: Optional[list["Routine"]] = Relationship(back_populates="user")
    sessions: Optional[list["WorkoutSession"]] = Relationship(back_populates="user")
    personal_records: Optional[list["PersonalRecord"]] = Relationship(
        back_populates="user", cascade_delete=True
    )


class RoutineExercise(BaseModel, table=True):
    """A link table that connects a Routine to an Exercise.

    This model manages the many-to-many relationship between routines and exercises.
    It includes additional fields to specify the order of an exercise within a routine.

    Attributes:
        id (Optional[int]): The unique identifier for the link.
        order (int): The position of the exercise within the routine.
        created_at (float): Timestamp of when the link was created.
        updated_at (float): Timestamp of when the link was last updated.
        routine_id (int): Foreign key linking to the Routine model.
        exercise_id (int): Foreign key linking to the Exercise model.
    """

    __tablename__ = "routines_exercises"

    id: Optional[int] = Field(default=None, primary_key=True)
    order: int = Field(default=1, nullable=False)
    # NOTE: a field that holds exercise note for each routine exercise
    notes: Optional[str]
    created_at: float = Field(nullable=False)
    updated_at: float = Field(nullable=False)
    routine_id: int = Field(
        foreign_key="routines.id", ondelete="CASCADE", nullable=False
    )
    # Trigger
    exercise_id: int = Field(
        foreign_key="exercises.id", ondelete="CASCADE", nullable=False
    )

    # Relationships
    routine: "Routine" = Relationship(back_populates="exercise_links")
    exercise: "Exercise" = Relationship(back_populates="routine_links")
    routine_exercise_sets: Optional[list["RoutineExerciseSet"]] = Relationship(
        back_populates="routine_exercise", cascade_delete=True
    )


class RoutineExerciseSet(BaseModel, table=True):
    """Represents a predefined set for a routine exercise.

    This model defines the planned details for a specific set within a routine,
    including the target weight, reps, and set type.

    Attributes:
        id (Optional[int]): The unique identifier for the set.
        routine_exercise_id (int): Foreign key linking to the parent RoutineExercise.
        set_number (int): The sequential number of the set within the exercise.
        set_type (str): The type of set (e.g., 'normal', 'warmup', 'failure').
        targeted_weight (Optional[Decimal]): The planned weight for the set.
        targeted_reps (Optional[int]): The planned repetitions for the set.
    """

    __tablename__ = "routines_exercises_sets"

    id: Optional[int] = Field(default=None, primary_key=True)

    routine_exercise_id: int = Field(
        foreign_key="routines_exercises.id", ondelete="CASCADE", nullable=False
    )
    set_number: int = Field(default=1, nullable=False)
    set_type: str = Field(default="normal", nullable=False)
    targeted_weight: Optional[Decimal] = Field(default=0, decimal_places=2)
    targeted_reps: Optional[int] = Field(default=0)

    # Relationships
    routine_exercise: RoutineExercise = Relationship(
        back_populates="routine_exercise_sets"
    )


class SessionExercise(BaseModel, table=True):
    """A link table that connects a WorkoutSession to an Exercise.

    This model stores the actual historical data for a set performed during a workout.
    It tracks the weight, reps, and other details of a user's action.

    Attributes:
        id (Optional[int]): The unique identifier for the set.
        session_id (int): Foreign key linking to the parent WorkoutSession.
        exercise_id (Optional[int]): Foreign key linking to the Exercise model. Can be `NULL` if the original exercise is deleted.
        exercise_name (str): The name of the exercise at the time of the workout, preserved for historical display.
        order (Optional[int]): The position of the exercise within the session.
        set_type (Optional[str]): The type of set (e.g., 'normal', 'warmup').
        set_number (int): The sequential number of the set within the exercise.
        weight_lifted (Optional[Decimal]): The weight used for the set.
        reps_completed (Optional[int]): The number of repetitions completed for the set.
        created_at (float): Timestamp of when the set was performed.
    """

    __tablename__ = "sessions_exercises"

    id: Optional[int] = Field(default=None, primary_key=True)

    session_id: int = Field(foreign_key="sessions.id", ondelete="CASCADE")
    # NOTE: Allow null when an exercise is removed
    exercise_id: Optional[int] = Field(default=None, foreign_key="exercises.id")

    # NOTE: If an exercise is removed then we still have a name to display
    exercise_name: str = Field(nullable=False)
    # order of the exercises within a session
    order: Optional[int] = Field(default=1)
    # set number is used with exercise id when an exercise is added during a session
    set_type: Optional[str] = Field(default="normal")
    set_number: int = Field(default=1)
    weight_lifted: Optional[Decimal] = Field(default=0, decimal_places=2)
    reps_completed: Optional[int] = Field(default=0)
    created_at: float = Field(nullable=False)

    # Relationships
    session: "WorkoutSession" = Relationship(back_populates="exercise_links")
    exercise: Optional["Exercise"] = Relationship(back_populates="session_links")
    personal_record: Optional["PersonalRecord"] = Relationship(
        back_populates="session_exercise", cascade_delete=True
    )


class Exercise(BaseModel, table=True):
    """Represents a specific exercise that a user can perform.

    This model stores the core details of an exercise, which can be part of
    multiple routines and workout sessions.

    Attributes:
        id (Optional[int]): The unique identifier for the exercise.
        name (str): The unique name of the exercise (e.g., 'Bench Press').
        description (Optional[str]): A description of the exercise.
        created_at (float): Timestamp of when the exercise was created.
        updated_at (float): Timestamp of when the exercise was last updated.
        user_id (int): Foreign key linking to the user who owns the exercise.
    """

    __tablename__ = "exercises"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    description: Optional[str]
    created_at: float = Field(nullable=False)
    updated_at: float = Field(nullable=False)
    user_id: int = Field(default=None, foreign_key="users.id")

    # Relationships
    user: User = Relationship(back_populates="exercises")
    personal_record: Optional["PersonalRecord"] = Relationship(
        back_populates="exercise", cascade_delete=True
    )
    routine_links: Optional[list[RoutineExercise]] = Relationship(
        back_populates="exercise", cascade_delete=True
    )
    session_links: Optional[list[SessionExercise]] = Relationship(
        back_populates="exercise"
    )


class Routine(BaseModel, table=True):
    """Represents a structured plan of exercises.

    This model is a collection of exercises in a specific order,
    providing a template for a workout session.

    Attributes:
        id (Optional[int]): The unique identifier for the routine.
        name (str): The name of the routine.
        description (Optional[str]): A description of the routine.
        created_at (float): Timestamp of when the routine was created.
        updated_at (float): Timestamp of when the routine was last updated.
        user_id (int): Foreign key linking to the user who owns the routine.
    """

    __tablename__ = "routines"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str]
    created_at: float = Field(nullable=False)
    updated_at: float = Field(nullable=False)
    user_id: int = Field(default=None, foreign_key="users.id", nullable=False)

    # Relationships
    user: User = Relationship(back_populates="routines")
    exercise_links: Optional[list[RoutineExercise]] = Relationship(
        back_populates="routine", cascade_delete=True
    )
    sessions: Optional[list["WorkoutSession"]] = Relationship(back_populates="routine")


class WorkoutSession(BaseModel, table=True):
    """Represents a single instance of a completed or in-progress workout.

    This model serves as the top-level container for a workout, tracking its
    details, duration, and the exercises performed within it.

    Attributes:
        id (Optional[int]): The unique identifier for the workout session.
        name (Optional[str]): The name of the workout session.
        description (Optional[str]): A description of the workout.
        duration (Optional[int]): The duration of the workout in seconds.
        notes (Optional[str]): Any notes recorded during the workout.
        created_at (float): Timestamp of when the session was created.
        updated_at (float): Timestamp of when the session was last updated.
        user_id (int): Foreign key linking to the user who performed the workout.
        routine_id (Optional[int]): Foreign key linking to the routine used for this session, if any.
    """

    __tablename__ = "sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(nullable=False)
    description: Optional[str]
    duration: Optional[int] = Field(default=0)
    total_weights: Optional[int] = Field(default=0, nullable=False)
    created_at: float = Field(nullable=False)
    updated_at: float = Field(nullable=False)
    user_id: int = Field(default=None, foreign_key="users.id", nullable=False)
    routine_id: Optional[int] = Field(default=None, foreign_key="routines.id")

    # Relationships
    user: User = Relationship(back_populates="sessions")
    routine: Optional[Routine] = Relationship(back_populates="sessions")
    exercise_links: Optional[list[SessionExercise]] = Relationship(
        back_populates="session", cascade_delete=True
    )


class PersonalRecord(BaseModel, table=True):
    """Represents a user's personal lifting record for a specific exercise.

    This table tracks a user's top achievements, linking each record to the
    exact workout set where it was achieved. This provides a verifiable
    historical record of a personal best.

    Attributes:
        id (Optional[int]): The unique identifier for the personal record.
        weight (Decimal): The maximum weight lifted for this record.
        notes (Optional[str]): Any additional notes or context for the record.
        updated_at (float): Timestamp of when the record was achieved or last updated.
        user_id (int): Foreign key linking to the user who owns the record.
        exercise_id (int): Foreign key linking to the specific exercise performed.
        session_exercise_id (int): Foreign key linking to the exact workout set where the record was achieved.
        user (User): Relationship to the User model.
        exercise (Exercise): Relationship to the Exercise model.
        session_exercise (SessionExercise): Relationship to the SessionExercise model.
    """

    __tablename__ = "personal_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    weight: Decimal = Field(default=0, decimal_places=2)
    notes: Optional[str]
    updated_at: float = Field(nullable=False)

    user_id: int = Field(
        foreign_key="users.id",
        ondelete="CASCADE",
        nullable=False,
    )
    exercise_id: int = Field(
        foreign_key="exercises.id", ondelete="CASCADE", nullable=False, unique=True
    )
    session_exercise_id: int = Field(
        foreign_key="sessions_exercises.id",
        ondelete="CASCADE",
        nullable=False,
    )

    # Relationships
    user: User = Relationship(back_populates="personal_records")
    exercise: Exercise = Relationship(back_populates="personal_record")
    session_exercise: SessionExercise = Relationship(back_populates="personal_record")
