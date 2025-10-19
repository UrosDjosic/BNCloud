import {ArtistDTO} from './artist';

export interface AlbumDTO {
  id: string,
  name: string,
  author: ArtistDTO,
  songs: any,
  genres: string[]
}
