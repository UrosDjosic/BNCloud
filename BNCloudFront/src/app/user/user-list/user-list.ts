import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';

@Component({
  selector: 'app-user-list',
  templateUrl: './user-list.html',
  styleUrl: './user-list.css',
  standalone: false
})
export class UserList implements OnInit {

  userListId?: string;
  userSongs: S[] = [];

  constructor(private route: ActivatedRoute, private router: Router) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.userListId = params.get('userListId') || undefined;
      if (this.userListId) {
        this.loadUserList(this.userListId);
      }
    });
  }

  loadUserList(listId: string) {
    // this.userListService.getUserSongs(listId).subscribe(res => this.userSongs = res);

    // Dummy data depending on listId
    if (listId === '1') {
      this.userSongs = [
        { id: 's1', name: 'Rising Dawn', artists: [{ id: 'a1', name: 'The Midnight Beats' }] },
        { id: 's2', name: 'Fading Lights', artists: [{ id: 'a2', name: 'Luna Waves' }] }
      ];
    } else if (listId === '2') {
      this.userSongs = [
        { id: 's3', name: 'Electric Dreams', artists: [{ id: 'a3', name: 'Solar Echoes' }] },
        { id: 's4', name: 'Starlit Skies', artists: [{ id: 'a1', name: 'The Midnight Beats' }, { id: 'a2', name: 'Luna Waves' }] }
      ];
    } else {
      this.userSongs = [];
    }
  }

  navigateToSong(songId: string) {
    this.router.navigate([`/song/${songId}`]);
  }

  navigateToArtist(artistId: string) {
    this.router.navigate([`/author/${artistId}`]);
  }
}

interface S {
  id: string;
  name: string;
  artists: { id: string; name: string }[];
}
