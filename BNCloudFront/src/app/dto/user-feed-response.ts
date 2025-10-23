import {DiscoverResponse} from './discover-response';

export interface UserFeedResponse {
  id: string;
  artists: DiscoverResponse[];
  songs: DiscoverResponse[];
  genre_favorite: DiscoverResponse[];
  genre_time_favorite: DiscoverResponse[];
}
