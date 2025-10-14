import {Component, OnInit} from '@angular/core';
import {Router} from '@angular/router';
import {SubscriptionItem} from '../../models/subscription-item';

@Component({
  selector: 'app-subscriptions',
  templateUrl: './subscriptions.html',
  styleUrl: './subscriptions.css',
  standalone: false
})
export class Subscriptions implements OnInit {

  subscriptions: SubscriptionItem[] = [];

  constructor(private router: Router) {}

  ngOnInit() {
    // Example: fetch user subscriptions
    // this.subscriptionService.getUserSubscriptions().subscribe(res => this.subscriptions = res);

    // Dummy data
    this.subscriptions = [
      { id: 's1', type: 'song', name: 'Song One' },
      { id: 'a1', type: 'album', name: 'Album A' },
      { id: 'auth1', type: 'author', name: 'Author X' },
      { id: 'g1', type: 'genre', name: 'Jazz' },
      { id: 'g2', type: 'genre', name: 'Pop' }
    ];
  }

  navigate(item: SubscriptionItem) {
    switch (item.type) {
      case 'song':
        this.router.navigate([`/song/${item.id}`]);
        break;
      case 'album':
        this.router.navigate([`/album/${item.id}`]);
        break;
      case 'author':
        this.router.navigate([`/author/${item.id}`]);
        break;
      case 'genre':
        this.router.navigate(['/search'], { queryParams: { genre: item.name } });
        break;
    }
  }
}
