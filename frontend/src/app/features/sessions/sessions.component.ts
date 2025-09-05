import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ApiService } from '../../core/services/api.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-sessions',
  imports: [ButtonModule, CardModule],
  templateUrl: './sessions.component.html',
  styleUrl: './sessions.component.scss',
})
export class SessionsComponent implements OnInit, OnDestroy {
  private apiService = inject(ApiService);
  private destroy$ = new Subject<void>();

  ngOnInit(): void {
    this.apiService
      .getSessions()
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        console.log(data);
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
