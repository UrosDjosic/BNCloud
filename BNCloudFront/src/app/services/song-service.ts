import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../env/enviroment';
import {DynamoSongResponse} from '../dto/dynamo-song-response';


@Injectable({
  providedIn: 'root'
})
export class SongService {

  constructor(private http: HttpClient) {}

  uploadSongMetadata(song: any): Observable<DynamoSongResponse> {
    return this.http.post<DynamoSongResponse>(`${environment.apiHost}/song`, song);
  }

  getSong(songId: string): Observable<object> {
    return this.http.get<object>(`${environment.apiHost}/song/${songId}`);
  }
}
