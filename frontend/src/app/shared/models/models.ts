export interface Exercise {
  id?: number;
  name?: string;
  description?: string;
  created_at?: Date;
  updated_at?: Date;
  personal_record?: MaxWeightRecord;
  user_id?: number;
}

export interface MaxWeightRecord {
  weight?: number;
  notes?: string;
  updated_at?: Date;
}

export interface ExerciseSet {
  id: number;
  set_type: string;
  targeted_weight: number;
  targeted_reps: number;
}

export interface RoutineExercise {
  id?: number;
  exercise_id?: number;
  name: string;
  description?: string;
  created_at: Date;
  updated_at: Date;
  max_weight?: number;
  sets?: ExerciseSet[];
}

export interface Routine {
  id?: number;
  name: string;
  description?: string | null;
  created_at?: Date;
  updated_at?: Date;
  user_id: number;
  exercises?: RoutineExercise[];
}

export interface Session {
  id: number;
  name?: string | null;
  description?: string | null;
  duration?: number;
  created_at: Date;
  updated_at?: Date | null;
  notes?: string | null;
  exercises?: SessionExercise[];
}

export interface SessionExercise {
  id: number;
  name?: string | null;
  description?: string | null;
  sets: SessionExerciseSet[];
}

export interface SessionExerciseSet {
  id?: number | null;
  set_type?: string | null;
  weight_lifted?: number | null;
  reps_completed: number | null;
}

export interface DashboardGlance {
  total_workouts: number;
  total_volumes: number;
  streaks: number;
  last_workout: string;
}
