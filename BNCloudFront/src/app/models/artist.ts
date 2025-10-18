import {GenreResponse} from '../dto/genre-response';

export interface ArtistDTO {
  id: string;
  name: string;
  biography: string;
  genres: GenreResponse[];
}
