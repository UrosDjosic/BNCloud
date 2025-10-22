import { Component } from '@angular/core';
import {SongService} from '../../services/song-service';
import {AuthService} from '../../services/auth-service';
import {TokenService} from '../../services/token-service';
import {UserFeedResponse} from '../../dto/user-feed-response';
import {DiscoverResponse} from '../../dto/discover-response';
import {Router} from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.html',
  styleUrl: './home.css',
  standalone: false
})
export class Home {
  songs : DiscoverResponse[] = [];
  genreSongs : DiscoverResponse[] = [];
  artists : DiscoverResponse[] = [];
  constructor(private songService: SongService,
              private authService: AuthService,
              private tokenService: TokenService,
              private router: Router) {
  }

  ngOnInit(){
    if(this.authService.isLoggedIn()){
      this.songService.initFeed(this.tokenService.getUserIdFromToken()!).subscribe(res => {
        console.log(res);
          this.songs = res.songs
          this.artists = res.artists
          this.genreSongs = res.genre_songs
        console.log(this.genreSongs)
        console.log(this.artists)
        console.log(this.songs)

      })
    }
  }

  getTimeBucket(): 'Morning' | 'Afternoon' | 'Evening' | 'Night' {
    const hour = new Date().getUTCHours();

    if (hour >= 6 && hour < 12) {
      return 'Morning';
    } else if (hour >= 12 && hour < 18) {
      return 'Afternoon';
    } else if (hour >= 18 && hour < 24) {
      return 'Evening';
    } else {
      return 'Night';
    }
  }

  songClicked(item: DiscoverResponse) {
      this.router.navigate(['song', item.id]);
  }
}
