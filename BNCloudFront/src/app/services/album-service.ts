import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../env/enviroment';


@Injectable({
  providedIn: 'root'
})
export class AlbumService {

  constructor(private http: HttpClient) {}

  uploadAlbum(album: any): Observable<string> {
    return this.http.post<string>(`${environment.apiHost}/album`, album);
  }
}
