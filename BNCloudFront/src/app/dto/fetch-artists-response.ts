import {ArtistDTO} from '../models/artist';

export interface FetchArtistsResponse {
  items: ArtistDTO[];
  lastKey: string;
}
