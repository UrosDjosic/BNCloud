export interface SearchResult {
  id: string;
  type: 'song' | 'album' | 'artist' | 'genre';
  name: string;
}
