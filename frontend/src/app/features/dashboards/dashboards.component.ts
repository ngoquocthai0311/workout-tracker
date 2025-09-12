import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { FormsModule } from '@angular/forms';
import { CommonModule, DATE_PIPE_DEFAULT_OPTIONS } from '@angular/common';
import { Router } from '@angular/router';
import { Session } from '../../shared/models/models';
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
  ],
  templateUrl: './dashboards.component.html',
  styleUrl: './dashboards.component.scss',
})
export class DashboardsComponent implements OnInit, OnDestroy {
  private router = inject(Router);
  private apiService = inject(ApiService);
  private destroy$ = new Subject<void>();

  public recentSessions: Session[] = [];
  products!: any[];

  selectedProduct!: any;

  metaKey: boolean = true;

  constructor() {}

  ngOnInit() {
    this.products = [
      {
        id: '1000',
        code: 'f230fh0g3',
        name: 'Bamboo Watch',
        description: 'Product Description',
        image: 'bamboo-watch.jpg',
        price: 65,
        category: 'Accessories',
        quantity: 24,
        inventoryStatus: 'INSTOCK',
        rating: 5,
      },
      {
        id: '1001',
        code: 'nvklal433',
        name: 'Black Watch',
        description: 'Product Description',
        image: 'black-watch.jpg',
        price: 72,
        category: 'Accessories',
        quantity: 61,
        inventoryStatus: 'OUTOFSTOCK',
        rating: 4,
      },
      {
        id: '1002',
        code: 'zz21cz3c1',
        name: 'Blue Band',
        description: 'Product Description',
        image: 'blue-band.jpg',
        price: 79,
        category: 'Fitness',
        quantity: 2,
        inventoryStatus: 'LOWSTOCK',
        rating: 3,
      },
      {
        id: '1003',
        code: '244wgerg2',
        name: 'Blue T-Shirt',
        description: 'Product Description',
        image: 'blue-t-shirt.jpg',
        price: 29,
        category: 'Clothing',
        quantity: 25,
        inventoryStatus: 'INSTOCK',
        rating: 5,
      },
      {
        id: '1004',
        code: 'h456wer53',
        name: 'Bracelet',
        description: 'Product Description',
        image: 'bracelet.jpg',
        price: 15,
        category: 'Accessories',
        quantity: 73,
        inventoryStatus: 'INSTOCK',
        rating: 4,
      },
    ];
    this.fetchRecentSessions();
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
