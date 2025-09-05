import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { EMPTY, Observable } from 'rxjs';

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

  getRoutineById(id: number): Observable<object> {
    if (!id) {
      return EMPTY;
    }

    return this.http.get(`${this.routinesAPI}/${id}`);
  }

  getSessions(): Observable<object> {
    return this.http.get(this.sessionsAPI);
  }

  getSessionById(id: number): Observable<object> {
    if (!id) {
      return EMPTY;
    }

    return this.http.get(`${this.sessionsAPI}/${id}`);
  }

  getExercises(): Observable<object> {
    return this.http.get(this.exercisesAPI);
  }

  getExerciseById(id: number): Observable<object> {
    if (!id) {
      return EMPTY;
    }

    return this.http.get(`${this.exercisesAPI}/${id}`);
  }

  // TODO: Add dashboards and users here
}
