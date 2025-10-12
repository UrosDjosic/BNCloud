import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Artist} from '../components/artist/artist';
import {ArtistDTO} from '../models/artist';
import {Observable} from 'rxjs';
import {environment} from '../../env/enviroment';
import {CreateArtistRequest} from '../dto/create-artist-request';
import {FetchArtistsResponse} from '../dto/fetch-artists-response';


@Injectable({
  providedIn: 'root'
})
export class ArtistService {

  constructor(private http: HttpClient) {}

  create(artist: CreateArtistRequest): Observable<any> {
    return this.http.post<void>(`${environment.apiHost}/artist`, artist)
  }


  getArtists(lastKey:string, pageSize: number) : Observable<FetchArtistsResponse> {
    let params : HttpParams = new HttpParams();
    if (lastKey && pageSize) {
      params = params
        .set('lastKey', lastKey)
        .set('pageSize', pageSize)
    }
    return this.http.get<FetchArtistsResponse>(`${environment.apiHost}/artist`,{params: params})
  }

  updateArtist(artist : ArtistDTO): Observable<ArtistDTO> {
    return this.http.put<ArtistDTO>(`${environment.apiHost}/artist`, artist)
  }
}
