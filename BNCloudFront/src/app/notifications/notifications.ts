import {Component, OnInit} from '@angular/core';
import {Notification} from '../models/notification';

@Component({
  selector: 'app-notifications',
  templateUrl: './notifications.html',
  styleUrl: './notifications.css',
  standalone: false
})
export class Notifications implements OnInit {

  notifications: Notification[] = [];

  constructor(
    // private notificationService: NotificationService
  ) {}

  ngOnInit() {
    this.loadNotifications();
  }

  loadNotifications() {
    // Placeholder for backend loading
    // this.notificationService.getUserNotifications().subscribe(res => this.notifications = res);

    // Dummy data
    this.notifications = [
      { id: '1', message: 'New album released!', read: false },
      { id: '2', message: 'Your subscription is renewed.', read: true },
      { id: '3', message: 'New song added to your playlist.', read: false }
    ];
  }

  markAsRead(notification: Notification) {
    if (!notification.read) {
      notification.read = true;
      this.sendReadNotification(notification);
    }
  }

  sendReadNotification(notification: Notification) {
    // Placeholder for backend update
    // this.notificationService.markAsRead(notification.id).subscribe();
    console.log(`Marked notification ${notification.id} as read`);
  }
}
