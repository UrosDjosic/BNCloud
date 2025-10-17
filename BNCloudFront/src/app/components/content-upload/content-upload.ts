import {Component, OnInit} from '@angular/core';
import {MatSnackBar} from '@angular/material/snack-bar';
import {ArtistDTO} from '../../models/artist';
import {ArtistService} from '../../services/artist-service';
import {SongService} from '../../services/song-service';
import {DynamoSongResponse} from '../../dto/dynamo-song-response';
import {finalize} from 'rxjs';
import {HttpClient, HttpHeaders} from '@angular/common/http';

@Component({
  selector: 'app-content-upload',
  templateUrl: './content-upload.html',
  styleUrl: './content-upload.css',
  standalone: false
})
export class ContentUpload implements OnInit {
  uploads: SongUpload[] = [{ genres: [], artists: [], genresText: '', image: null, file: null }];
  artists: ArtistDTO[] = [];
  lastKey: string | null = null;

  constructor(private snackBar: MatSnackBar, private artistService: ArtistService, private ss: SongService, private http: HttpClient) {}

  ngOnInit(): void {
    this.loadArtists();
  }

  /** Fetch all artists to populate dropdown */
  loadArtists(lastKey: string = '', pageSize: number = 50): void {
    this.artistService.getArtists(lastKey, pageSize).subscribe({
      next: (response) => {
        // Append current batch of artists
        this.artists = [...this.artists, ...response.items];

        // If there’s another page, fetch it recursively
        if (response.lastKey) {
          this.loadArtists(response.lastKey, pageSize);
        } else {
          console.log(`Loaded all ${this.artists.length} artists`);
        }
      },
      error: (err) => {
        console.error('Failed to load artists', err);
        this.snackBar.open('Failed to load artists', 'Close', { duration: 3000 });
      },
    });
  }

  /** Handle audio file selection */
  onFileSelected(event: any, index: number): void {
    const file: File = event.target.files[0];
    if (file && file.size < 10*1024*1024) {
      const song = this.uploads[index];
      song.file = file;
      song.fileName = file.name;
      song.fileType = file.type;
      song.fileSize = file.size;
      song.creationTime = new Date();
      song.modificationTime = file.lastModified ? new Date(file.lastModified) : new Date();
    }
    else {
      this.snackBar.open("You must upload a file smaller than 10MB!")
    }
  }

  /** Handle cover image upload */
  onImageSelected(event: any, index: number): void {
    const file: File = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        this.uploads[index].imagePreview = reader.result as string;
      };
      reader.readAsDataURL(file);
      this.uploads[index].image = file;

      console.log(this.uploads[index]);
    }
  }

  /** Convert comma-separated text to array */
  updateGenres(index: number): void {
    const song = this.uploads[index];
    song.genres = song.genresText
      ? song.genresText.split(',').map((g) => g.trim()).filter((g) => g)
      : [];
  }

  /** Add another song input block */
  addAnotherSong(): void {
    this.uploads.push({ genres: [], artists: [], genresText: '', image: null, file: null});
  }

  /** Remove one song entry */
  removeSong(index: number): void {
    this.uploads.splice(index, 1);
  }

  submit(): void {
    if (this.uploads.length === 1) {
      const upload = this.uploads[0];

      const song = {
        name: upload.name,
        genres: upload.genres,
        artists: upload.artists,
        creationTime: upload.creationTime,
        modificationTime: upload.modificationTime,
        ratings: [],
        audioFileName: upload.fileName,
        imageFileName: upload.image!.name,
      };

      this.ss.uploadSongMetadata(song).subscribe({
        next: (response: DynamoSongResponse) => {
          console.log('Presigned URLs received:', response);

          // Step 2: upload audio file
          const audioHeaders = new HttpHeaders({});

          this.http.put(response.audioUploadUrl, upload.file, { headers: audioHeaders, responseType: 'text' })
            .pipe(finalize(() => console.log('Audio upload attempt finished')))
            .subscribe({
              next: () => {
                // Step 3: upload image
                const imageHeaders = new HttpHeaders({});

                this.http.put(response.imageUploadUrl, upload.image, { headers: imageHeaders, responseType: 'text' })
                  .subscribe({
                    next: () => {
                      this.snackBar.open('Upload successful!', 'Close', { duration: 3000 });
                    },
                    error: err => {
                      console.error('Image upload failed', err);
                      this.snackBar.open('Image upload failed', 'Close', { duration: 3000 });
                    }
                  });
              },
              error: err => {
                console.error('Audio upload failed', err);
                this.snackBar.open('Audio upload failed', 'Close', { duration: 3000 });
              }
            });
        },
        error: err => {
          console.error('Failed to create song entry', err);
          this.snackBar.open('Failed to create song entry', 'Close', { duration: 3000 });
        }
      });
    }
  }

}

interface SongUpload {
  file: File | null;
  fileName?: string;
  fileType?: string;
  fileSize?: number;
  creationTime?: Date;
  modificationTime?: Date;
  name?: string;
  genres: string[];
  genresText?: string;
  image: File | null;
  imagePreview?: string;
  artists: string[]; // will store selected artist IDs
}
