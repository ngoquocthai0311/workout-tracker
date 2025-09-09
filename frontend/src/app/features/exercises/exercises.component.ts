import { Component, inject } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';
import { FormGroup, FormsModule, Validators } from '@angular/forms';
import { Dialog } from 'primeng/dialog';
import { ApiService } from '../../core/services/api.service';
import { Subject, takeUntil } from 'rxjs';
import { Exercise } from '../../shared/models/models';
import { FormControl, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-exercises',
  imports: [
    Dialog,
    CardModule,
    ButtonModule,
    ScrollPanelModule,
    IconFieldModule,
    InputIconModule,
    InputTextModule,
    FormsModule,
    ReactiveFormsModule,
  ],
  templateUrl: './exercises.component.html',
  styleUrl: './exercises.component.scss',
})
export class ExercisesComponent {
  private apiService = inject(ApiService);
  private destroy$ = new Subject<void>();

  createExerciseFormGroup = new FormGroup({
    name: new FormControl('', [Validators.required]),
    description: new FormControl(''),
  });

  public exercises: Exercise[] = [];
  public filteredExercises: Exercise[] = [];

  visible: boolean = false;

  ngOnInit(): void {
    this.fetchExercises();
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

  fetchExercises() {
    this.apiService
      .getExercises()
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        this.exercises = data as Exercise[];
        this.filteredExercises = this.exercises;
        console.log(this.exercises);
      });
  }

  removeExercise(id: number | undefined) {
    if (!id) {
      // fetch again the exercises
      this.fetchExercises();
      return;
    }

    this.apiService
      .removeExerciseById(id)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        this.fetchExercises();
      });
  }

  showDialog() {
    this.visible = true;
  }

  closeDialog() {
    this.visible = false;
    this.createExerciseFormGroup.reset();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
