import { Component } from '@angular/core';
import {FormBuilder} from '@angular/forms';
import {MatSnackBar} from '@angular/material/snack-bar';
import {OnInit} from '@angular/core';
import {ArtistDTO} from '../../models/artist';
import {Validators} from '@angular/forms';
import {ArtistService} from '../../services/artist-service';

@Component({
  selector: 'app-artist-crud',
  templateUrl: './artist-crud.html',
  styleUrl: './artist-crud.css',
  standalone: false
})
export class ArtistCrud implements OnInit {

  isCreating: boolean = false; // toggle between create and update/delete
  displayedArtists: ArtistDTO[] = [];
  lastKey : string = '';
  pageSize = 3;
  hasMore = true;
  loading = false;
  selectedArtist?: ArtistDTO;

  createForm: any;
  updateForm: any;

  constructor(
    private fb: FormBuilder,
    private snackBar: MatSnackBar,
    private artistService: ArtistService,
  ) {}

  ngOnInit() {
    // Forms
    this.createForm = this.fb.group({
      name: ['', Validators.required],
      biography: ['', Validators.required],
      genres: ['', Validators.required]
    });

    this.updateForm = this.fb.group({
      name: ['', Validators.required],
      biography: ['', Validators.required],
      genres: ['', Validators.required]
    });

    this.fetchArtists(); //async, be careful
  }

  toggleView() {
    this.isCreating = !this.isCreating;
    this.selectedArtist = undefined; // reset selection
  }

  // Fodder methods
  fetchArtists() {
    if (!this.hasMore || this.loading) return;
    this.loading = true;
    this.artistService.getArtists(this.lastKey, this.pageSize).subscribe(res => {
      this.displayedArtists.push(...res.items);
      this.lastKey = res.lastKey;
      this.hasMore = !!res.lastKey;
      this.loading = false;
    });
  }

  selectArtist(artist: ArtistDTO) {
    this.selectedArtist = artist;
    this.updateForm.patchValue({
      name: artist.name,
      biography: artist.biography,
      genres: artist.genres.join(', ')
    });
  }

  createArtist() {
    if (this.createForm.invalid) {
      this.snackBar.open('Please fill all fields', 'Close', { duration: 3000 });
      return;
    }

    const formValue = this.createForm.value;


    this.artistService.create({
      name: formValue.name,
      genres: formValue.genres.split(',').map((g: string) => g.trim()),
      biography : formValue.biography
    }).subscribe({
      next: () => {
        this.snackBar.open('Artist created successfully!', 'Close', { duration: 3000 });
        this.createForm.reset();
      },
      error: (err) => {
        console.error(err);
        this.snackBar.open('Failed to create artist', 'Close', { duration: 3000 });
      }
    })

    this.createForm.reset();
    this.fetchArtists(); // refresh list
    this.toggleView(); // go back to update/delete view
  }

  updateArtist() {
    if (!this.selectedArtist || this.updateForm.invalid) return;

    const formValue = this.updateForm.value;
    this.artistService.updateArtist({
      id : this.selectedArtist.id,
      name: formValue.name,
      genres: formValue.genres.split(',').map((g: string) => g.trim()),
      biography : formValue.biography
    }).subscribe({
      next: (res : ArtistDTO) => {
        this.snackBar.open(`Succesfully updated "${formValue.name}" ✏️!`, 'Close', { duration: 3000 });
        const index = this.displayedArtists.findIndex(a => a.id === res.id);
        console.log(index);
        console.log(res)
        if (index !== -1) {
          this.displayedArtists[index] = res;
        }
        this.selectedArtist = undefined;
      }
    })
  }

  deleteArtist() {
    if (!this.selectedArtist) return;

    // this.artistService.delete(this.selectedArtist.id).subscribe({ ... });
    this.snackBar.open(`Pretend we deleted artist "${this.selectedArtist.name}" ❌`, 'Close', { duration: 3000 });
    this.selectedArtist = undefined;
    this.fetchArtists();
  }
  onScroll(event: any) {
    const element = event.target;
    if (element.scrollHeight - element.scrollTop === element.clientHeight) {
      this.fetchArtists();
  }

  }
}
