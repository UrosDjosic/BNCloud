import {ArtistDTO} from './artist';
import {AlbumDTO} from './album';

export interface SongDTO {
  id: string;
  fileName: string;
  fileType: string;
  size: string;
  createdAt: string;
  updatedAt: string;
  genres: string[]; //maybe change to enum later?
  authors: ArtistDTO[];
  ratings?: number[]; // 1-3
  image: string;
}
