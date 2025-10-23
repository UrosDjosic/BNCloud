import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Artist} from '../components/artist/artist';
import {ArtistDTO} from '../models/artist';
import {map, Observable} from 'rxjs';
import {environment} from '../../env/enviroment';
import {CreateArtistRequest} from '../dto/create-artist-request';
import {FetchArtistsResponse} from '../dto/fetch-artists-response';


@Injectable({
  providedIn: 'root'
})
export class ArtistService {

  constructor(private http: HttpClient) {}

  create(artist: CreateArtistRequest): Observable<ArtistDTO> {
    return this.http.post<{ message: string; artist: ArtistDTO }>(
      `${environment.apiHost}/artist`,
      artist
    ).pipe(
      map(response => response.artist)
    );
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

  getArtist(artistId :string) : Observable<object> {
    return this.http.get<object>(`${environment.apiHost}/artist/${artistId}`)
  }

  delete(artistId: string) {
    return this.http.put(`${environment.apiHost}/artist/${artistId}`,{});
  }

}
