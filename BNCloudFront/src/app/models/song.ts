import {Artist} from './artist';
import {Album} from './album';

export interface SongDTO {
  id: string;
  fileName: string;
  fileType: string;
  size: string;
  createdAt: string;
  updatedAt: string;
  genre: string; //maybe change to enum later?
  authors: Artist[];
  albums: Album[];
  ratings?: number[]; // 1-3
}
