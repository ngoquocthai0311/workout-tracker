import { ApiService } from './../../core/services/api.service';
import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { Dialog } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-routines',
  imports: [
    Dialog,
    ButtonModule,
    CardModule,
    ScrollPanelModule,
    InputTextModule,
  ],
  templateUrl: './routines.component.html',
  styleUrl: './routines.component.scss',
})
export class RoutinesComponent implements OnInit, OnDestroy {
  private apiService = inject(ApiService);
  private destroy$ = new Subject<void>();

  ngOnInit(): void {
    this.apiService
      .getRoutines()
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        console.log(data);
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
