import { ExerciseSet } from './../../../shared/models/models';
import { ApiService } from './../../../core/services/api.service';
import { TableModule } from 'primeng/table';
import { FormsModule } from '@angular/forms';
import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { DividerModule } from 'primeng/divider';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { Subject, takeUntil } from 'rxjs';
import { RoutineExercise, Routine } from '../../../shared/models/models';
import { Router } from '@angular/router';

@Component({
  selector: 'app-routine-form',
  imports: [
    InputIconModule,
    IconFieldModule,
    DividerModule,
    FormsModule,
    TableModule,
    CardModule,
    ButtonModule,
    InputTextModule,
  ],
  templateUrl: './routine-form.component.html',
  styleUrl: './routine-form.component.scss',
})
export class RoutineFormComponent implements OnInit, OnDestroy {
  private apiService = inject(ApiService);
  private router = inject(Router);
  private destroy$ = new Subject<void>();
  private routineId: number = 0;
  public exercises: RoutineExercise[] = [];

  public routine: Routine = {} as Routine;

  products!: any[];
  selectedProduct!: any;

  metaKey: boolean = true;

  constructor() {}

  ngOnInit() {
    this.routineId = this.router.url.split('/').pop() as unknown as number;
    this.fetchRoutine();
    this.fetchExercises();
  }

  updateRoutine() {
    this.apiService
      .updateRoutineById(this.routineId, this.routine)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        this.fetchRoutine();
      });
  }

  fetchExercises() {
    this.apiService
      .getExercises()
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        this.exercises = data as RoutineExercise[];
      });
  }

  fetchRoutine() {
    if (!this.routineId) {
      // TODO: add error here or redirect
      return;
    }
    this.apiService
      .getRoutineById(this.routineId)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        this.routine = data as Routine;
        console.log(this.routine);
      });
  }

  removeSet(setIndex: number, exerciseId?: number) {
    console.log(exerciseId, setIndex);
    if (!exerciseId) {
      this.fetchRoutine();
      return;
    }

    for (const index in this.routine.exercises) {
      const exercise: RoutineExercise =
        this.routine.exercises[index as unknown as number];
      if (exercise.id === exerciseId && exercise.sets) {
        exercise.sets.splice(setIndex, 1);
        return;
      }
    }
  }

  addSet(exerciseNumber: number) {
    if (this.routine.exercises) {
      const exercise: RoutineExercise = this.routine.exercises[exerciseNumber];
      if (!exercise.sets) {
        exercise.sets = [];
      }

      exercise.sets.push({
        set_type: 'normal',
        targeted_weight: 0,
        targeted_reps: 0,
      } as ExerciseSet);
    }
  }

  addExercise(exerciseId?: number) {
    if (!exerciseId) {
      this.fetchRoutine();
      return;
    }

    const exercise: RoutineExercise | undefined = this.exercises.find(
      (exercise) => exercise.id === exerciseId,
    );

    if (exercise) {
      this.routine.exercises?.push(exercise);
    }
  }

  removeExercise(exerciseNumber: number) {
    if (this.routine.exercises) {
      this.routine.exercises.splice(exerciseNumber, 1);
    }
  }

  public createRoutine() {
    const newRoutine: Routine = {
      name: 'testing again 123',
      description: 'something',
      user_id: 1,
    };
    this.apiService
      .createRoutine(newRoutine)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        console.log(data);
      });
  }

  public removeRoutine() {
    this.apiService
      .removeRoutineById(24)
      .pipe(takeUntil(this.destroy$))
      .subscribe((message) => {
        console.log(message);
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
