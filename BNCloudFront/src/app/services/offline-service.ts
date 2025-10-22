import {Injectable} from '@angular/core';
import {IDBPDatabase, openDB} from 'idb';

@Injectable({
  providedIn: 'root'
})
export class OfflineService {
  private dbPromise: Promise<IDBPDatabase>;

  constructor() {
    this.dbPromise = this.initDB();
  }

  private async initDB(): Promise<IDBPDatabase> {
    return openDB('OfflineSongsDB', 1, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('songs')) {
          db.createObjectStore('songs');
        }
      }
    });
  }

  async saveSongBlob(songId: string, blob: Blob): Promise<void> {
    const db = await this.dbPromise;
    const blobToStore = new Blob([blob], { type: blob.type || 'audio/mpeg' }); // ensure type
    await db.put('songs', blobToStore, songId);
  }

  async getSongBlob(songId: string): Promise<Blob | undefined> {
    const db = await this.dbPromise;
    const blob = await db.get('songs', songId);
    if (blob) {
      // Restore proper type
      return new Blob([blob], {type: blob.type || 'audio/mpeg'});
    }
    return undefined;
  }

  async deleteSong(songId: string): Promise<void> {
    const db = await this.dbPromise;
    await db.delete('songs', songId);
  }

  async clearAll(): Promise<void> {
    const db = await this.dbPromise;
    await db.clear('songs');
  }

  async listAllSongs(): Promise<string[]> {
    const db = await this.dbPromise;
    return await db.getAllKeys('songs') as string[];
  }
}
