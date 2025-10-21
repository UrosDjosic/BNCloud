import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../env/enviroment';


@Injectable({
  providedIn: 'root'
})
export class UserlistService {

  constructor(private http: HttpClient) {}

  getUsersUserlists(userId: string): Observable<object> {
    return this.http.get<object>(`${environment.apiHost}/userlist/user/${userId}`)
  }

  createUserlist(request: any): Observable<object> {
    return this.http.post<object>(`${environment.apiHost}/userlist`, request);
  }

  getUserlist(userlistId: string): Observable<object> {
    return this.http.get<object>(`${environment.apiHost}/userlist/${userlistId}`);
  }

  updateUserlist(userlistId: string, song: string): Observable<object> {
    return this.http.put<object>(`${environment.apiHost}/userlist/${userlistId}`, {
      song: song
    });
  }
}
