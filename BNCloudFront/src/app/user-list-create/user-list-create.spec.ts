import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserListCreate } from './user-list-create';

describe('UserListCreate', () => {
  let component: UserListCreate;
  let fixture: ComponentFixture<UserListCreate>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserListCreate]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserListCreate);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
