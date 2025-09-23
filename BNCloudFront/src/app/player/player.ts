import {Component, ElementRef, Input, OnInit, ViewChild} from '@angular/core';
import {MatIconModule} from '@angular/material/icon';
import {MatSliderModule} from '@angular/material/slider';
import {MatIconButton} from '@angular/material/button';

@Component({
  selector: 'app-player',
  templateUrl: './player.html',
  styleUrl: './player.css',
  imports: [
    MatIconModule,
    MatSliderModule,
    MatIconButton
  ],
  standalone: true
})
export class Player implements OnInit {

  @Input() songId!: string; // used to fetch actual file in real implementation
  @ViewChild('audioPlayer') audioPlayer!: ElementRef<HTMLAudioElement>;

  isPlaying: boolean = false;
  currentTime: number = 0;
  duration: number = 0;

  constructor() {}

  ngOnInit(): void {}

  ngAfterViewInit() {
    // Load dummy audio for now (replace with backend URL)
    if (this.audioPlayer) {
      this.audioPlayer.nativeElement.src = ''; // placeholder or static mp3 path
      this.audioPlayer.nativeElement.load();

      this.audioPlayer.nativeElement.onloadedmetadata = () => {
        this.duration = this.audioPlayer.nativeElement.duration;
      };

      this.audioPlayer.nativeElement.ontimeupdate = () => {
        this.currentTime = this.audioPlayer.nativeElement.currentTime;
      };
    }
  }

  togglePlay() {
    if (!this.audioPlayer) return;
    const audio = this.audioPlayer.nativeElement;
    if (this.isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    this.isPlaying = !this.isPlaying;
  }

  formatTime(time: number): string {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  }

  onSeek(event: any) {
    if (!this.audioPlayer) return;
    this.audioPlayer.nativeElement.currentTime = event.value;
  }

  onVolumeChange(event: any) {
    if (!this.audioPlayer) return;
    this.audioPlayer.nativeElement.volume = event.value;
  }
}
