import {DiscoverResponse} from './discover-response';

export interface GenreDiscoverResponse {
  id: string,
  name: string,
  albums: DiscoverResponse[],
  artists: DiscoverResponse[],
}
