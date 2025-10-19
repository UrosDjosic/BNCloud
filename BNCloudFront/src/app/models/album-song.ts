export interface AlbumSongDTO {
  id: string;
  name: string;
  artists?: string[];   // samo ID-evi autora
  fileName?: string;    // ime fajla za prikaz
}
