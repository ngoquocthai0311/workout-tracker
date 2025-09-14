import {
  Exercise,
  ExerciseSet,
  Routine,
  RoutineExercise,
} from './../../../shared/models/models';
import { ApiService } from './../../../core/services/api.service';
import { TableModule } from 'primeng/table';
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { DividerModule } from 'primeng/divider';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { Subject, takeUntil } from 'rxjs';
import { Router } from '@angular/router';
import { InputNumberModule } from 'primeng/inputnumber';
import { Dialog } from 'primeng/dialog';
import { ScrollPanelModule } from 'primeng/scrollpanel';

@Component({
  selector: 'app-routine-form',
  imports: [
    Dialog,
    InputIconModule,
    IconFieldModule,
    DividerModule,
    FormsModule,
    TableModule,
    CardModule,
    ButtonModule,
    InputTextModule,
    InputNumberModule,
    ReactiveFormsModule,
    ScrollPanelModule,
  ],
  templateUrl: './routine-form.component.html',
  styleUrl: './routine-form.component.scss',
})
export class RoutineFormComponent implements OnInit, OnDestroy {
  private apiService = inject(ApiService);
  private router = inject(Router);
  private destroy$ = new Subject<void>();
  private routineId: number = 0;

  public exercises: Exercise[] = [];
  public filteredExercises: Exercise[] = [];
  public routine: Routine = {} as Routine;
  public visible: boolean = false;

  public createExerciseFormGroup = new FormGroup({
    name: new FormControl('', [Validators.required]),
    description: new FormControl(''),
  });

  products!: any[];
  selectedProduct!: any;

  metaKey: boolean = true;

  constructor() {}

  ngOnInit() {
    if (this.router.url.split('/').pop() == 'create-routine') {
      this.routine = {} as Routine;
    } else {
      this.routineId = this.router.url.split('/').pop() as unknown as number;
      this.fetchRoutine();
    }
    this.fetchExercises();
  }

  updateRoutine() {
    // console.log(this.routine);
    this.apiService
      .updateRoutineById(this.routineId, this.routine)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        this.routine = data as Routine;
      });
  }

  createRoutine() {
    this.apiService
      .createRoutine(this.routine)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        // redirect to routines
        console.log(data);
        this.router.navigate(['/routines']);
      });
  }

  fetchExercises() {
    this.apiService
      .getExercises()
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        this.exercises = data as Exercise[];
        this.filteredExercises = this.exercises;
      });
  }

  createExercise() {
    this.visible = true;
  }

  closeDialog() {
    this.visible = false;
    this.createExerciseFormGroup.reset();
  }

  onCreateExercise() {
    const newExercise: Exercise = this.createExerciseFormGroup
      .value as Exercise;

    // TODO: add interceptor in the future to bind user_id here if save in cookies
    // or let the backend get it from the cookie
    newExercise.user_id = 1;
    this.apiService
      .createExercise(newExercise)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        console.log(data);
        this.visible = false;
        this.createExerciseFormGroup.reset();
        this.fetchExercises();
      });
  }

  searchExercise(event: any): void {
    const value = event.target.value;

    if (value) {
      this.filteredExercises = this.exercises.filter((exercise) =>
        exercise.name?.includes(value),
      );
    } else {
      this.filteredExercises = this.exercises;
    }
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

    console.log(this.routine);
  }

  addExercise(exerciseId?: number) {
    if (!exerciseId) {
      this.fetchRoutine();
      return;
    }

    const exercise: Exercise | undefined = this.exercises.find(
      (exercise) => exercise.id === exerciseId,
    );

    if (exercise) {
      if (!this.routine.exercises) {
        this.routine.exercises = [] as RoutineExercise[];
      }
      this.routine.exercises?.push({
        ...exercise,
        exercise_id: exercise.id,
        id: null as unknown,
      } as RoutineExercise);
    }

    console.log(this.routine);
  }

  removeExercise(exerciseNumber: number) {
    if (this.routine.exercises) {
      this.routine.exercises.splice(exerciseNumber, 1);
    }
  }

  public removeRoutine() {
    this.apiService
      .removeRoutineById(this.routineId)
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
