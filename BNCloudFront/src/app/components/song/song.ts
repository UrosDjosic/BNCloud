import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {SongService} from '../../services/song-service';
import {jwtDecode} from 'jwt-decode';
import {JwtClaims} from '../../models/jwt-claims';
import {MatSnackBar} from '@angular/material/snack-bar';
import {UserlistService} from '../../services/userlist-service';
import { MatDialog } from '@angular/material/dialog';
import {ConfirmDialogComponent} from '../confirm-dialog/confirm-dialog.component';
import {OfflineService} from '../../services/offline-service';
import {AuthService} from '../../services/auth-service';

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

  showUserListDropdown = false;
  userlistId?: string;
  usersLists?: any;

  petnesFeninga?: any

  role : string ='';

  constructor(private dialog: MatDialog, private route: ActivatedRoute, private router: Router,
              private ss: SongService, private us: UserlistService,
              private snackbar: MatSnackBar, private offlineSongs: OfflineService,
              private authService: AuthService,) {}

  ngOnInit() {
    const token = localStorage.getItem('idToken');
    if (token) {
      const claims = jwtDecode<JwtClaims>(token);
      this.user = claims.sub;
      if (this.user) {
        this.loadUsersLists();
      }
    }
    this.route.paramMap.subscribe(params => {
      this.songId = params.get('songId') || undefined;
      if (this.songId) {
        this.loadSong(this.songId);
      }
    });
    this.role = this.authService.getRole()
  }

  async loadSong(id: string) {

    //try to hit cached blob if downloaded (offline playback)
    const cachedBlob = await this.offlineSongs.getSongBlob(id);
    if (cachedBlob) {
      console.log(`Loaded song ${id} from IndexedDB`);
      console.log(cachedBlob);
      console.log(cachedBlob.type)
      this.song = {
        audio: URL.createObjectURL(cachedBlob)
      }
      return;
    }

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
        image: null,   // placeholder
        userRating : res.userRating,
        avgRating: res.avgRating,
        sumRatings: res.sumRatings,
        numRatings: res.numRatings,
      };

      //load ratings
      if (this.user) {
        this.currentRating = this.song.userRating;
        this.avgRating = Number(parseFloat(this.song.avgRating).toFixed(2));
      }

      try {
        const [audioBlob, imageBlob] = await Promise.all([
          this.downloadFromS3(res.audioUrl),
          this.downloadFromS3(res.imageUrl)
        ]);

        this.petnesFeninga = audioBlob;
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

  loadUsersLists() {
    this.us.getUsersUserlists(this.user).subscribe({
      next: (res: any) => {this.usersLists = res.usersLists; console.log(this.usersLists);},
      error: (err) => {console.log(err)}
    })
  }

  selectUserList() {
    this.showUserListDropdown = true;
  }

  onUserListSelected(selectedId: string) {
    this.userlistId = selectedId;
    this.showUserListDropdown = false;
    this.addToUserList();
  }

  addToUserList() {
    this.us.updateUserlist(this.userlistId!, this.songId!).subscribe({
      next: result => {this.snackbar.open("Added.", 'OK')},
      error: err => {this.snackbar.open("Failed to add.", ":(")}
    });
  }

  async cacheSongForOffline() {
    if (!this.songId || !this.song?.audio) return;
    await this.offlineSongs.saveSongBlob(this.songId, this.petnesFeninga);
    this.snackbar.open('Song saved for offline playback.', 'OK', { duration: 3000 });
  }

  async removeOfflineCopy() {
    if (!this.songId) return;
    await this.offlineSongs.deleteSong(this.songId);
    this.snackbar.open('Offline copy removed.', 'OK', { duration: 3000 });
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
          this.avgRating = parseFloat((
            (this.song.sumRatings + this.currentRating) /
            (this.song.numRatings + 1)
          ).toFixed(2));
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
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: { message: 'Are you sure you want to delete this song?' }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.ss.deleteSong(this.songId!).subscribe({
          next: () => {
            this.snackbar.open('Song deleted successfully.', 'OK', { duration: 3000 });
            this.router.navigate(['/songs']);
          },
          error: () => {
            this.snackbar.open('Failed to delete song.', 'Close', { duration: 3000 });
          }
        });
      }
    });
  }

  navigateToArtist(artistId: string) {
    this.router.navigate([`/artist/${artistId}`]);
  }
}
