import {GenreResponse} from './genre-response';

export interface CreateArtistRequest {
  name: string;
  biography: string;
  genres: GenreResponse[];
}
