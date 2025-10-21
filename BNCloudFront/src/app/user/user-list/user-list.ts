import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { SongService } from '../../services/song-service';
import { forkJoin, Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import {UserlistService} from '../../services/userlist-service';

@Component({
  selector: 'app-user-list',
  templateUrl: './user-list.html',
  styleUrls: ['./user-list.css'],
  standalone: false
})
export class UserList implements OnInit {

  userListId?: string;
  userListName: string = '';
  userSongs: Song[] = [];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private songService: SongService,
    private us: UserlistService
  ) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.userListId = params.get('userListId') || undefined;
      if (this.userListId) {
        this.loadUserList(this.userListId);
      }
    });
  }

  loadUserList(listId: string) {
    this.getUserlist(listId).pipe(
      switchMap((res: any) => {
        this.userListName = res.name || 'Unnamed List';
        const songObservables: Observable<any>[] = res.songs.map((songId: string) =>
          this.songService.getSong(songId)
        );
        return forkJoin(songObservables);
      })
    ).subscribe({
      next: (songs: any[]) => {
        this.userSongs = songs.map(s => ({
          id: s.id,
          name: s.name,
          artists: s.artists || []
        }));
      },
      error: err => {
        console.error('Failed to load user list or songs', err);
        this.userSongs = [];
      }
    });
  }

  getUserlist(userlistId: string): Observable<object> {
    return this.us.getUserlist(userlistId);
  }

  navigateToSong(songId: string) {
    this.router.navigate(['/song', songId]);
  }

  navigateToArtist(artistId: string) {
    this.router.navigate(['/artist', artistId]);
  }
}

interface Song {
  id: string;
  name: string;
  artists: { id: string; name: string }[];
}
