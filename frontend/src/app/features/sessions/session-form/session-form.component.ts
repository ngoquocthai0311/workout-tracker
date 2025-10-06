import {
  Exercise,
  Routine,
  RoutineExercise,
  Session,
  SessionExercise,
  SessionExerciseSet,
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
import { interval, Subject, Subscription, takeUntil } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { InputNumberModule } from 'primeng/inputnumber';
import { Dialog } from 'primeng/dialog';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { DatePipe, NgTemplateOutlet } from '@angular/common';
import {
  CdkDrag,
  CdkDragDrop,
  CdkDropList,
  moveItemInArray,
} from '@angular/cdk/drag-drop';
import { DrawerModule } from 'primeng/drawer';

@Component({
  selector: 'app-session-form',
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
    DatePipe,
    CdkDrag,
    CdkDropList,
    DrawerModule,
    NgTemplateOutlet,
  ],
  templateUrl: './session-form.component.html',
  styleUrl: './session-form.component.scss',
})
export class SessionFormComponent implements OnInit, OnDestroy {
  private apiService = inject(ApiService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private destroy$ = new Subject<void>();
  private timer: Subscription | null = null;
  private routineId: number = 0;
  private routine: Routine = {} as Routine;

  public sessionId: number = 0;
  public exercises: Exercise[] = [];
  public filteredExercises: Exercise[] = [];
  public session: Session = {} as Session;
  public exerciseDialogVisible: boolean = false;
  public exercisesVisible: boolean = false;
  public createExerciseFormGroup = new FormGroup({
    name: new FormControl('', [Validators.required]),
    description: new FormControl(''),
  });
  public counter: number = 0;

  metaKey: boolean = true;

  constructor() {}

  ngOnInit() {
    const state = this.router.lastSuccessfulNavigation?.extras.state;

    if (state && state['routine']) {
      this.routine = state['routine'] as Routine;
    }

    if (this.router.url.split('/').pop()?.includes('log-session')) {
      this.routineId = this.route.snapshot.queryParams[
        'routine'
      ] as unknown as number;

      // log session with routine
      if (this.routine && this.routineId && this.routine.id == this.routineId) {
        // map each routine exercise to session exercise
        this.session.exercises = [];
        this.session.name = this.routine.name;
        this.session.description = this.routine.description;
        this.routine.exercises?.forEach((routineExercise: RoutineExercise) => {
          this.session.exercises?.push({
            id: routineExercise.exercise_id,
            name: routineExercise.name,
            // TODO: Investigate why I put it
            // description: routineExercise.notes,
            sets: routineExercise.sets as unknown as SessionExerciseSet[],
          } as SessionExercise);
        });
      } else if (this.routine.id !== this.routineId) {
        // TODO: Add pop up to say the data is not valid
        this.router.navigate(['routines']);
      }
      // Assume log new session with empty routine
    } else {
      this.sessionId = this.route.snapshot.paramMap.get(
        'id',
      ) as unknown as number;
      this.fetchSession();
    }
    this.fetchExercises();

    // trigger time counting for logging session
    if (!this.sessionId) {
      this.triggerCounting();
    }
  }

  dropExercise(event: CdkDragDrop<SessionExercise[]>) {
    moveItemInArray(
      this.session.exercises || [],
      event.previousIndex,
      event.currentIndex,
    );
  }

  dropSet(
    event: CdkDragDrop<SessionExerciseSet[]>,
    exerciseSets: SessionExerciseSet[] = [],
  ) {
    moveItemInArray(
      exerciseSets || [],
      event.previousIndex,
      event.currentIndex,
    );
  }

  triggerCounting() {
    this.timer = interval(1000)
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        // milliseconds
        if (this.session.duration) {
          this.session.duration += 1000;
        } else {
          this.session.duration = 1000;
        }

        this.counter = this.session.duration;
      });
  }

  resumeOrPauseCounting() {
    if (this.timer) {
      this.timer.unsubscribe();
      this.timer = null;
    } else {
      this.triggerCounting();
    }
  }

  updateSession() {
    this.apiService
      .updateSessionById(this.sessionId, this.session)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        this.session = data as Session;
      });
  }

  saveSession() {
    // pause timer
    this.timer?.unsubscribe();

    if (this.routineId) {
      this.session.routine_id = this.routineId;
    }

    this.apiService
      .createSession(this.session)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        // redirect to routines
        this.router.navigate(['/sessions']);
      });
  }

  fetchSession() {
    if (!this.sessionId) {
      // TODO: add error here or redirect
      return;
    }
    this.apiService
      .getSessionById(this.sessionId)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        this.session = data as Session;
        console.log(this.session);
      });
  }

  removeSet(setIndex: number, exerciseId?: number) {
    if (!exerciseId) {
      this.fetchSession();
      return;
    }
    for (const index in this.session.exercises) {
      const exercise: SessionExercise =
        this.session.exercises[index as unknown as number];
      if (exercise.id === exerciseId && exercise.sets) {
        exercise.sets.splice(setIndex, 1);
        return;
      }
    }
  }

  addSet(exerciseNumber: number) {
    if (this.session.exercises) {
      const exercise: SessionExercise = this.session.exercises[exerciseNumber];
      if (!exercise.sets) {
        exercise.sets = [];
      }
      exercise.sets.push({
        set_type: 'normal',
        weight_lifted: 0,
        reps_completed: 0,
      } as SessionExerciseSet);
    }
  }

  addExercise(exerciseId?: number) {
    if (!exerciseId) {
      this.fetchSession();
      return;
    }

    const exercise: Exercise | undefined = this.exercises.find(
      (exercise) => exercise.id === exerciseId,
    );

    if (exercise) {
      if (!this.session.exercises) {
        this.session.exercises = [] as SessionExercise[];
      }
      this.session.exercises?.push({
        ...exercise,
        id: exercise.id,
      } as SessionExercise);
    }
  }

  removeExercise(exerciseNumber: number) {
    if (this.session.exercises) {
      this.session.exercises.splice(exerciseNumber, 1);
    }
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

        if (data) {
          if (!this.session.exercises) {
            this.session.exercises = [] as SessionExercise[];
          }
          this.session.exercises?.push({
            ...data,
            id: data.id,
          } as SessionExercise);
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

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
