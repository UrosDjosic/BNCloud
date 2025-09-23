export interface SubscriptionItem {
  id: string;
  type: 'song' | 'album' | 'author' | 'genre';
  name: string;
}
