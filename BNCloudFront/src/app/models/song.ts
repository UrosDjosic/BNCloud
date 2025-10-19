import { ArtistDTO } from './artist';

export interface SongDTO {
  id: string;
  name: string;
  artists?: string[];       // lista ID-eva autora
  audioKey?: string;        // ključ fajla na S3
  audioUrl?: string;        // URL fajla za preuzimanje
  imageUrl?: string;        // URL slike za preuzimanje
  fileName?: string;        // ime fajla, generisano iz audioKey
  audio?: string | null;    // ObjectURL nakon download-a
  image?: string | null;    // ObjectURL nakon download-a
  ratings?: number[];
  genres?: string[];
  creationTime?: string;    // ISO string ili Date
  modificationTime?: string;
}
