import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { FormsModule } from '@angular/forms';
import { CommonModule, DatePipe } from '@angular/common';
import { Router } from '@angular/router';
import { DashboardGlance, Session } from '../../shared/models/models';
import { ApiService } from '../../core/services/api.service';
import { Subject, takeUntil } from 'rxjs';
import { ExerciseSummaryPipe } from '../../shared/pipes/exercise-summary.pipe';

@Component({
  selector: 'app-dashboards',
  imports: [
    ButtonModule,
    CardModule,
    TableModule,
    FormsModule,
    CommonModule,
    ExerciseSummaryPipe,
    DatePipe,
  ],
  templateUrl: './dashboards.component.html',
  styleUrl: './dashboards.component.scss',
})
export class DashboardsComponent implements OnInit, OnDestroy {
  private router = inject(Router);
  private apiService = inject(ApiService);
  private destroy$ = new Subject<void>();

  public recentSessions: Session[] = [];
  public glance: DashboardGlance = {} as DashboardGlance;
  products!: any[];

  selectedProduct!: any;

  metaKey: boolean = true;

  constructor() {}

  ngOnInit() {
    this.fetchRecentSessions();
    this.fetchGlance();
  }

  fetchGlance() {
    this.apiService
      .getAGlance()
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        this.glance = data as DashboardGlance;
        console.log(this.glance);
      });
  }

  fetchRecentSessions() {
    this.apiService
      .getSessions()
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        this.recentSessions = data as Session[];
        console.log(this.recentSessions);
      });
  }

  startNewWorkoutSession() {
    this.router.navigate(['sessions', 'log-session']);
  }

  navigateToRoutines() {
    this.router.navigate(['routines']);
  }

  navigateToSessions() {
    this.router.navigate(['sessions']);
  }

  navigateToExercises() {
    this.router.navigate(['exercises']);
  }

  navigateToReports() {
    this.router.navigate(['reports']);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
