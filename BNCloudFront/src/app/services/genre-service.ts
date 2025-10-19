import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Artist} from '../components/artist/artist';
import {ArtistDTO} from '../models/artist';
import {map, Observable} from 'rxjs';
import {environment} from '../../env/enviroment';
import {CreateArtistRequest} from '../dto/create-artist-request';
import {FetchArtistsResponse} from '../dto/fetch-artists-response';
import {GenreResponse} from '../dto/genre-response';
import {GenreDiscoverResponse} from '../dto/genre-discover-response';


@Injectable({
  providedIn: 'root'
})
export class GenreService {

  constructor(private http: HttpClient) {}

  getAll(): Observable<any> {
    return this.http.get<any[]>(`${environment.apiHost}/genre`)
  }


  discover(name: string): Observable<GenreDiscoverResponse | undefined> {
    let params = new HttpParams();
    if (name) {
      params = params.set('name', name);
    }

    return this.http.get<GenreDiscoverResponse>(`${environment.apiHost}/genre/discover`, { params })
      .pipe(
        map(res => (res as any)[0])
      );
  }

}
