import { Routes } from '@angular/router';
import { DashboardsComponent } from './features/dashboards/dashboards.component';

export const routes: Routes = [
  {
    path: '',
    component: DashboardsComponent,
    title: 'Dashboard',
  },
  {
    path: 'exercises',
    loadComponent: () =>
      import('./features/exercises/exercises.component').then(
        (m) => m.ExercisesComponent,
      ),
    title: 'Exercise',
  },
  {
    path: 'routine/:id',
    loadComponent: () =>
      import('./features/routines/routine-form/routine-form.component').then(
        (m) => m.RoutineFormComponent,
      ),
  },
  {
    path: 'routines/create-routine',
    loadComponent: () =>
      import('./features/routines/routine-form/routine-form.component').then(
        (m) => m.RoutineFormComponent,
      ),
  },
  {
    path: 'routines',
    loadComponent: () =>
      import('./features/routines/routines.component').then(
        (m) => m.RoutinesComponent,
      ),
    title: 'routines',
  },
  {
    path: 'sessions/log-session',
    loadComponent: () =>
      import('./features/sessions/session-form/session-form.component').then(
        (m) => m.SessionFormComponent,
      ),
  },
  {
    path: 'session/:id',
    loadComponent: () =>
      import('./features/sessions/session-form/session-form.component').then(
        (m) => m.SessionFormComponent,
      ),
    title: 'sessions',
  },
  {
    path: 'sessions',
    loadComponent: () =>
      import('./features/sessions/sessions.component').then(
        (m) => m.SessionsComponent,
      ),
    title: 'sessions',
  },
  {
    path: 'reports',
    loadComponent: () =>
      import('./features/reports/reports.component').then(
        (m) => m.ReportsComponent,
      ),
    title: 'reports',
  },
];
