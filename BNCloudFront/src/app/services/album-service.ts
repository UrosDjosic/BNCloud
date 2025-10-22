import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../env/enviroment';
import {AlbumDTO} from '../models/album';


@Injectable({
  providedIn: 'root'
})
export class AlbumService {

  constructor(private http: HttpClient) {}

  uploadAlbum(album: any): Observable<string> {
    return this.http.post<string>(`${environment.apiHost}/album`, album);
  }

  getAlbum(albumId: string): Observable<AlbumDTO> {
    return this.http.get<AlbumDTO>(`${environment.apiHost}/album/${albumId}`);
  }

  updateAlbum(albumId: string, data: { name: string }): Observable<any> {
    return this.http.put(`${environment.apiHost}/album/${albumId}`, data);
  }

  deleteAlbum(albumId: string): Observable<void> {
    return this.http.delete<void>(`${environment.apiHost}/album/${albumId}`);
  }
}
