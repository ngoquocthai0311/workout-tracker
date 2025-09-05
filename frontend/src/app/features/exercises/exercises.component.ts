import { Component, inject } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { Dialog } from 'primeng/dialog';
import { ApiService } from '../../core/services/api.service';
import { Subject, takeUntil } from 'rxjs';

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
  ],
  templateUrl: './exercises.component.html',
  styleUrl: './exercises.component.scss',
})
export class ExercisesComponent {
  private apiService = inject(ApiService);
  private destroy$ = new Subject<void>();

  visible: boolean = false;

  ngOnInit(): void {
    this.apiService
      .getExercises()
      .pipe(takeUntil(this.destroy$))
      .subscribe((data) => {
        console.log(data);
      });
  }

  showDialog() {
    this.visible = true;
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
