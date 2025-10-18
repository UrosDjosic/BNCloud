import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Artist} from '../components/artist/artist';
import {ArtistDTO} from '../models/artist';
import {map, Observable} from 'rxjs';
import {environment} from '../../env/enviroment';
import {CreateArtistRequest} from '../dto/create-artist-request';
import {FetchArtistsResponse} from '../dto/fetch-artists-response';
import {GenreResponse} from '../dto/genre-response';


@Injectable({
  providedIn: 'root'
})
export class GenreService {

  constructor(private http: HttpClient) {}

  getAll(): Observable<any> {
    return this.http.get<any[]>(`${environment.apiHost}/genre`)
  }

}
