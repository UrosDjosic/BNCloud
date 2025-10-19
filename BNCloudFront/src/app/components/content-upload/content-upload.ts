import {Component, OnInit} from '@angular/core';
import {MatSnackBar} from '@angular/material/snack-bar';
import {ArtistDTO} from '../../models/artist';
import {ArtistService} from '../../services/artist-service';
import {SongService} from '../../services/song-service';
import {DynamoSongResponse} from '../../dto/dynamo-song-response';
import {AlbumService} from '../../services/album-service';
import {GenreResponse} from '../../dto/genre-response';
import {GenreService} from '../../services/genre-service';
import {DiscoverResponse} from '../../dto/discover-response';

@Component({
  selector: 'app-content-upload',
  templateUrl: './content-upload.html',
  styleUrl: './content-upload.css',
  standalone: false
})
export class ContentUpload implements OnInit {
  uploads: SongUpload[] = [{ genres: [], artists: [], genresText: '', image: null, file: null }];
  artists: DiscoverResponse[] = [];
  lastKey: string | null = null;
  availableGenres: GenreResponse[] = [];
  testMode: boolean = false;
  totalProgress: number = 0;
  isUploading: boolean = false;
  private uploadProgressMap = new Map<string, number>();

  constructor(private snackBar: MatSnackBar, private artistService: ArtistService, private ss: SongService, private as: AlbumService,
              private genreService: GenreService) {}

  ngOnInit(): void {
    this.loadArtists();
    this.fetchGenres();
  }
  private fetchGenres() {
    this.genreService.getAll().subscribe(res => {
      this.availableGenres = res.genres;
      console.log(res);
    })
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
      ? song.genresText
        .split(',')
        .map(g => g.trim())
        .filter(g => g !== '')
        .map(g => ({ id: '', name: g }))
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

  async submit(): Promise<void> {
    this.isUploading = true;
    this.totalProgress = 0;
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
        next: async (response: DynamoSongResponse) => {
          await Promise.all([
            this.uploadToS3(upload.file!, response.audioUploadUrl),
            this.uploadToS3(upload.image!, response.imageUploadUrl)
          ]);
          this.snackBar.open('Song uploaded successfully', 'Close', { duration: 3000 });
          this.isUploading = false;
          this.uploadProgressMap.clear();
          this.totalProgress = 100;

          setTimeout(() => {
            this.totalProgress = 0;
          }, 1500);
        },
        error: (err) => {
          console.error(err);
          this.snackBar.open('Failed to upload song', 'Close', { duration: 3000 });
          this.isUploading = false;
          this.uploadProgressMap.clear();
          this.totalProgress = 100;

          setTimeout(() => {
            this.totalProgress = 0;
          }, 1500);
        }
      });
    } else {
      try {
        // 1️⃣ Upload all songs metadata + files in parallel
        const uploadResults = await Promise.all(
          this.uploads.map(async (upload) => {
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

            return new Promise<{ id: string; name: string }>((resolve, reject) => {
              this.ss.uploadSongMetadata(song).subscribe({
                next: async (response: DynamoSongResponse) => {
                  try {
                    await Promise.all([
                      this.uploadToS3(upload.file!, response.audioUploadUrl),
                      this.uploadToS3(upload.image!, response.imageUploadUrl),
                    ]);
                    resolve({ id: response.songId, name: song.name! });
                  } catch (uploadErr) {
                    reject(uploadErr);
                  }
                },
                error: (err) => reject(err),
              });
            });
          })
        );


        // 2️⃣ Aggregate genres & artists across all uploads
        const allGenres = [
          ...new Set(this.uploads.flatMap((u) => u.genres))
        ];
        const allArtists = [
          ...new Set(this.uploads.flatMap((u) => u.artists))
        ];

        // 3️⃣ Create album object
        const album = {
          name: this.uploads[0].name || 'Untitled Album',
          genres: allGenres,
          artists: allArtists,
          songs: uploadResults, // IDs returned from uploadSongMetadata
        };

        // 4️⃣ Upload album
        this.as.uploadAlbum(album).subscribe({
          next: (response: string) => {
            console.log('Album created:', response);
            this.snackBar.open('Album uploaded successfully', 'Close', { duration: 3000 });
          },
          error: (err) => {
            console.error('Album creation failed', err);
            this.snackBar.open('Failed to create album', 'Close', { duration: 3000 });
          }
        });
      } catch (err) {
        console.error('One or more song uploads failed:', err);
        this.snackBar.open('Some songs failed to upload', 'Close', { duration: 3000 });
      }
    }
  }

  updateProgress(percent: number): void {
    this.totalProgress = percent;
  }

  setFileProgress(fileName: string, percent: number) {
    // Sačuvaj progres za taj fajl
    this.uploadProgressMap.set(fileName, percent);

    // Izračunaj prosečan progres svih aktivnih uploadova
    const values = Array.from(this.uploadProgressMap.values());
    const avgProgress = Math.round(values.reduce((a, b) => a + b, 0) / values.length);

    this.totalProgress = avgProgress;
  }

  async uploadToS3(file: File, presignedUrl: string): Promise<void> {

    if (this.testMode) {
      console.log(`Simulating upload for ${file.name}...`);
      return new Promise<void>((resolve) => {
        let progress = 0;
        const interval = setInterval(() => {
          progress += 10 + Math.random() * 20;
          if (progress > 100) progress = 100;

          this.setFileProgress(file.name, progress);

          if (progress >= 100) {
            clearInterval(interval);
            console.log(`Simulated upload complete for ${file.name}`);
            resolve();
          }
        }, 200);
      });
    }

    // stvarni upload ako nije test režim
    return new Promise<void>((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open('PUT', presignedUrl, true);

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded / event.total) * 100);
          this.setFileProgress(file.name, percent);
          console.log(`Upload progress: ${percent}%`);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve();
        } else {
          reject(new Error(`S3 upload failed: ${xhr.status}`));
        }
      };

      xhr.onerror = () => {
        console.error('Network error during S3 upload');
        reject(new Error('Network error during S3 upload'));
      };

      xhr.onerror = () => reject(new Error('Network error during S3 upload'));
      xhr.send(file);
    });
  }


  toggleGenre(song: any, genre: any): void {
    if (!song.genres) {
      song.genres = [];
    }

    const index = song.genres.findIndex((g: any) => g.id === genre.id);
    if (index > -1) {
      // Remove
      song.genres.splice(index, 1);
    } else {
      // Add
      song.genres.push({ id: genre.id, name: genre.name });
    }
  }


  isGenreSelected(song: any, genre: any): boolean {
    return song.genres?.some((g: any) => g.id === genre.id);
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
  genres: GenreResponse[];
  genresText?: string;
  image: File | null;
  imagePreview?: string;
  artists: DiscoverResponse[]; // will store selected artist IDs
}
