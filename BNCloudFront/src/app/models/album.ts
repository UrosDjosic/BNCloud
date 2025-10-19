import {ArtistDTO} from './artist';
import {AlbumSongDTO} from './album-song';

export interface AlbumDTO {
  id: string,
  name: string,
  author: ArtistDTO,
  songs: AlbumSongDTO[],
  genres: string[]
}
