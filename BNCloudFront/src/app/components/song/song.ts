import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {SongService} from '../../services/song-service';
import {jwtDecode} from 'jwt-decode';
import {JwtClaims} from '../../models/jwt-claims';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-song',
  templateUrl: './song.html',
  styleUrl: './song.css',
  standalone: false
})
export class Song implements OnInit {

  songId?: string;
  song?: any;
  user?: any;

  // ⭐ rating logic
  stars = [1, 2, 3, 4, 5];
  currentRating = 0;
  hoverRating = 0;
  avgRating = 0;

  constructor(private route: ActivatedRoute, private router: Router, private ss: SongService, private snackbar: MatSnackBar) {}

  ngOnInit() {
    const token = localStorage.getItem('idToken');
    if (token) {
      const claims = jwtDecode<JwtClaims>(token);
      this.user = claims.sub;
    }
    this.route.paramMap.subscribe(params => {
      this.songId = params.get('songId') || undefined;
      if (this.songId) {
        this.loadSong(this.songId);
      }
    });
  }

  loadSong(id: string) {
    this.ss.getSong(id).subscribe(async (res: any) => {
      console.log(res);

      const audioKey = res.audioKey;

      // Step 1: Load basic metadata
      this.song = {
        name: res.name,
        ratings: res.ratings,
        genres: res.genres,
        id: id,
        creationTime: res.creationTime,
        modificationTime: res.modificationTime,
        artists: res.artists,
        transcript : res.transcript,
        fileName: audioKey.split('/').at(-1), // safely get filename
        audio: null,  // placeholder
        image: null   // placeholder
      };

      //load ratings
      if (this.user) {
        for (const rating of this.song.ratings) {
          if (rating.user === this.user) {
            this.currentRating = rating.stars;
            break;
          }
        }
        let sum = 0;
        let total = 0;
        for (const stars of this.song.ratings) {
          sum += Number(stars.stars);
          total++;
        }
        this.avgRating = sum/total;
      }

      try {
        const [audioBlob, imageBlob] = await Promise.all([
          this.downloadFromS3(res.audioUrl),
          this.downloadFromS3(res.imageUrl)
        ]);

        this.song.audio = URL.createObjectURL(audioBlob);
        this.song.image = URL.createObjectURL(imageBlob);

        console.log('Audio and image loaded', this.song);
      } catch (err) {
        console.error('Error downloading media from S3', err);
      }
    });
  }

  async downloadFromS3(presignedUrl: string): Promise<Blob> {
    return new Promise<Blob>((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.open('GET', presignedUrl, true);
      xhr.responseType = 'blob'; // ensures we get a Blob

      // Optional progress listener
      xhr.onprogress = (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded / event.total) * 100);
          console.log(`Download progress: ${percent}%`);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          console.log('Download succeeded:', xhr.status);
          resolve(xhr.response); // this is the Blob
        } else {
          console.error('Download failed:', xhr.status, xhr.responseText);
          reject(new Error(`S3 download failed with status ${xhr.status}`));
        }
      };

      xhr.onerror = () => {
        console.error('Network error during S3 download');
        reject(new Error('Network error during S3 download'));
      };

      xhr.send(); // no body for GET
    });
  }

  subscribeSong() {
    // Placeholder
    // this.userService.subscribeSong(this.songId).subscribe(...)
    console.log('Subscribed to song');
  }

  addToUserList() {
    // Placeholder
    console.log('Added to user list');
  }

  downloadSong() {
    // Placeholder
    console.log('Downloading song file');
  }

  setRating(rating: number) {
    this.currentRating = rating;
    console.log(`User rated this song: ${rating} stars`);

    if (this.user) {
      const request = {
        song: this.songId,
        user: this.user,
        stars: rating.toString()
      };

      this.ss.rateSong(request).subscribe({
        next: () => {
          window.location.reload();
        },
        error: (err: Error) => {
          console.error('Error rating song:', err);
          this.snackbar.open('Failed to rate the song.', 'Close', { duration: 3000 });
        }
      });
    }
  }

  editSong() {
    // Navigate to song edit page or open dialog
    this.router.navigate([`song/${this.songId}/edit`]);
  }

  deleteSong() {
    // this.songService.deleteSong(this.songId).subscribe(...)
  }

  navigateToArtist(artistId: string) {
    this.router.navigate([`/artist/${artistId}`]);
  }
}
