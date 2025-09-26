import { ApiService } from './../../core/services/api.service';
import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { InputTextModule } from 'primeng/inputtext';
import { Subject, takeUntil } from 'rxjs';
import { Routine } from '../../shared/models/models';
import { ExerciseSummaryPipe } from '../../shared/pipes/exercise-summary.pipe';
import { Router } from '@angular/router';

@Component({
  selector: 'app-routines',
  imports: [
    ButtonModule,
    CardModule,
    ScrollPanelModule,
    InputTextModule,
    ExerciseSummaryPipe,
  ],
  templateUrl: './routines.component.html',
  styleUrl: './routines.component.scss',
})
export class RoutinesComponent implements OnInit, OnDestroy {
  private apiService = inject(ApiService);
  private destroy$ = new Subject<void>();
  private router = inject(Router);

  public routines: Routine[] = [];

  ngOnInit(): void {
    this.getRoutines();
  }

  public getRoutines() {
    this.apiService
      .getRoutines()
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        this.routines = data as Routine[];
      });
  }

  public removeRoutine(id: number | undefined) {
    if (!id) {
      return;
    }

    this.apiService
      .removeRoutineById(id)
      .pipe(takeUntil(this.destroy$))
      .subscribe((_) => {
        this.getRoutines();
      });
  }

  getRoutineDetail(id?: number) {
    if (!id) {
      return;
    }

    this.router.navigate(['routine', id]);
  }

  createNewRoutine() {
    this.router.navigate(['routines', 'create-routine']);
  }

  startRoutine(routine: Routine) {
    this.router.navigate(['sessions', 'log-session'], {
      queryParams: { routine: routine.id },
      state: { routine: routine },
    });
  }

  startNewWorkoutSession() {
    this.router.navigate(['sessions', 'log-session']);
  }

  visible: boolean = false;

  showDialog() {
    this.visible = true;
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
