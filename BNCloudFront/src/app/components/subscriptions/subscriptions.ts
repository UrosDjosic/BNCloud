import {Component, OnInit} from '@angular/core';
import {Router} from '@angular/router';
import {SubscriptionItem} from '../../models/subscription-item';
import {TokenService} from '../../services/token-service';
import {SubscriptionService} from '../../services/subscription-service';
import {SubscriptionResponse} from '../../dto/subscriptions-response';
import {MatSnackBar} from '@angular/material/snack-bar';
import {ConfirmDialogComponent} from '../confirm-dialog/confirm-dialog.component';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';

@Component({
  selector: 'app-subscriptions',
  templateUrl: './subscriptions.html',
  styleUrls: ['./subscriptions.css'],
  standalone: false
})

export class Subscriptions implements OnInit {

  subscriptions: SubscriptionResponse[] = [];
  email: string | null = null;

  constructor(private router: Router,
              private tokenService: TokenService,
              private subscriptionService: SubscriptionService,
              private snackBar: MatSnackBar,
              private dialog: MatDialog) {}

  ngOnInit() {
    this.email = this.tokenService.getUserEmailFromToken();
    if(!this.email) {
      return;
    }
    this.subscriptionService.getUserSubscriptions(this.email).subscribe(res =>
      this.subscriptions = res);
  }

  navigate(item: SubscriptionResponse) {
    switch (item.sub_type) {
      case 'artist':
        this.router.navigate(['/artist' , item.subject_id]);
        break;
    }
  }

  unsubscribeClick(item: SubscriptionResponse) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Confirm Unsubscribe',
        message: `Are you sure you want to unsubscribe from ${item.sub_type}?`
      },
      width: '350px'
    });

    dialogRef.afterClosed().subscribe((result: boolean | undefined) => {
      if (result === true) {
        this.subscriptionService.unsubscribe({
          subject_id: item.subject_id,
          user_email: this.email!,
          sub_type: item.sub_type
        }).subscribe(() => {
          this.snackBar.open(
            `Unsubscribed from ${item.sub_type} - ${item.subject_id}`,
            'Close',
            {duration: 2000}
          );
        });
      }
    });
  }
}
