import {SongDTO} from './song';

export interface Album {
  id: string,
  name: string,
  author: string,
  songs: SongDTO[]
}
