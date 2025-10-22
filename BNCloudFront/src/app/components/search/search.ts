import {Component, OnInit} from '@angular/core';
import {FormBuilder, Validators} from '@angular/forms';
import {SearchResult} from '../../models/search-result';
import {ActivatedRoute, Router} from '@angular/router';
import {SongService} from '../../services/song-service';

@Component({
  selector: 'app-search',
  templateUrl: './search.html',
  styleUrl: './search.css',
  standalone: false
})
export class Search implements OnInit {

  searchForm: any;
  results: any = [];

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private ss: SongService
  ) {}

  ngOnInit() {

    this.searchForm = this.fb.group({
      type: ['song', Validators.required],
      query: ['', Validators.required]
    });
  }

  onSearch() {
    if (this.searchForm.invalid) return;

    const { type, query } = this.searchForm.value;

    console.log(query)

    // Fetch results
    this.fetchResults((String(query)));
  }

  fetchResults(query: string) {
    this.ss.searchSong(query).subscribe({
      next: (res: any) => {
        this.results = res.result;
      },
      error: err => {
        console.log(err);
      }
    });
  }
}
