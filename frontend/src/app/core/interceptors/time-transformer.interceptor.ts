import { HttpEventType, HttpInterceptorFn } from '@angular/common/http';
import { tap } from 'rxjs';

export const timeTransformerInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    tap((event) => {
      if (event.type === HttpEventType.Response) {
        const body: unknown = event.body;
        if (body) {
          if (Array.isArray(body)) {
            for (const item of body) {
              transformDate(item);
            }
          } else {
            transformDate(body);
          }
        }
      }
    }),
  );
};

function transformDate(item: any): void {
  if (
    Object.prototype.hasOwnProperty.call(item, 'created_at') ||
    Object.prototype.hasOwnProperty.call(item, 'updated_at')
  ) {
    item.created_at = new Date(item.created_at * 1000);
    item.updated_at = new Date(item.updated_at * 1000);
  } else if (
    Object.prototype.hasOwnProperty.call(item, 'last_workout') &&
    item.last_workout
  ) {
    item.last_workout = new Date(item.last_workout * 1000);
  }

  // go inside nested object using dfs
  for (const prop of Object.keys(item)) {
    if (item[prop] instanceof Date) {
      continue;
    }
    if (Array.isArray(item[prop])) {
      for (const eachItem of item[prop]) {
        transformDate(eachItem);
      }
    } else if (item[prop] instanceof Object) {
      transformDate(item[prop]);
    }
  }
}
