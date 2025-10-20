export interface SubscriptionRequest {
  subject_id: string;
  subject_name: string;
  user_email: string;
  sub_type: 'genre' | 'artist';
}
