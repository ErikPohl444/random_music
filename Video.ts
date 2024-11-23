import { DomSanitizer } from '@angular/platform-browser';

export class Video {
    id: number;
    title: string;
    videoCode: string;
    desc: string;

    constructor(id: number, title: string, videoCode: string, desc: string, videoURL: string, private _sanitizer: DomSanitizer){
          this.id = id;
          this.title = title;
          this.videoCode = videoCode;
          this.desc = desc;
          this.safeURL = this._sanitizer.bypassSecurityTrustResourceUrl(videoURL);
    }
}