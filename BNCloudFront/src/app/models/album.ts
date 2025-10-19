import {ArtistDTO} from './artist';
import {AlbumSongDTO} from './album-song';
import {GenreResponse} from '../dto/genre-response';

export interface AlbumDTO {
  id: string,
  name: string,
  author: ArtistDTO,
  songs: AlbumSongDTO[],
  genres: GenreResponse[]
}
