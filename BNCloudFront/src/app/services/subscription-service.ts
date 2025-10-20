import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {SubscriptionRequest} from '../dto/subscription-request';
import {Observable} from 'rxjs';
import {environment} from '../../env/enviroment';
import {Subscriptions} from '../components/subscriptions/subscriptions';
import {SubscriptionResponse} from '../dto/subscriptions-response';
import {UnsubscribeRequest} from '../dto/unsubscribe-request';


@Injectable({
  providedIn: 'root',

})
export class SubscriptionService {
  constructor(private http: HttpClient) {}

  subscribe(subscribeRequest : SubscriptionRequest): Observable<void> {
    return this.http.post<void>(`${environment.apiHost}/subscription`, subscribeRequest);
  }

  getUserSubscriptions(email: string): Observable<SubscriptionResponse[]> {
    return this.http.get<SubscriptionResponse[]>(`${environment.apiHost}/subscription/${email}`);
  }

  unsubscribe(unsubscribeRequest : UnsubscribeRequest): Observable<void> {
    return this.http.put<void>(`${environment.apiHost}/subscription`,unsubscribeRequest);
  }
}
