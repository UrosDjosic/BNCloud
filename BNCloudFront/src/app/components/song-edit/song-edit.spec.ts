import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SongEdit } from './song-edit';

describe('SongEdit', () => {
  let component: SongEdit;
  let fixture: ComponentFixture<SongEdit>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SongEdit]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SongEdit);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
