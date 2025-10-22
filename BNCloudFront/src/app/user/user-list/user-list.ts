import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { SongService } from '../../services/song-service';
import { forkJoin, Observable, of } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import {UserlistService} from '../../services/userlist-service';
import { catchError } from 'rxjs';

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
    console.log(listId);
    this.getUserlist(listId).pipe(
      switchMap((res: any) => {
        this.userListName = res.name || 'Unnamed List';

        if (!res.songs || res.songs.length === 0) {
          return of([] as any[]); // explicitly type as any[]
        }

        const songObservables: Observable<any | null>[] = res.songs.map((songId: string) =>
          this.songService.getSong(songId).pipe(
            catchError(err => {
              console.warn(`Song ${songId} could not be loaded (maybe deleted)`, err);
              return of(null); // return null for missing song
            })
          )
        );

        return forkJoin(songObservables);
      })
    ).subscribe(
      (songs: (any | null)[]) => {
        // Filter out null entries
        this.userSongs = songs
          .filter((s): s is any => s !== null) // type guard
          .map(s => ({
            id: s.id,
            name: s.name,
            artists: s.artists || []
          }));
      },
      (err) => {
        console.error('Failed to load user list', err);
        this.userSongs = [];
      }
    );
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
