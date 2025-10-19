import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {SongService} from '../../services/song-service';

@Component({
  selector: 'app-song',
  templateUrl: './song.html',
  styleUrl: './song.css',
  standalone: false
})
export class Song implements OnInit {

  songId?: string;
  song?: any;

  constructor(private route: ActivatedRoute, private router: Router, private ss: SongService) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.songId = params.get('songId') || undefined;
      if (this.songId) {
        this.loadSong(this.songId);
      }
    });
  }

  async loadSong(id: string) {
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
        fileName: audioKey.split('/').at(-1), // safely get filename
        audio: null,  // placeholder
        image: null   // placeholder
      };

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

  rateSong(stars: number) {
    if (this.song) this.song.ratings?.push(stars);
    // this.songService.rateSong(this.songId, stars).subscribe(...)
  }

  editSong() {
    // Navigate to song edit page or open dialog
    this.router.navigate(['content-rud']);
  }

  deleteSong() {
    // this.songService.deleteSong(this.songId).subscribe(...)
  }

  navigateToArtist(artistId: string) {
    this.router.navigate([`/artist/${artistId}`]);
  }
}
