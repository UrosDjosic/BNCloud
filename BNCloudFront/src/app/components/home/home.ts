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
  genreFavorite : DiscoverResponse[] = [];
  genreTimeFavorite : DiscoverResponse[] = [];
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
          this.genreFavorite = res.genre_favorite
        this.genreTimeFavorite = res.genre_time_favorite
        console.log(this.genreTimeFavorite)
        console.log(this.genreFavorite)
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

  genreClicked(item: DiscoverResponse) {
      this.router.navigate(['discover', item.name]);
  }
}
