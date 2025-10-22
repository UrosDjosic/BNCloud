import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {map, Observable} from 'rxjs';
import {environment} from '../../env/enviroment';
import {DynamoSongResponse} from '../dto/dynamo-song-response';
import {UserFeedResponse} from '../dto/user-feed-response';


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

  updateSong(songId: string, updatedSong: any): Observable<DynamoSongResponse> {
    return this.http.put<DynamoSongResponse>(`${environment.apiHost}/song/${songId}`, updatedSong);
  }

  audioUpdate(newAudio: any): Observable<object> {
    return this.http.put<object>(`${environment.apiHost}/song/audio`, newAudio);
  }

  imageUpdate(newImage: any): Observable<object> {
    return this.http.put<object>(`${environment.apiHost}/song/image`, newImage)
  }

  rateSong(rating: any): Observable<object> {
    return this.http.put<object>(`${environment.apiHost}/song/rate`, rating);
  }

  searchSong(name: string): Observable<object> {
    return this.http.get<object>(`${environment.apiHost}/song/search/${name}`);
  }

  deleteSong(songId: string): Observable<void> {
    return this.http.delete<void>(`${environment.apiHost}/song/${songId}`);
  }

  initFeed(userId: string): Observable<UserFeedResponse> {
    return this.http
      .get<UserFeedResponse[]>(`${environment.apiHost}/feed/${userId}`)
      .pipe(
        map(res => res[0]) // ✅ take only the first object from the array
      );
  }
}
