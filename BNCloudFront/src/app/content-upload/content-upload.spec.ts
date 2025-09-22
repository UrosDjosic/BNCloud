import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContentUpload } from './content-upload';

describe('ContentUpload', () => {
  let component: ContentUpload;
  let fixture: ComponentFixture<ContentUpload>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContentUpload]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ContentUpload);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
