import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { EMPTY, Observable } from 'rxjs';
import { Exercise, Routine, Session } from '../../shared/models/models';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private http = inject(HttpClient);
  private routinesAPI = '/api/v1/routines';
  private sessionsAPI = '/api/v1/sessions';
  private exercisesAPI = '/api/v1/exercises';
  private usersAPI = '/api/v1/users';
  private dashboardsAPI = '/api/v1/dashboards';

  constructor() {}

  getRoutines(): Observable<object> {
    return this.http.get(this.routinesAPI);
  }

  createRoutine(newRoutine: Routine): Observable<object> {
    return this.http.post(this.routinesAPI, newRoutine);
  }

  getRoutineById(id: number): Observable<object> {
    if (!id) {
      return EMPTY;
    }

    return this.http.get(`${this.routinesAPI}/${id}`);
  }

  updateRoutineById(id: number, newData: Routine): Observable<object> {
    return this.http.patch(`${this.routinesAPI}/${id}`, newData);
  }

  removeRoutineById(id: number): Observable<object> {
    return this.http.delete(`${this.routinesAPI}/${id}`);
  }

  getSessions(): Observable<object> {
    return this.http.get(this.sessionsAPI);
  }

  createSession(newSession: Session): Observable<object> {
    return this.http.post(this.sessionsAPI, newSession);
  }

  getSessionById(id: number): Observable<object> {
    if (!id) {
      return EMPTY;
    }

    return this.http.get(`${this.sessionsAPI}/${id}`);
  }

  updateSessionById(id: number, newData: Session): Observable<object> {
    return this.http.patch(`${this.sessionsAPI}/${id}`, newData);
  }

  removeSessionById(id: number): Observable<object> {
    return this.http.delete(`${this.sessionsAPI}/${id}`);
  }

  getExercises(): Observable<object> {
    return this.http.get(this.exercisesAPI);
  }

  createExercise(newExercise: Exercise): Observable<object> {
    return this.http.post(this.exercisesAPI, newExercise);
  }

  getExerciseById(id: number): Observable<object> {
    if (!id) {
      return EMPTY;
    }

    return this.http.get(`${this.exercisesAPI}/${id}`);
  }

  updateExerciseById(id: number, newData: Exercise): Observable<object> {
    return this.http.patch(`${this.exercisesAPI}/${id}`, newData);
  }

  removeExerciseById(id: number): Observable<object> {
    return this.http.delete(`${this.exercisesAPI}/${id}`);
  }

  // TODO: Add dashboards and users here
}
