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
import {
  CdkDrag,
  CdkDragDrop,
  CdkDropList,
  moveItemInArray,
} from '@angular/cdk/drag-drop';
import { DrawerModule } from 'primeng/drawer';
import { NgTemplateOutlet } from '@angular/common';
import { ToastService } from '../../../core/services/toast.service';

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
    CdkDrag,
    CdkDropList,
    DrawerModule,
    NgTemplateOutlet,
  ],
  templateUrl: './routine-form.component.html',
  styleUrl: './routine-form.component.scss',
})
export class RoutineFormComponent implements OnInit, OnDestroy {
  private apiService = inject(ApiService);
  private router = inject(Router);
  private toastService = inject(ToastService);
  private destroy$ = new Subject<void>();
  private routineId: number = 0;

  public exercises: Exercise[] = [];
  public filteredExercises: Exercise[] = [];
  public routine: Routine = {} as Routine;
  public exerciseDialogVisible: boolean = false;
  public exercisesVisible: boolean = false;

  public createExerciseFormGroup = new FormGroup({
    name: new FormControl('', [Validators.required]),
    description: new FormControl(''),
  });

  public routineFormGroup = new FormGroup({
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
      this.initRoutineFormGroup();
    } else {
      this.routineId = this.router.url.split('/').pop() as unknown as number;
      this.fetchRoutine();
    }
    this.fetchExercises();
  }

  dropExercise(event: CdkDragDrop<RoutineExercise[]>) {
    moveItemInArray(
      this.routine.exercises || [],
      event.previousIndex,
      event.currentIndex,
    );
  }

  dropSet(event: CdkDragDrop<ExerciseSet[]>, exerciseSets: ExerciseSet[] = []) {
    moveItemInArray(
      exerciseSets || [],
      event.previousIndex,
      event.currentIndex,
    );
  }

  updateRoutine() {
    this.apiService
      .updateRoutineById(this.routineId, this.routine)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        if (Object.keys(data).length > 0) {
          this.routine = data as Routine;
          this.toastService.showSuccess('Update routine successfully');
        } else {
          this.toastService.showError('Please check your input');
        }
      });
  }

  createRoutine() {
    this.apiService
      .createRoutine(this.routine)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        // redirect to routines
        if (Object.keys(data).length > 0) {
          this.router.navigate(['/routines']);
          this.toastService.showSuccess('Create routine successfully');
        } else {
          this.toastService.showError('Please check your input');
        }
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
    this.exerciseDialogVisible = true;
    this.exercisesVisible = false;
  }

  closeDialog() {
    this.exerciseDialogVisible = false;
    this.createExerciseFormGroup.reset();
  }

  onCreateExercise() {
    const newExercise: Exercise = this.createExerciseFormGroup
      .value as Exercise;

    this.apiService
      .createExercise(newExercise)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data: Exercise) => {
        this.exerciseDialogVisible = false;
        this.createExerciseFormGroup.reset();
        this.fetchExercises();

        // append newly created exercise to session
        if (data) {
          if (!this.routine.exercises) {
            this.routine.exercises = [] as RoutineExercise[];
          }
          this.routine.exercises?.push({
            ...data,
            exercise_id: data.id,
            id: null as unknown,
          } as RoutineExercise);
        }

        // trigger toast
        if (Object.keys(data).length > 0) {
          this.toastService.showError('Can not create exercise');
        } else {
          this.toastService.showSuccess('Create exercise successfully');
        }
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
      this.toastService.showError('Invalid state');
      this.router.navigate(['/routines']);
      return;
    }
    this.apiService
      .getRoutineById(this.routineId)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        if (Object.keys(data).length == 0) {
          this.toastService.showError('Can not get routine data');
          this.router.navigate(['/routines']);
          return;
        }

        this.routine = data as Routine;

        // populate data for form control;
        this.initRoutineFormGroup();
      });
  }

  removeSet(setIndex: number, exerciseId?: number) {
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
  }

  removeExercise(exerciseNumber: number) {
    if (this.routine.exercises) {
      this.routine.exercises.splice(exerciseNumber, 1);
    }
  }

  private initRoutineFormGroup() {
    this.routineFormGroup.setValue({
      name: this.routine.name || '',
      description: this.routine.description || '',
    });

    this.routineFormGroup.controls['name'].valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe((value) => {
        console.log(value);
        this.routine.name = value || '';
      });

    this.routineFormGroup.controls['description'].valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe((value) => {
        console.log(value);
        this.routine.description = value || '';
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
