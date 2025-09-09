import { ApiService } from './../../core/services/api.service';
import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { Dialog } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { Subject, takeUntil } from 'rxjs';
import { Routine } from '../../shared/models/models';
import { ExerciseSummaryPipe } from '../../shared/pipes/exercise-summary.pipe';

@Component({
  selector: 'app-routines',
  imports: [
    Dialog,
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

  visible: boolean = false;

  showDialog() {
    this.visible = true;
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
