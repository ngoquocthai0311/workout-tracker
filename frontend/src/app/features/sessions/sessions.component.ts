import { Component, inject, OnDestroy, OnInit, Pipe } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ApiService } from '../../core/services/api.service';
import { Subject, takeUntil } from 'rxjs';
import { Session } from '../../shared/models/models';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { ExerciseSummaryPipe } from '../../shared/pipes/exercise-summary.pipe';

@Component({
  selector: 'app-sessions',
  imports: [ButtonModule, CardModule, ScrollPanelModule, ExerciseSummaryPipe],
  templateUrl: './sessions.component.html',
  styleUrl: './sessions.component.scss',
})
export class SessionsComponent implements OnInit, OnDestroy {
  private apiService = inject(ApiService);
  private destroy$ = new Subject<void>();

  public sessions: Session[] = [];

  ngOnInit(): void {
    this.fetchSession();
  }

  fetchSession() {
    this.apiService
      .getSessions()
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        this.sessions = data as Session[];
      });
  }

  removeSession(id?: number) {
    if (!id) {
      return;
    }
    this.apiService
      .removeSessionById(id)
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        console.log(data);
        this.fetchSession();
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
