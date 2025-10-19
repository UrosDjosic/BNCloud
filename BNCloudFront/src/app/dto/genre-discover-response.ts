import {AlbumDTO} from '../models/album';
import {ArtistDTO} from '../models/artist';
import {DiscoverResponse} from './discover-response';

export interface GenreDiscoverResponse {
  id: string,
  name: string,
  albums: DiscoverResponse[],
  artists: DiscoverResponse[],
}
