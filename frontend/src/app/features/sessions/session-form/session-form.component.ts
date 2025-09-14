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
import { Subject, takeUntil } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { InputNumberModule } from 'primeng/inputnumber';
import { Dialog } from 'primeng/dialog';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { ToastService } from '../../../core/services/toast.service';

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
  ],
  templateUrl: './session-form.component.html',
  styleUrl: './session-form.component.scss',
})
export class SessionFormComponent implements OnInit, OnDestroy {
  private apiService = inject(ApiService);
  private toastService = inject(ToastService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private destroy$ = new Subject<void>();
  private routineId: number = 0;
  private routine: Routine = {} as Routine;

  public sessionId: number = 0;
  public exercises: Exercise[] = [];
  public filteredExercises: Exercise[] = [];
  public session: Session = {} as Session;
  public visible: boolean = false;
  public createExerciseFormGroup = new FormGroup({
    name: new FormControl('', [Validators.required]),
    description: new FormControl(''),
  });

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
            sets: routineExercise.sets as unknown as SessionExerciseSet[],
          } as SessionExercise);
        }, console.log(this.session));
      } else if (this.routine.id !== this.routineId) {
        // TODO: Add pop up to say the data is not valid
        this.router.navigate(['routines']);
      }
      // Assume log new session with empty routine
    } else {
      this.sessionId = this.route.snapshot.paramMap.get(
        'id',
      ) as unknown as number;
      // this.sessionId = this.router.url.split('/').pop() as unknown as number;
      // check for
      console.log(this.sessionId);
      this.fetchSession();
    }
    console.log(this.routine);
    this.fetchExercises();
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
    this.apiService
      .createSession(this.session)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        // redirect to routines
        console.log(data);
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
    console.log(exerciseId, setIndex);
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
    console.log(this.session);
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
        this.toastService.showSuccess('fetch successfully');
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

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
