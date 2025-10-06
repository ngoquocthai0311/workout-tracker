import { ToastService } from './toast.service';
import {
  HttpClient,
  HttpErrorResponse,
  HttpStatusCode,
} from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { catchError, EMPTY, Observable, of } from 'rxjs';
import { Exercise, Routine, Session } from '../../shared/models/models';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private http = inject(HttpClient);
  private toastService = inject(ToastService);
  private routinesAPI = '/api/v1/routines';
  private sessionsAPI = '/api/v1/sessions';
  private exercisesAPI = '/api/v1/exercises';
  private usersAPI = '/api/v1/users';
  private dashboardsAPI = '/api/v1/dashboards';

  constructor() {}

  getRoutines(): Observable<object> {
    return this.http.get(this.routinesAPI).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  createRoutine(newRoutine: Routine): Observable<object> {
    return this.http.post(this.routinesAPI, newRoutine).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  getRoutineById(id: number): Observable<object> {
    if (!id) {
      return EMPTY;
    }

    return this.http.get(`${this.routinesAPI}/${id}`).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  updateRoutineById(id: number, newData: Routine): Observable<object> {
    return this.http.patch(`${this.routinesAPI}/${id}`, newData).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  removeRoutineById(id: number): Observable<object> {
    return this.http.delete(`${this.routinesAPI}/${id}`).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  getSessions(): Observable<object> {
    return this.http.get(this.sessionsAPI).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  createSession(newSession: Session): Observable<object> {
    return this.http.post(this.sessionsAPI, newSession).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  getSessionById(id: number): Observable<object> {
    if (!id) {
      return EMPTY;
    }

    return this.http.get(`${this.sessionsAPI}/${id}`).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  updateSessionById(id: number, newData: Session): Observable<object> {
    return this.http.patch(`${this.sessionsAPI}/${id}`, newData).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  removeSessionById(id: number): Observable<object> {
    return this.http.delete(`${this.sessionsAPI}/${id}`).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  getExercises(): Observable<object> {
    return this.http.get(this.exercisesAPI).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  createExercise(newExercise: Exercise): Observable<object> {
    return this.http.post(this.exercisesAPI, newExercise).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  getExerciseById(id: number): Observable<object> {
    if (!id) {
      return EMPTY;
    }

    return this.http.get(`${this.exercisesAPI}/${id}`).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  updateExerciseById(id: number, newData: Exercise): Observable<object> {
    return this.http.patch(`${this.exercisesAPI}/${id}`, newData).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  removeExerciseById(id: number): Observable<object> {
    return this.http.delete(`${this.exercisesAPI}/${id}`).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  // TODO: Add dashboards and users here

  getAGlance(): Observable<object> {
    return this.http.get(`${this.dashboardsAPI}/glance`).pipe(
      catchError((error: HttpErrorResponse) => {
        this.catchError(error);
        return of({});
      }),
    );
  }

  // Private functions
  // error handlings
  private catchError(error: HttpErrorResponse) {
    const message: string = error.message;
    switch (error.status) {
      case HttpStatusCode.InternalServerError: {
        this.toastService.showError('Please contact developer');
        console.log(message);
        break;
      }
      case HttpStatusCode.UnprocessableEntity: {
        this.toastService.showWarn('Can not proceed the request');
        console.log(message);
        break;
      }
      case HttpStatusCode.NotFound: {
        console.log(message);
        break;
      }
      default: {
        console.log('Unhandled error, please check');
        console.log(message);
      }
    }
  }
}
