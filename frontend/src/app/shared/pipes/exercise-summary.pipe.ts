import { Pipe, PipeTransform } from '@angular/core';
import { RoutineExercise, SessionExercise } from '../models/models';

@Pipe({
  name: 'exerciseSummary',
})
export class ExerciseSummaryPipe implements PipeTransform {
  transform(
    exercises: SessionExercise[] | RoutineExercise[] | undefined,
  ): string {
    if (!exercises) {
      return '';
    }

    let total_exercises: number = 0;
    let total_sets: number = 0;
    exercises.forEach((exercise) => {
      total_exercises += 1;
      if (exercise.sets && exercise.sets.length > 0) {
        exercise.sets.forEach(() => {
          total_sets += 1;
        });
      }
    });
    if (!total_exercises && !total_sets) {
      return 'No exercises';
    }
    return `${total_exercises} exercise(s) ${total_sets} set(s)`;
  }
}
